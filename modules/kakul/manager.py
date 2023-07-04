#-*- coding:utf-8 -*-
import random
import time
import math
import itertools

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
    supp: list = field(default_factory=list)
    deal: list = field(default_factory=list)


def GetTextTime(ind):
    days = ["수", "목", "금", "토", "일", "월", "화"]
    return days[ind//72] + " " + "%02d:%02d"%((ind%72)//3+10, ind%3*20)

# Time starts on 10:00 AM, Wed (End of lost ark maintenance)
# Each time slot is 20 minutes
def GetAllTimesWithoutDay(days):
    v = []
    if "수" not in days:
        v.extend(range(     12*3,     14*3)) # 22:00 ~ 24:00
    if "목" not in days:
        v.extend(range(72*1+12*3,72*1+14*3)) # 22:00 ~ 24:00
    if "금" not in days:
        v.extend(range(72*2+12*3,72*2+14*3)) # 22:00 ~ 24:00
    if "토" not in days:
        v.extend(range(72*3+ 6*3,72*3+ 8*3)) # 16:00 ~ 18:00
    if "일" not in days:
        v.extend(range(72*4+ 6*3,72*4+ 8*3)) # 16:00 ~ 18:00
    if "월" not in days:
        v.extend(range(72*5+12*3,72*5+14*3)) # 22:00 ~ 24:00
    if "화" not in days:
        v.extend(range(72*6+12*3,72*6+14*3)) # 22:00 ~ 24:00
    return v


class Manager:
    def __init__(self, idn):
        self.channel = None # Channel id
        self.characters = [] # list of Character
        self.users = [] # list of users

        self.leftovers = [] # list of characters
        self.parties = []
        self.groups = []

        self.idn = idn
        self.time_domain = dict()
    
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
    
    def EditPartyTime(self, partyIndex, daytime):
        self.parties[partyIndex].daytime = daytime
        return True

    def AddPartyRaw(self, names, clear, daytime):
        self.parties.append(Party(len(self.parties)))
        self.parties[-1].cleared = clear
        self.parties[-1].daytime = daytime
        for name in names:
            v = self.GetCharacterByName(name)
            if v is not None:
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

    def AddUserRaw(self, name, ping, active, avoiddays):
        self.users.append(User(name, ping, active, avoiddays))

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
        
    def UpdateStrength(self, name, force = False, verbose = False):
        for c in self.characters:
            if name != None and c.name != name:
                continue
            appx = GetApproxStrength(c.name) / 30000
            if not force:
                if c.power < appx:
                    c.power = appx
            else:
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
    
    def IsUserExists(self, name):
        for user in self.users:
            if user.name == name:
                return True
        return False

    def SetUserActive(self, name, state):
        for user in self.users:
            if user.name == name:
                user.active = state
                return True
        return False
    
    def SetUserAvoidDays(self, name, days):
        for user in self.users:
            if user.name == name:
                user.avoiddays = days
                return True
        return False

    def SetCharacterActive(self, name, state):
        for character in self.characters:
            if character.name == name:
                character.active = state
                return True
        return False

    def SetCharacterEssential(self, name, state):
        for character in self.characters:
            if character.name == name:
                character.essential = state
                return True
        return False

    def RecalculateTime(self, time_domain=None):
        
        for pind in range(len(self.parties)):
            users = []
            for mem in self.parties[pind].members:
                users.append(mem.owner)
            sss = []
            for user in self.users:
                if self.parties[pind].isOwnerExists(user.name):
                    for day in user.avoiddays:
                        sss.append(day)
            svs = ""
            for day in ["수", "목", "금", "토", "일", "월", "화"]:
                if day not in sss:
                    svs += day
            self.parties[pind].daytime = svs
            
        """
        if time_domain == None:
            fill = dict()
        else:
            fill = time_domain
        pind = 0
        for pind in range(len(self.parties)):
            users = []
            for mem in self.parties[pind].members:
                users.append(mem.owner)
            sss = []
            for user in self.users:
                if self.parties[pind].isOwnerExists(user.name):
                    for day in user.avoiddays:
                        sss.append(day)
            times = GetAllTimesWithoutDay(list(set(sss)))
            for ti in times:
                if str(ti) not in fill:
                    self.parties[pind].daytime = GetTextTime(ti)
                    fill[str(ti)] = []
                    for user in users:    
                        fill[str(ti)].append(user)
                    break
                else:
                    flag = False
                    for user in users:
                        if user in fill[str(ti)]:
                            flag = True
                    if not flag:
                        self.parties[pind].daytime = GetTextTime(ti)
                        for user in users:
                            fill[str(ti)].append(user)
                        break
        self.time_domain = fill
        """
            

    def GeneratePartyV3(self, parameters = dict(), verbose = False):
        self.ResetParty()
        if len(self.characters) < 4:
            printl("Not enough characters to make a party(4), party is not generated")
            return -1
        printl("#"*50)
        printl("Party Generation Algorithm v3 has been started.")
        printl("Parameters" + str(parameters))

        sample_steps = 10 if "sample_steps" not in parameters else parameters["sample_steps"]
        optimize_steps = 256 if "optimize_steps" not in parameters else parameters["optimize_steps"]
        weight_group = 0.25 if "weight_group" not in parameters else parameters["weight_group"]
        weight_power = 2 if "weight_power" not in parameters else parameters["weight_power"]
        weight_duperole = 1 if "weight_duperole" not in parameters else parameters["weight_duperole"]

        best_error = 9999
        best_both2deal = []

        def EvaluateParties(pps, param_pow = 2, param_dupe = 1):
            if len(pps) <= 0:
                return -1
            res1, res2 = 0, 0
            pw_tot = 0
            for p in pps:
                pw_tot += p.GetPartyPower()
                if p.isRoleDupe():
                    res2 += param_dupe
            pw_avg = pw_tot / len(pps)
            for p in pps: # Mean square error
                res1 += (p.GetPartyPower() - pw_avg) ** 2 * param_pow
            return (res1 + res2) / len(pps)

        def _TempLenPrint(n):
            strr = ""
            for key, value in n.items():
                if value["supp"] == 0 and value["deal"] == 0:
                    continue
                strr += f'{key}:({value["deal"]}, {value["supp"]}) '
            printl(strr)

        valid_gens = 0
        for step in range(sample_steps):
            deal_ess, supp_ess = [], []
            deal_ext, supp_ext = [], []
            both_ess, both_ext = [], []
            for c in self.characters:
                if c.isBoth():
                    c.isSupportMode = True
                if self.GetUserByName(c.owner).active:
                    if c.active:
                        if c.essential:
                            if c.isSupporter():
                                supp_ess.append(c)
                            else:
                                deal_ess.append(c)
                            if c.isBoth():
                                both_ess.append(c)
                        else:
                            if c.isSupporter():
                                supp_ext.append(c)
                            else:
                                deal_ext.append(c)
                            if c.isBoth():
                                both_ext.append(c)
            
            # Step 1, manage supporter-dealer ratio
            both2deal = []
            if verbose:
                printl(" >>> Step 1 : manage supporter-dealer ratio, %d/%d"%(len(supp_ess), len(deal_ess)))
            while len(supp_ess) * 3 != len(deal_ess):
                if len(supp_ess) * 3 < len(deal_ess):
                    if len(supp_ext) > 0:
                        supp = random.choice(supp_ext)
                        supp_ess.append(supp)
                        supp_ext.remove(supp)
                        if verbose:
                            printl("Added " + supp.name + " to support")
                    else:
                        break
                elif len(supp_ess) * 3 > len(deal_ess) + 3 and (len(both_ess) > 0 or len(both_ext) > 0):
                    if len(both_ess) > 0: # Change "Both" to "Dealer"
                        both = random.choice(both_ess)
                        deal_ess.append(both)
                        supp_ess.remove(both)
                        both_ess.remove(both)
                        both2deal.append(both)
                        if verbose:
                            printl("Changed " + both.name + " to dealer")
                    elif len(both_ext) > 0:
                        both = random.choice(both_ext)
                        deal_ess.append(both)
                        supp_ext.remove(both)
                        both_ext.remove(both)
                        both2deal.append(both)
                        if verbose:
                            printl("Changed " + both.name + " to dealer")
                    else:
                        break
                elif len(supp_ess) * 3 > len(deal_ess):
                    if len(deal_ext) > 0: # Append Extra dealers first
                        deal = random.choice(deal_ext)
                        deal_ess.append(deal)
                        deal_ext.remove(deal)
                        if verbose:
                            printl("Added " + deal.name + " to dealer")
                    else:
                        break
            if len(supp_ess) * 3 != len(deal_ess):
                printl("Dealer-Support ratio is not sufficient to create parties, party will not generated")
                return -1
            deals = deal_ess
            supps = supp_ess
            if verbose:
                printl("%d/%d, total %d parties will be generated" % (len(supps), len(deals), len(supps)))
            total_char_n = len(deals) + len(supps)
            # Add current Character pool to data
            cnt_user = {}
            deal_user, supp_user = {}, {}
            for c in deals:
                if c.owner not in cnt_user:
                    cnt_user[c.owner] = {"deal": 0, "supp": 0}
                    deal_user[c.owner] = []
                    supp_user[c.owner] = []
                deal_user[c.owner].append(c)
            for c in supps:
                if c.owner not in cnt_user:
                    cnt_user[c.owner] = {"deal": 0, "supp": 0}
                    deal_user[c.owner] = []
                    supp_user[c.owner] = []
                supp_user[c.owner].append(c)

            # Step 2. Create group starting from Max number of consecutive parties.
            ## Get every possible combination of users that have more than N characters.
            ## Choose element that has more supporter count than party count.
            ## Repeat until there is no more possible combination.
            ## After the process, if there dealer is left, ignore.

            groups = []
            if verbose:
                printl(" >>> Step 2 : Create group starting from Max number of consecutive parties")
            max_iter, curr_iter = 32, 0
            while(curr_iter < max_iter):
                curr_iter += 1
                finished = True
                maxu, chn = 0, 0
                for u in cnt_user:
                    cnt_user[u] = {"deal": len(deal_user[u]), "supp": len(supp_user[u])}
                    cnt = cnt_user[u]["deal"] + cnt_user[u]["supp"]
                    if cnt > 0:
                        chn += cnt
                        if cnt >= maxu:
                            maxu = cnt
                        finished = False
                if verbose:
                    _TempLenPrint(cnt_user)
                if maxu * 4 > chn:
                    break
                if finished:
                    break
                max_group = max([cnt_user[x]["deal"] + cnt_user[x]["supp"] for x in cnt_user])
                # TODO : Maybe make this random to get better results
                group_iter = random.randint(max(0, max_group-3), max_group)
                for group_size in range(group_iter, 0, -1):
                    users = [x for x in cnt_user if cnt_user[x]["deal"] + cnt_user[x]["supp"] >= group_size]
                    candidates = []
                    for comb in itertools.combinations(users, 4):
                        if cnt_user[comb[0]]["supp"] + cnt_user[comb[1]]["supp"] + cnt_user[comb[2]]["supp"] + cnt_user[comb[3]]["supp"] >= group_size and cnt_user[comb[0]]["deal"] + cnt_user[comb[1]]["deal"] + cnt_user[comb[2]]["deal"] + cnt_user[comb[3]]["deal"] >= group_size * 3:
                            candidates.append(comb)
                    if verbose and len(candidates) > 0:
                        printl(f"Group size: {group_size}, {len(candidates)} candidates")
                    if len(candidates) == 0: # Skip to next group size
                        continue
                    # Pick one of the candidates
                    candidate = random.choice(candidates)
                    if verbose:
                        printl(f"Selected candidate: {candidate}")
                    candn = {}
                    for user in candidate:
                        candn[user] = 0
                    group = Group(count=group_size, users=list(candidate))
                    _remove = []
                    # If a user has exact number of characters, append all characters
                    for user in candidate:
                        if len(supp_user[user]) + len(deal_user[user]) == group_size:
                            candn[user] += group_size
                            for char in supp_user[user]:
                                group.supp.append(char)
                                _remove.append(char)
                            for char in deal_user[user]:
                                group.deal.append(char)
                                _remove.append(char)

                    # Append characters if user has only one type of character
                    for user in candidate:
                        if cnt_user[user]["deal"] == 0:
                            for char in supp_user[user]:
                                if char not in group.supp:
                                    group.supp.append(char)
                                    _remove.append(char)
                                    candn[user] += 1
                                    if candn[user] >= group_size:
                                        break 
                        if cnt_user[user]["supp"] == 0:
                            for char in deal_user[user]:
                                if char not in group.deal:
                                    group.deal.append(char)
                                    _remove.append(char)
                                    candn[user] += 1
                                    if candn[user] >= group_size:
                                        break 
                    # Check if group is not valid
                    if len(group.supp) > group_size or len(group.deal) > group_size * 3:
                        if verbose:
                            printl(f"Group is not valid, skipping #Supp:{len(group.supp)}, #Deal:{len(group.deal)}")
                        break
                    # Append supporters
                    supps_temp = []
                    for user in candidate:
                        for char in supp_user[user]:
                            supps_temp.append(char)
                    for char in supps_temp:
                        if len(group.supp) >= group_size:
                            break
                        if candn[char.owner] < group_size:
                            if char not in group.supp:
                                group.supp.append(char)
                                _remove.append(char)
                                candn[char.owner] += 1
                    # Append dealers
                    for user in candidate:
                        if candn[user] >= group_size:
                            continue
                        for char in deal_user[user]:
                            if char not in group.deal:
                                group.deal.append(char)
                                _remove.append(char)
                                candn[user] += 1
                                if candn[user] >= group_size:
                                    break
                    if len(group.supp) < group_size or len(group.deal) < group_size * 3:
                        if verbose:
                            printl(f"Group is not valid, skipping #Supp:{len(group.supp)}, #Deal:{len(group.deal)}")
                        break
                    groups.append(group)
                    for char in _remove:
                        for user in cnt_user:
                            if char in deal_user[user]:
                                deal_user[user].remove(char)
                            if char in supp_user[user]:
                                supp_user[user].remove(char)
                    if verbose:
                        printl(f"Group: {group}")
                    break
            if not finished:
                if verbose:
                    printl("Failed to generate groups, moving to next step")
                continue
            # Intermission - create parties from groups
            parties = []
            for group in groups:
                pps = []
                for i in range(group.count):
                    pps.append(Party(len(parties)+i))
                for char in group.supp:
                    for party in pps:
                        success = party.AddCharacter(char, strict=True)
                        if success:
                            break
                for char in group.deal:
                    for party in pps:
                        success = party.AddCharacter(char, strict=False)
                        if success:
                            break
                parties.extend(pps)
            
            if verbose:
                printl(str(parties))
            valid_gens += 1
            # Step 4. Optimize party by swapping characters with same owner.
            ## 1. It is not good to have same role in party
            ## 2. It is better if every parties are balanced
            curr_error = EvaluateParties(parties, weight_power, weight_duperole)
            if verbose:
                print(f"Current error: {curr_error}")
            for opt_step in range(optimize_steps):
                # Random swap two characters, maybe using this...? >> self.ReplaceCharacters
                # get a random character from random party
                p1 = random.choice(parties)
                char1 = random.choice(p1.members)
                if char1.isSupporter():
                    continue
                owner_char = []
                # find another member from another party with same owner
                for p2 in parties:
                    if p1.idx == p2.idx:
                        continue
                    for char in p2.members:
                        if char1.owner == char.owner and not char.isSupporter():
                            owner_char.append(char)
                            break
                if len(owner_char) == 0:
                    continue
                char2 = random.choice(owner_char)
                for p2 in parties:
                    if char2 in p2.members:
                        break
                p1.members.remove(char1)
                p2.members.remove(char2)
                p1.members.append(char2)
                p2.members.append(char1)
                new_error = EvaluateParties(parties, weight_power, weight_duperole)
                if new_error < curr_error:
                    curr_error = new_error
                else:
                    p1.members.remove(char2)
                    p2.members.remove(char1)
                    p1.members.append(char1)
                    p2.members.append(char2)
                if opt_step % 10 == 0 and verbose:
                    printl(f"Optimize Step {opt_step+1}/{optimize_steps}, Error: {curr_error}")
            # Step 5. Calculate the score, and if party is good enough, replace old one
            ## Score is calculated by avoiddays, EvaluateParties, party dupes
            ##
            appears = dict()
            for group in groups:
                for user in group.users:
                    if user not in appears:
                        appears[user] = 1
                    else:
                        appears[user] += 1
            group_error = 0
            for user in appears:
                group_error += appears[user] ** 2 * weight_group
            group_error = group_error / len(appears)

            final_error = group_error + curr_error
            if verbose:
                printl(f"Final Error: {final_error}")
            if final_error < best_error:
                best_error = final_error
                best_both2deal = both2deal
                self.parties = parties
                printl(f'New best #{step+1}, error: {best_error}')
                
        for char in self.characters:
            if char in best_both2deal:
                char.isSupportMode = False
        self.RecalculateTime()
        printl("#"*50)
        printl(f'{valid_gens}/{sample_steps} valid party generations')
        printl(str(self.parties))
        printl(f'Final Error: {best_error}')
        return best_error
