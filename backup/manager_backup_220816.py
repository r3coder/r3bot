
import random
import discord

ROLE_LIST = ["디스트로이어", "버서커", "워로드", "홀리나이트(딜)", "홀리나이트(폿)", "홀리나이트(딜폿)", "기공사", "배틀마스터", "스트라이커", "인파이터", "창술사", "건슬링어", "데빌헌터", "블래스터", "스카우터", "호크아이", "바드(딜)", "바드(폿)", "바드(딜폿)", "서머너", "소서리스", "아르카나", "도화가(딜)", "도화가(폿)", "도화가(딜폿)", "리퍼", "블레이드", "데모닉", "기상술사"]

class Character:
    def __init__(self, owner, name, role, essential = True, power = 1.0):
        self.owner = owner
        self.name = name
        self.role = role
        self.essential = essential
        self.power = power

        if self.role in ["홀리나이트(폿)", "바드(폿)", "도화가(폿)"]:
            self.isSupportMode = True
        else:   
            self.isSupportMode = False
    
    def __repr__(self):
        v = "필수X" if not self.essential else ""
        t = ""
        if self.role in ["홀리나이트(딜폿)", "바드(딜폿)", "도화가(딜폿)"]:
            t = "(폿)" if self.isSupportMode else "(딜)"
        if self.isSupportMode:
            return f"{self.name} / {self.role}{t} - {self.owner} {v}"
        else:
            return f"{self.name} / {self.role}{t} - {self.owner} | {self.power} {v}"

    def isSupporter(self):
        if self.role in ["홀리나이트(폿)", "바드(폿)", "도화가(폿)"] or self.isSupportMode:
            return True
    
    def isBoth(self):
        if self.role in ["홀리나이트(딜폿)", "바드(딜폿)", "도화가(딜폿)"]:
            return True
    
    # equal
    def __eq__(self, other):
        if type(other) != type(self):
            return False
        return self.owner == other.owner and self.name == other.name and self.role == other.role and self.power == other.power

class Party:
    def __init__(self):
        self.members = []
        self.isCleared = False

    def isOwnerExists(self, owner):
        for member in self.members:
            if member.owner == owner:
                return True
        return False
    
    def isRoleExists(self, role):
        for member in self.members:
            if member.role.replace("(딜)", "").replace("(폿)", "").replace("(딜폿)", "") == role.replace("(딜)", "").replace("(폿)", "").replace("(딜폿)", ""):
                return True
        return False
    
    def getPartyStrength(self):
        f = 0
        for member in self.members:
            if not member.isSupporter():
                f += member.power
        return f

    def isSupporterExists(self):
        for member in self.members:
            if member.isSupporter():
                return True
        return False

    def addMember(self, member):
        if len(self.members) < 4:
            self.members.append(member)
            return True
        else:
            return False

    def RemoveCharacter(self, member):
        self.members.remove(member)

    def __repr__(self):
        v = ":o:" if self.isCleared else ":x:"
        s = "인원:%d/4, 딜량:%2.2f, 클리어:%s\n"%(len(self.members), self.getPartyStrength(), v)
        for member in self.members:
            s += "  " + str(member) + "\n"
        return s
    
class Manager:
    def __init__(self):
        # Variables that saved
        self.characters = []
        self.pingList = dict()


        # Variables that not saved
        self.parties = []
        self.leftovers = []

        self.partyPowerMaxThreshold = 5.0
        self.partyPowerMinThreshold = 4.0
        self.priorityPower = 3.0
    
    def IsCharacterExists(self, name):
        for character in self.characters:
            if character.name == name:
                return True
        return False

    def GetCharacterByName(self, name):
        for character in self.characters:
            if character.name == name:
                return character
        return None

    def GetPartyOfCharacter(self, name):
        for idx in range(len(self.parties)):
            for char in self.parties[idx].members:
                if char.name == name:
                    return idx
        return -1

    def ChangeCharacterPosition(self, name1, name2):
        # find name1 or name2 in parties and change position
        for party in self.parties:
            for i in range(len(party.members)):
                if party.members[i].name == name1:
                    self.leftovers.append(party.members[i])
                    party.members[i] = self.GetCharacterByName(name2)
                    del self.leftovers[party.members[i]]
                    return True
                elif party.members[i].name == name2:
                    self.leftovers.append(party.members[i])
                    party.members[i] = self.GetCharacterByName(name1)
                    del self.leftovers[party.members[i]]
                    return True
        return False
    
    def ResetParties(self):
        self.parties = []
        self.leftovers = []

    def SwapPartyMember(self, member1, member2):

        pass

    def AssignToParty(self, dealer, duplicateRoleCheck = False, dealerPowerCheck = False):
        
        assigned = False
        for idx in range(len(self.parties)):
            # Must check condition
            if not self.parties[idx].isOwnerExists(dealer.owner) and len(self.parties[idx].members) < 4:
                dupRole = duplicateRoleCheck and not self.parties[idx].isRoleExists(dealer.role)
                power = dealerPowerCheck and self.parties[idx].getPartyStrength() + dealer.power <= self.partyPowerMaxThreshold
                if not duplicateRoleCheck and not dealerPowerCheck:
                    assigned = True
                    break
                elif dupRole and not dealerPowerCheck:
                    assigned = True
                    break
                elif not dealerPowerCheck and power:
                    assigned = True
                    break
                elif dupRole and power:
                    assigned = True
                    break

        if assigned:
            self.parties[idx].addMember(dealer)
            print("Assigned %s to party %d"%(dealer, idx+1))
        else:
            print("%s is not assigned"%dealer)

        return assigned

    def BalanceBetweenTwoParties(self, ind1, ind2):
        if self.parties[ind1].getPartyStrength() > self.parties[ind2].getPartyStrength():
            ind1, ind2 = ind2, ind1

        self.parties[ind1].members.sort(key=lambda x:x.power)
        self.parties[ind2].members.sort(key=lambda x:x.power)

        v1 = self.parties[ind1].members
        v2 = self.parties[ind2].members
        for m1 in v1:
            for m2 in v2:
                self.SwapPartyMember(m1, m2)
                if self.parties[ind1].getPartyStrength >= self.partyPowerMinThreshold:
                    return True
        return False  

    def MakeParties(self):
        # Reset parties and leftovers
        self.parties = []
        self.leftovers = []
        ### main Party making Logic ###
        # Return nothing if there is no characters
        if len(self.characters) < 1:
            return
        # If there is less then 4 people, make one party
        if len(self.characters) < 4:
            self.parties.append(Party())
            for character in self.characters:
                self.parties[-1].addMember(character)

        # create number of parties
        party_count = (len(self.characters)+1) // 4
        for i in range(party_count):
            self.parties.append(Party())
        supporters, dealers, both, non_essential = [], [], [], []

        owner_count = dict()
        # Assign supporters
        for i in self.characters:
            if i.essential:
                if i.isSupporter():
                    supporters.append(i)
                elif i.isBoth():
                    i.isSupportMode = False
                    both.append(i)
                else:
                    dealers.append(i)
            else:
                non_essential.append(i)
            
            if i.owner not in owner_count:
                owner_count[i.owner] = 1
            else:
                owner_count[i.owner] += 1
            

        # Print Statstics
        print("Create party with %d characters"%len(self.characters))
        print("%d Parties will be created"%party_count)
        print("Supporters(%d) : %s"%(len(supporters),str(supporters)))
        print("Dealers(%d) : %s"%(len(dealers),str(dealers)))
        print("Both(%d) : %s"%(len(both),str(both)))
        print("Non-essential(%d) : %s"%(len(non_essential),str(non_essential)))

        # Assign supporters to parties
        random.shuffle(supporters)
        if len(supporters) < party_count:
            # Lack of supporters
            print("Lack of supporters, assigning both to the supporters")
            iv = 0
            for i in range(len(supporters)):
                self.parties[iv].addMember(supporters[i])
                iv += 1
            # Append both to left parties
            if len(both) <= party_count - iv:
                print("Supporters are still in shortage, some dealers will be send to leftover lateron")
                for i in range(len(both)):
                    both[len(both)-1].isSupportMode = True
                    self.parties[iv].addMember(both[len(both)-1])
                    del both[len(both)-1]
                    iv += 1
            else:
                print("Supporters are enough, assigning rest to dealers")
                for i in range(party_count - iv):
                    both[len(both)-1].isSupportMode = True
                    self.parties[iv].addMember(both[len(both)-1])
                    del both[len(both)-1]
                    iv += 1                
        else:
            print("Enough supporters, send supporters to leftover")
            for i in range(party_count):
                self.parties[i].addMember(supporters[i])
            # Assign rest of supporters to leftovers
            for i in range(party_count, len(supporters)):
                self.leftovers.append(supporters[i])

        # Now, assign dealers (and left supporters that can be dealer)
        dealers = both + dealers
        random.shuffle(dealers)
        print("Dealers (+both) to be assigned:%s"%str(dealers))

        print(f" == Assigning strong characters (<={self.priorityPower})")
        dealers.sort(key=lambda x:x.power, reverse=True)
        dellist = []
        for dealer in dealers:
            if dealer.power >= self.priorityPower:
                self.parties.sort(key=lambda x:x.getPartyStrength())
                res = self.AssignToParty(dealer, True, True)
                if not res:
                    self.leftovers.append(dealer)
                dellist.append(dealer)
        for dealer in dellist:
            dealers.remove(dealer)
        

        dealers = dealers + self.leftovers
        assign_threshold = party_count / 2
        print(f" == Assign user with many characters (<={assign_threshold})")
        # Rule 1. Assign person who with most characters (threshold = 1/2 of party count)
        while len(dealers) > 0:
            max_numbers = [key for key, value in owner_count.items() if value == max(owner_count.values())]
            cur_owner = max_numbers[0]
            if owner_count[cur_owner] <= assign_threshold:
                break
            del owner_count[cur_owner]

            dellist = []
            for dealer in dealers:
                if dealer.owner == cur_owner:
                    # print("Assigning %s's dealer :%s"%(cur_owner, dealer))
                    res = self.AssignToParty(dealer, True, True)
                    if not res:
                        self.leftovers.append(dealer)
                    dellist.append(dealer)
            for dealer in dellist:
                dealers.remove(dealer)

        print(" == Assign rest dealers... Step 1")
        # Next, place stronger characters, and rest
        dealers.sort(key=lambda x:x.power, reverse=True)
        print(dealers)
        dellist = []
        for dealer in dealers:
            self.parties.sort(key=lambda x:x.getPartyStrength())
            res = self.AssignToParty(dealer, True, True)
            if not res:
                self.leftovers.append(dealer)
            dellist.append(dealer)
        for dealer in dellist:
            dealers.remove(dealer)


        print(" == Assign rest dealers... Step 2 (w/o power)")
        dealers = dealers + self.leftovers
        random.shuffle(dealers)
        self.leftovers = []
        dellist = []
        for dealer in dealers:
            res = self.AssignToParty(dealer, True, False)
            if not res:
                self.leftovers.append(dealer)
            dellist.append(dealer)
        for dealer in dellist:
            dealers.remove(dealer)

        print(" == Assign rest dealers... Step 3 (w/o ower, role)")
        dealers = dealers + self.leftovers
        random.shuffle(dealers)
        self.leftovers = []
        dellist = []
        for dealer in dealers:
            res = self.AssignToParty(dealer, False, False)
            if not res:
                self.leftovers.append(dealer)
            dellist.append(dealer)
        for dealer in dellist:
            dealers.remove(dealer)


        print(" == Assign rest dealers... Step 4 (not required to go)")
        dealers = dealers + self.leftovers + non_essential
        random.shuffle(dealers)
        self.leftovers = []
        for dealer in dealers:
            res = self.AssignToParty(dealer, False, False)
            if not res:
                self.leftovers.append(dealer)

        """
        print(" == Shuffle rest members... Step 5")
        self.parties.sort(key=lambda x:x.getPartyStrength())
        iteration = 0
        while iteration <= len(self.parties) and self.parties[0].getPartyStrength() >= self.partyPowerMinThreshold:
            for i in range(len(self.parties)-2):
                res = self.BalanceBetweenTwoParties(0, len(self.parites) - 1 - i)
                if res:
                    break
            iteration += 1
            self.parties.sort(key=lambda x:x.getPartyStrength())
        """

        print("Party Matching Complete")
        print("Leftovers(%d) : %s"%(len(self.leftovers),str(self.leftovers)))
        # for i in self.parties:
        #     print(i)
        # print(self.leftovers)
        ## (people number - 1) % 4 + 1 
        
    def GetPartyOwners(self, ind):
        s = []
        for i in self.parties[ind].members:
            s.append(str(i.owner))
        return s

    def AddCharacter(self, owner, name, role, ess=True, power=1.0):
        if role not in ROLE_LIST:
            discord.Embed(description="직업이 잘못되었습니다.\n\n직업 리스트 : %s"%str(ROLE_LIST), color=discord.Color.red())
        c = Character(owner, name, role, ess, power)
        # Check if character is already in the list
        if c in self.characters:
            return discord.Embed(description="이미 존재하는 캐릭터입니다.", color=discord.Color.red())
        self.characters.append(c)
        s = "캐릭터 %s가 쿠크세이튼 파티 풀에 추가되었습니다."%(c.name)
        if len(self.parties) > 0: # If there is party
            self.leftovers.append(c)
            s += "\n이미 결성된 파티가 있어서, 파티에 소속되지 못한 캐릭터에 추가되었습니다."
        return discord.Embed(description=s, color=discord.Color.blue())
    
    
    def RemoveCharacter(self, name):
        flag = False
        for c in self.characters:
            if c.name == name:
                self.characters.remove(c)
                flag = True
                break

        if flag:
            return discord.Embed(description="%s 캐릭터가 쿠크세이튼 파티 풀에서 제거되었습니다. 이미 결성된 파티에서는 제거되지 않습니다."%msg[1], color=discord.Color.blue())
        else:
            return discord.Embed(description="존재하지 않는 캐릭터입니다.", color=discord.Color.red())
        
    def GetCharacterCount(self):
        return len(self.characters)

    def GetCharactersText(self):
        ss = ""
        for c in self.characters:
            ss += "%s\n"%c
        return ss
    
    def GetPartyEmbed(self):
        if len(self.parties) == 0:
            return discord.Embed(description="결성되어 있는 파티가 없습니다. 관리자에게 문의해 파티결성 명령을 입력해 주세요.", color=discord.Color.red())
        else:
            embed = discord.Embed(description="현재 쿠크세이튼 풀에 있는 파티 목록입니다.\n참가가 불가능하거나 파티 멤버 변경이 필요할 경우, 각 파티원들과 직접 조율 바랍니다.", color=discord.Color.blue())
            for v, p in enumerate(self.parties):
                stv = "(인원부족)" if len(p.members) < 4 else ""
                embed.add_field(name="파티 %d %s"%((v+1),stv), value="%s"%p, inline=False)
            p = "파티에 소속되지 못한 캐릭터들입니다.\n"
            for i in self.leftovers:
                p += "%s\n"%i
            embed.add_field(name="파티 없음", value="%s"%p, inline=False)
        return embed

    def GetUserEmbed(self, user):
        embed = discord.Embed(description="유저 %s의 정보입니다."%user, color=discord.Color.blue())
        s = ""
        cnt = 0
        for i in self.characters:
            if i.owner == user:
                cnt+=1
                s += str(i) + "\n"
        if s == "":
            "파티 풀에 포함된 캐릭터가 없습니다."
        embed.add_field(name="파티 풀에 포함된 캐릭터 수 %d"%(cnt), value="%s"%s, inline=False)
        if len(self.parties) > 0:
            for v, p in enumerate(self.parties):
                if p.isOwnerExists(user):
                    stv = "(인원부족)" if len(p.members) < 4 else ""
                    embed.add_field(name="파티 %d %s"%((v+1),stv), value="%s"%p, inline=False)
        return embed

    def SetPartyClear(self, number, status):
        try:
            p = int(number)
        except:
            p = -1
        if p < 1 or p > len(self.parties):
            return discord.Embed(description="존재하지 않는 파티 번호입니다.", color=discord.Color.red())
        
        if self.parties[p-1].isCleared == status:
            if status:
                return discord.Embed(description="이미 클리어된 파티입니다.", color=discord.Color.red())
            else:
                return discord.Embed(description="클리어 처리가 안 되어 있는 파티입니다.", color=discord.Color.red())

        # Check cleared status
        self.parties[p-1].isCleared = status

        if status:
            return discord.Embed(description="파티 %d번 클리어 완료!"%p, color=discord.Color.blue())
        else:
            return discord.Embed(description="파티 %d번 클리어 처리를 취소했습니다."%p, color=discord.Color.blue())
