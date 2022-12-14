#-*- coding:utf-8 -*-
import random
import time
import math

from ..kakul.character import Character
from ..kakul.party import Party
from ..kakul.user import User
from ..kakul.utils import printl
from ..kakul.loainfo import GetApproxStrength

from dataclasses import dataclass, field




@dataclass
class UserInfo:
    countAssigned: int = 0
    countEssential: int = 0
    countNonessential: int = 0
    charEssential: list = field(default_factory=list)
    charNonessential: list = field(default_factory=list)
    def __str__(self):
        return "%d/%d(%d) %s"%(self.countAssigned, self.countEssential, self.countNonessential, self.charEssential)

@dataclass
class Cube:
    score: int = 0.0
    parties: list = field(default_factory=list)
    groups: list = field(default_factory=list)
    charSup: dict = field(default_factory=dict)

@dataclass
class Group:
    count: int = 0
    users: list = field(default_factory=list)
    sups: list = field(default_factory=list)

class Manager:
    def __init__(self):
        self.characters = [] # list of Character
        self.users = [] # list of users

        self.leftovers = [] # list of characters
        self.parties = []
        self.groups = []
    
    def Fix(self):
        set = []
        dell = []
        for char in self.characters:
            if char.name in set:
                dell.append(char)
            else:
                set.append(char.name)
        for char in dell:
            self.characters.remove(char)
        set = []
        dell = []
        for user in self.users:
            if user.name in set:
                dell.append(user)
            else:
                set.append(user.name)
        for user in dell:
            self.users.remove(user)

    def Validate(self):
        assignedList = []
        self.leftovers = []
        for party in self.parties:
            for char in party.members:
                if char in assignedList:
                    party.members.remove(char)
                assignedList.append(char)
        for char in self.characters:
            if char not in assignedList:
                self.leftovers.append(char)
        self.characters.sort(key=lambda x: x.power, reverse=True)

    def AddCharacterToParty(self, character, partyIndex, strict = False):
        if character not in self.characters:
            return False
        if character not in self.leftovers:
            tag = False
            for party in self.parties:
                if character in party.members:
                    party.members.remove(character)
                    tag = True
                    break
            if not tag:
                return False
        res = self.parties[partyIndex].AddCharacter(character, strict)
        self.Validate()
        return res
        
    def RemoveCharacterFromParty(self, character):
        for i in range(len(self.parties)):
            if character in self.parties[i].members:
                res = self.parties[i].RemoveCharacter(character)
                self.Validate()                
                return True
        return False
    
    def ReplaceCharacters(self, char1, char2):
        char1pos, char2pos = -1, -1
        for partyInd in range(len(self.parties)):
            if char1 in self.parties[partyInd].members:
                char1pos = partyInd
            if char2 in self.parties[partyInd].members:
                char2pos = partyInd
        if char1pos == -1 and char2pos == -1:
            return False
        elif char1pos == -1:
            self.parties[char2pos].RemoveCharacter(char2)
            res = self.parties[char2pos].AddCharacter(char1, strict=False)
            if res:
                self.Validate()
                return True
            else:
                self.parties[char2pos].AddCharacter(char2, strict=False)
                return False
        elif char2pos == -1:
            self.parties[char1pos].RemoveCharacter(char1)
            res = self.parties[char1pos].AddCharacter(char2, strict=False)
            if res:
                self.Validate()
                return True
            else:
                self.parties[char1pos].AddCharacter(char1, strict=False)
                return False
        else:
            self.parties[char1pos].RemoveCharacter(char1)
            self.parties[char2pos].RemoveCharacter(char2)
            res1 = self.parties[char1pos].AddCharacter(char2, strict=False)
            res2 = self.parties[char2pos].AddCharacter(char1, strict=False)
            if res1 and res2:
                self.Validate()
                return True
            else:
                self.parties[char1pos].AddCharacter(char1, strict=False)
                self.parties[char2pos].AddCharacter(char2, strict=False)
                return False
                
    def AddEmptyParty(self):
        self.parties.append(Party(len(self.parties)))
        return True

    def AddPartyRaw(self, names, clear):
        self.parties.append(Party(len(self.parties)))
        self.parties[-1].cleared = clear
        for name in names:
            v = self.GetCharacterByName(name)
            self.parties[-1].AddCharacter(self.GetCharacterByName(name), strict=False)

    def AddCharacter(self, character):
        if character in self.characters:
            printl(f"Character {character} already in manager")
            return False
        self.characters.append(character)
        return True

    def AddCharacterRaw(self, owner, name, role, power, essential, active, isSupportMode):
        self.characters.append(Character(owner, name, role, power, essential, active, isSupportMode))
    
    def RemoveCharacterbyName(self, name):
        for c in self.characters:
            if c.name == name:
                return self.RemoveCharacter(c)
        return False

    def RemoveCharacter(self, character):
        if character not in self.characters:
            printl(f"Character {character} not in manager")
            return False
        self.characters.remove(character)
        return True
    
    def EditCharacter(self, name, is_essential=None, is_support=None):
        for character in self.characters:
            if character.name == name:
                if is_essential != None:
                    character.essential = is_essential
                if is_support != None:
                    character.isSupportMode = is_support
                return True
                break
        return False

    def AddUserRaw(self, name, ping, active):
        self.users.append(User(name, ping, active))

    def AddUser(self, user):
        if user in self.users:
            printl(f"User {user} already in manager")
            return False
        self.users.append(user)
        return True
    
    def RemoveUser(self, user):
        if user not in self.users:
            printl(f"User {user} not in manager")
            return False
        self.users.remove(user)
        return True
        
    def UpdateStrength(self, name, verbose = False):
        for c in self.characters:
            if name != None and c.name != name:
                continue
            appx = GetApproxStrength(c.name) / 30000
            # if c.power < appx:
            c.power = appx 
            if verbose:
                printl("Updated %s's strength to %2.1f" % (c.name, c.power))

    def GetCharacterByName(self, name):
        for c in self.characters:
            if c.name == name:
                return c
        return None
    
    def GetCharactersByUser(self, user):
        return [c for c in self.characters if c.user == user]
    
    def GetCharactersByRole(self, role):
        return [c for c in self.characters if c.role == role]
    
    def ResetParty(self):
        self.parties = []
        self.leftovers = []
        for c in self.characters:
            self.leftovers.append(c)
    
    def SetPartyClearState(self, partyIndex, state):
        if partyIndex >= len(self.parties) or partyIndex < 0:
            return False
        self.parties[partyIndex].cleared = state

    def GetUserByName(self, name):
        for user in self.users:
            if user.name == name:
                return user
        return None

    def SetUserActive(self, name, state):
        for user in self.users:
            if user.name == name:
                user.active = state
                return True
        return False

    def SetCharacterActive(self, name, state):
        for character in self.characters:
            if character.name == name:
                character.active = state
                return True
        return False


    def GenerateParty(self, parameters = dict(), verbose = False):
        printl("#"*50)
        printl("Party Generation Algorithm has been started.")
        printl("Parameters" + str(parameters))
        self.ResetParty()
        # If there are less than 4 characters, do not make a party
        if len(self.characters) < 4:
            if verbose:
                printl("Not enough characters to make a party(4), party is not generated")
            return -1


        # Count number of parties should be maded
        charCountTotal = len(self.characters)
        charCountEssential = 0
        for c in self.characters:
            if self.GetUserByName(c.owner).active:
                if c.essential:
                    charCountEssential += 1
        if verbose:
            printl("%d number of essential(%d total), active characters detected." % (charCountEssential, charCountTotal))
        
        ownerDict = {}
        for char in self.characters:
            if not char.active:
                continue
            if self.GetUserByName(char.owner).active:
                if char.owner in ownerDict:
                    if char.essential:
                        ownerDict[char.owner].countEssential += 1
                        ownerDict[char.owner].charEssential.append(char)
                    else:
                        ownerDict[char.owner].countNonessential += 1
                        ownerDict[char.owner].charNonessential.append(char)

                else:
                    ownerDict[char.owner] = UserInfo(countEssential=1, charEssential=[char])
        
        if verbose:
            printl("User Information:")
            for user in self.users:
                printl(f"  {user.name} {ownerDict[user.name]}")
        
        tott = 0

        best_score = 0
        best_ind = 0
        best_text = ""
        best_cube = None

        sample_steps = 4096 if "sample_steps" not in parameters else parameters["sample_steps"]
        
        for step in range(sample_steps):
            pts = ""
            for val in ownerDict:
                ownerDict[val].countAssigned = 0
            # Return all boths to the supporter mode
            for character in self.characters:
                if character.isBoth():
                    character.isSupportMode = True

            # Count number of supporters
            isLackOfSupporter = False
            numSupporters = 0
            supporterList, supporterNSList = [], []
            for c in self.characters:
                if not c.active:
                    continue
                if c.isSupporter() and self.GetUserByName(c.owner).active:
                    if c.essential:
                        supporterList.append(c)
                        numSupporters += 1
                    else:
                        supporterNSList.append(c)
        
            cube = Cube()
            pts += "Cube #%4d: "%(step+1)

            # groupSize should be random between 2 and 6, I think.
            groupSize = random.randint(3, 6) # groupSize = 6 
            pts += "GS=%d"%groupSize
            # Making consecutive groups
            groups = []
            rep = 100
            while groupSize >= 1:
                cand = []
                for _, val in enumerate(ownerDict):
                    if ownerDict[val].countEssential - ownerDict[val].countAssigned >= groupSize:
                        cand.append(val)
                if len(cand) >= 4:
                    random.shuffle(cand)
                    cand = cand[:4]
                    supcnt = 0
                    for char in supporterList:
                        if char.owner in cand:
                            supcnt += 1
                    if supcnt < groupSize:
                        rep -= 1
                        if rep < 0:
                            groupSize -= 1
                            rep = 100
                        continue
                    groups.append(Group(count=groupSize, users=cand[:4]))
                    for i in range(4):
                        ownerDict[cand[i]].countAssigned += groupSize
                else:
                    groupSize -= 1
            # Append group using non-essential, starting from group size 4
            flagNonessential = False
            for user in self.users:
                if not user.active:
                    continue
                if ownerDict[user.name].countAssigned < ownerDict[user.name].countEssential:
                    flagNonessential = True
                    break
            if flagNonessential:
                groupSize = 4
                rep = 100
                while groupSize >= 1:
                    cand = []
                    for _, val in enumerate(ownerDict):
                        if ownerDict[val].countEssential + ownerDict[val].countNonessential - ownerDict[val].countAssigned >= groupSize:
                            cand.append(val)
                    if len(cand) >= 4:
                        random.shuffle(cand)
                        cand = cand[:4]
                        supcnt = 0
                        for char in supporterList:
                            if char.owner in cand:
                                supcnt += 1
                        if supcnt < groupSize:
                            rep -= 1
                            if rep < 0:
                                groupSize -= 1
                                rep = 100
                            continue
                        groups.append(Group(count=groupSize, users=cand[:4]))
                        for i in range(4):
                            ownerDict[cand[i]].countAssigned += groupSize
                    else:
                        groupSize -= 1
            
            
            partyCount = 0
            for group in groups:
                partyCount += group.count
            if numSupporters < partyCount:
                # Append leftover supporters
                for c in supporterNSList:
                    supporterList.append(c)
                    numSupporters += 1
                if numSupporters < partyCount:
                    isLackOfSupporter = True
            elif numSupporters > partyCount:
                # Get all boths
                boths = []
                for c in self.characters:
                    if not c.active:
                        continue
                    if c.essential and c.isBoth() and self.GetUserByName(c.owner).active:
                        boths.append(c)
                boths.sort(key=lambda x: x.power, reverse=True)
                # Set random boths to be non-supporter mode
                for i in range(min(len(boths),numSupporters - partyCount)):
                    boths[i].isSupportMode = False
                    supporterList.remove(boths[i])
                    # if verbose:
                    #     printl(f"Character {boths[i].name} is set to non-supporter mode.")
        

            flag = False
            for user in self.users:
                if not user.active:
                    continue
                if ownerDict[user.name].countAssigned < ownerDict[user.name].countEssential:
                    flag = True
                    break
            if flag:
                pts += " 1X"
                cube.score = -9999
                
                if verbose:
                    printl(pts)
                continue
            else:
                pts += " 1O "


            # Phase 2: Ensure one supporter for one party
            supporters = dict()
            for char in supporterList:
                if char.isSupporter():
                    if char.owner not in supporters:
                        supporters[char.owner] = []
                    if ownerDict[char.owner].countAssigned > ownerDict[char.owner].countEssential or char.essential:
                        supporters[char.owner].append(char)
            
            # get appearances of each user
            appears = dict()
            for group in groups:
                for user in group.users:
                    if user not in appears:
                        appears[user] = 1
                    else:
                        appears[user] += 1
            # iterate through appears
            groups.sort(key=lambda x: x.count)
            for group in groups:
                group.users.sort(key=lambda x: appears[x]+10 - len(supporters[x] if x in supporters else []))
                if group.count > len(group.sups):
                    names = group.users * group.count
                    for user in names:
                        if len(group.sups) == group.count:
                            break
                        if user in supporters and len(supporters[user]) > 0:
                            group.sups.append(supporters[user][0])
                            supporters[user].remove(supporters[user][0])
                            
            ss = ""
            for s in supporters:
                if len(supporters[s]) > 0:
                    ss += str(supporters[s]) + ","
            if ss == "":
                pts += "2O "
            else:
                pts += "2X "
                cube.score = -9999
                
                if verbose:
                    printl(pts)
                continue
            
            # Phase 3: Assign Characters and get score
            dealers = dict()
            dealersNS = dict()
            for char in self.characters:
                if not char.active:
                    continue
                if not char.isSupporter():
                    if char.owner not in dealers:
                        dealers[char.owner] = []
                        dealersNS[char.owner] = []
                    if char.essential:
                        dealers[char.owner].append(char)
                    else:
                        dealersNS[char.owner].append(char)


            # Assign sups and deals to the party and get mse
            pps = []
            groups.sort(key=lambda x: x.count, reverse=True)
            for dealer in dealers:
                random.shuffle(dealers[dealer])
            for group in groups:
                for iv in range(group.count):
                    pps.append(Party(len(pps)))
                    if iv < len(group.sups):
                        pps[-1].AddCharacter(group.sups[iv])
                    for user in group.users:
                        if user in dealers and len(dealers[user]) > 0:
                            v = pps[-1].AddCharacter(dealers[user][0], strict=False)
                            if v:
                                dealers[user].remove(dealers[user][0])
                        elif user in dealersNS and len(dealersNS[user]) > 0:
                            v = pps[-1].AddCharacter(dealersNS[user][0], strict=False)
                            if v:
                                dealersNS[user].remove(dealersNS[user][0])
            
            # Get Score
            ttStr = 0
            for party in pps:
                ttStr += party.GetPartyPower()
            averageStr = ttStr / len(pps)

            score_powerbal, score_validsup, score_validrole = 0, 0, 0
            score_group = 0
            weight_powerbal = 30 if "weight_powerbal" not in parameters else parameters["weight_powerbal"]
            weight_validsup = 20 if "weight_validsup" not in parameters else parameters["weight_validsup"]
            weight_validrole = 20 if "weight_validrole" not in parameters else parameters["weight_validrole"]
            weight_group = 30 if "weight_group" not in parameters else parameters["weight_group"]
            for party in pps:
                pw = party.GetPartyPower()
                if pw < averageStr:
                    score_powerbal += (averageStr - pw) ** 2 * 2
                else:
                    score_powerbal += (pw - averageStr) ** 2
                if not party.isRoleDupe():
                    score_validrole += weight_validrole
                if party.isSupporterExists():
                    score_validsup += weight_validsup

            # Score based on group
            for key in appears:
                if appears[key] > 1:
                    score_group += (appears[key] - 1) ** 2

            score_validsup = score_validsup / len(pps)
            score_validrole = score_validrole / len(pps)
            score_powerbal = max(weight_powerbal - score_powerbal / len(pps), 0)

            score_group = max(0, weight_group - score_group / len(appears))
            
            cube.score += score_powerbal + score_validsup + score_validrole + score_group
                
            tott += 1
            pts += "%2.1f "%(cube.score)
            
            

            if verbose:
                printl(pts)
                pss = "Party Info:\n"
                for party in pps:
                    pss += " "*22+str(party) + "\n"
                printl(pss)
            
            if cube.score > best_score:
                
                cube.parties = pps
                cube.groups = groups
                for char in self.characters:
                    if char.isBoth():
                        cube.charSup[char.name] = char.isSupportMode

                best_score = cube.score
                best_cube = cube
                best_ind = step
                best_text = "%5.1f=(PB)%4.1f+(VS)%4.1f+(VR)%4.1f+(GR)%4.1f"%(cube.score, score_powerbal, score_validsup, score_validrole, score_group)

                printl("Cube #%d, Best Score Updated: %s"%(step, best_text))

        printl("#"*50)
        printl("Valid Generations: %d/%d"%(tott, sample_steps))

        # if verbose:
        printl("Best Result: Cube #%d"%(best_ind))
        printl("  Score: %2.1f"%(best_score))
        pss = "  Group Info:\n"
        for ggg in best_cube.groups:
            pss += str(ggg) + "\n"
        printl(pss[:-1])
        pss = "  Party Info:\n"
        for party in best_cube.parties:
            pss += str(party) + "\n"
        printl(pss)
        self.parties = best_cube.parties
        self.groups = [g.count for g in best_cube.groups]
        
        for char in self.characters:
            if char.name in best_cube.charSup:
                char.isSupportMode = best_cube.charSup[char.name]
        
        self.Validate()

        return best_score, best_text
