
import random
import interactions

ROLE_LIST = ["디스트로이어", "버서커", "워로드", "홀리나이트(딜)", "홀리나이트(폿)", "홀리나이트(딜폿)", "기공사", "배틀마스터", "스트라이커", "인파이터", "창술사", "건슬링어", "데빌헌터", "블래스터", "스카우터", "호크아이", "바드(딜)", "바드(폿)", "바드(딜폿)", "서머너", "소서리스", "아르카나", "도화가(딜)", "도화가(폿)", "도화가(딜폿)", "리퍼", "블레이드", "데모닉", "기상술사"]

ROLE_ICON = ["<:loa_destroyer:1009187088798863380>", "<:loa_berserker:1009187084029935717>", "<:loa_gunlancer:1009187095702671380>", "<:loa_paladin:1009187101264314460>", "<:loa_paladin:1009187101264314460>", "<:loa_paladin:1009187101264314460>", "<:loa_soulfist:1009187110508560534>", "<:loa_wardancer:1009187116594511933>", "<:loa_striker:1009187112505069669>", "<:loa_scrapper:1009187104464576632>", "<:loa_glaivier:1009187093794275409>", "<:loa_gunslinger:1009187097556566088>", "<:loa_deadeye:1009187085611188244>", "<:loa_artillerist:1009187080468967476>", "<:loa_machinist:1009187099213307976>", "<:loa_sharpshooter:1009187107257987082>", "<:loa_bard:1009187082205409333>", "<:loa_bard:1009187082205409333>", "<:loa_bard:1009187082205409333>", "<:loa_summoner:1009187114954530907>", "<:loa_sorceress:1009187108424003825>", "<:loa_arcanist:1009187078829002793>", "<:loa_dohwaga:1009187090329784381>", "<:loa_dohwaga:1009187090329784381>", "<:loa_dohwaga:1009187090329784381>", "<:loa_reaper:1009187102518423645>", "<:loa_deathblade:1009187087385362502>", "<:loa_shadowhunter:1009187105915809844>", "<:loa_gisang:1009187092296892597>"]

Color = {
    "red": 0xff4444,
    "blue": 0x4444ff,
    "green": 0x44ff44,
}

def GetPowerEmoji(power):
    if power < 1.0:
        return ":scooter:"
    elif power < 1.5:
        return ":red_car:"
    elif power < 2.0:
        return ":taxi:"
    elif power < 2.5:
        return ":bus:"
    elif power < 3.0:
        return ":airplane:"
    elif power < 3.5:
        return ":rocket:"
    else:
        return ":flying_saucer:"

class Character:
    def __init__(self, owner, name, role, essential = True, power = 1.0, sup = None):
        self.owner = owner
        self.name = name
        self.role = role
        self.essential = essential
        self.power = power
        if sup is None:
            if self.role in ["홀리나이트(폿)", "바드(폿)", "도화가(폿)"]:
                self.isSupportMode = True
            else:   
                self.isSupportMode = False
        else:
            self.isSupportMode = sup

    def __repr__(self):
        v = ":x:" if not self.essential else ""
        axe = ""
        t = ""
        p = self.power if not self.isSupporter() else "   "
        if self.role in ["홀리나이트(딜폿)", "바드(딜폿)", "도화가(딜폿)"]:
            t = "(폿)" if self.isSupporter() else "(딜)"
            axe = ":axe:"
        rr = ROLE_ICON[ROLE_LIST.index(self.role)]
        if self.isSupporter():
            return f":black_circle: `{p}` {self.name} {rr}{axe}{t} ({self.owner}) {v}"
        else:
            return f"{GetPowerEmoji(self.power)} `{p}` {self.name} {rr}{axe}{t} ({self.owner}) {v}"

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
        self.cleared = False

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
    
    def isNameExists(self, name):
        for member in self.members:
            if member.name == name:
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

    def isPartyFull(self):
        return len(self.members) == 4
    
    def isCleared(self):
        return self.cleared

    def __repr__(self):
        v = ":o:" if self.cleared else ":x:"
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
    
    def ResetParty(self):
        self.parties = []
        self.leftovers = []
        return interactions.Embed(title="파티를 리셋했습니다", color=0xffffff)

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

    # Generate Parties Based on Enrolled Characters, returns embed
    def PartyGenerate(self, max_power, min_power, priority_power):
        # Reset parties and leftovers
        self.ResetParty()
        self.partyPowerMaxThreshold = max_power
        self.partyPowerMinThreshold = min_power
        self.priorityPower = priority_power
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

        embed = interactions.Embed(description="파티가 결성되었습니다.", color=0xffffff)
        return embed
        
    # Generate Party List as embed
    def PartyList(self, uncleared, owner):
        if len(self.parties) == 0:
            return interactions.Embed(description="결성되어 있는 파티가 없습니다. 관리자에게 문의해 파티결성 명령을 입력해 주세요.", color=0xff0000)
        s = ""
        if uncleared:
            s += "\n클리어되지 않은 파티만 출력합니다."
        if owner != None:
            s += "\n%s님이 있는 파티만 출력합니다."%owner

        embed = interactions.Embed(description="현재 쿠크세이튼 풀에 있는 파티 목록입니다.\n참가가 불가능하거나 파티 멤버 변경이 필요할 경우, 각 파티원들과 직접 조율 바랍니다.%s"%s, color=Color["blue"])
        for v, p in enumerate(self.parties):
            if uncleared and p.isCleared():
                continue
            if owner != None and p.isOwnerExists(owner) == False:
                continue
            stv = "(인원부족)" if len(p.members) < 4 else ""
            embed.add_field(name="파티 %d %s"%((v+1),stv), value="%s"%p, inline=False)
        p = "파티에 소속되지 못한 캐릭터들입니다.\n"
        for i in self.leftovers:
            p += "%s\n"%i
        embed.add_field(name="파티 없음", value="%s"%p, inline=False)
        return embed

    # List of Characters
    def CharacterList(self, owner):
        if owner == None:
            s = ""
            for i in self.characters:
                s += "%s\n"%i
            return interactions.Embed(title="현재 쿠크세이튼 풀에는 캐릭터가 %d개 있습니다."%len(self.characters),description="%s"%s, color=Color["blue"])
        s = ""
        for i in self.characters:
            if i.owner == owner:
                s += "%s\n"%i
        return interactions.Embed(title="%s님의 캐릭터 목록입니다."%owner, description="%s"%s, color=Color["blue"])


    def AddCharacter(self, owner, name, role, ess, power, sup):
        if role not in ROLE_LIST:
            return interactions.Embed(description="직업이 잘못되었습니다.\n\n직업 리스트 : %s"%str(ROLE_LIST), color=Color["red"])
        c = Character(owner, name, role, ess, power, sup)
        # Check if character is already in the list
        if c in self.characters:
            return interactions.Embed(description="이미 존재하는 캐릭터입니다.", color=Color["red"])
        self.characters.append(c)
        s = "캐릭터 %s가 쿠크세이튼 파티 풀에 추가되었습니다."%(c.name)
        if len(self.parties) > 0: # If there is party
            self.leftovers.append(c)
            s += "\n이미 결성된 파티가 있어서, 파티에 소속되지 못한 캐릭터에 추가되었습니다."
        return interactions.Embed(description=s, color=Color["green"])

    def ChangeCharacterInfo(self, name, power, essential, isSupport):
        if power == None and essential == None and isSupport == None:
            return interactions.Embed(description="입력한 값이 없습니다.", color=Color["red"])
        for i in self.characters:
            if i.name == name:
                if power != None:
                    i.power = power
                if essential != None:
                    i.essential = essential
                if isSupport != None:
                    i.isSupportMode = isSupport
                return interactions.Embed(description="캐릭터 %s의 정보가 변경되었습니다.\n%s"%(name,i), color=Color["green"])
        return interactions.Embed(description="존재하지 않는 캐릭터입니다.", color=Color["red"])

    def RemoveCharacter(self, name):
        for c in self.characters:
            if c.name == name:
                self.characters.remove(c)
                return interactions.Embed(description="%s 캐릭터가 쿠크세이튼 파티 풀에서 제거되었습니다. 이미 결성된 파티 및 대기 명단에서는 제거되지 않으며, 다음 파티 매칭때 제거됩니다."%msg[1], color=Color["green"])
        return interactions.Embed(description="존재하지 않는 캐릭터입니다.", color=Color["red"])

    def SetPartyClear(self, number, status):
        if number < 1 or number > len(self.parties):
            return interactions.Embed(description="존재하지 않는 파티 번호입니다.", color=Color["red"])
        if self.parties[number-1].isCleared() == status:
            if status:
                return interactions.Embed(description="이미 클리어된 파티입니다.", color=Color["red"])
            else:
                return interactions.Embed(description="이미 클리어 처리가 안 되어 있는 파티입니다.", color=Color["red"])

        # Check cleared status
        self.parties[number-1].cleared = status
        if status:
            return interactions.Embed(description="파티 %d번 클리어 처리 완료!"%number, color=Color["green"])
        else:
            return interactions.Embed(description="파티 %d번 클리어 처리를 취소했습니다."%number, color=Color["green"])

    def PartyCall(self, ind):
        if ind < 1 or ind > len(self.parties):
            return interactions.Embed(description="존재하지 않는 파티 번호입니다.", color=Color["red"])
        if self.parties[ind-1].isCleared():
            return interactions.Embed(description="이미 클리어된 파티입니다.", color=Color["red"])
        embed = interactions.Embed(title="파티 %d번 호출!"%ind, description="%s"%self.parties[ind-1], color=Color["blue"])
        msg = ""
        for i in self.parties[ind-1].members:
            msg += "%s "%self.pingList[i.owner]
        return msg, embed

    def PartyJoin(self, ind, name):
        info = "\n파티 %d의 정보\n%s"%(ind, self.parties[ind-1])
        if ind < 1 or ind > len(self.parties):
            return interactions.Embed(description="존재하지 않는 파티 번호입니다.", color=Color["red"])
        if self.parties[ind-1].isCleared():
            return interactions.Embed(description="이미 클리어된 파티입니다.\n" + info, color=Color["red"])
        if self.parties[ind-1].isPartyFull():
            return interactions.Embed(description="이미 최대 인원수를 초과했습니다.\n" + info, color=Color["red"])    
        ch = self.GetCharacterByName(name)
        if ch == None:
            return interactions.Embed(description="존재하지 않는 캐릭터입니다.", color=Color["red"])
        info += "입력 캐릭터의 정보\n%s\n"%ch
        if self.parties[ind-1].isOwnerExists(ch.owner):
            return interactions.Embed(description="이미 유저가 해당 파티에 참여중입니다.\n" + info, color=Color["red"])
        if self.parties[ind-1].isNameExists(ch.name):
            return interactions.Embed(description="이미 그 캐릭터는 해당 파티에 있습니다.\n" + info, color=Color["red"])
        if ch in self.leftovers:
            self.leftovers.remove(ch)
            self.parties[ind-1].members.append(ch)
            info = "\n파티 %d의 정보\n%s"%(ind, self.parties[ind-1])
            embed = interactions.Embed(description="캐릭터 %s를 대기 명단에서 제외하고 파티 %d번에 참여시켰습니다.\n"%(ch.name, ind) + info, color=Color["green"])
        else:
            for indk in range(len(self.parties)):
                if ch in self.parties[indk].members:
                    if self.parties[indk].isCleared():   
                        info = "\n파티 %d의 정보\n%s"%(indk+1, self.parties[indk])
                        info += "입력 캐릭터의 정보\n%s\n"%ch 
                        return interactions.Embed(description="이미 클리어된 파티에 있습니다.\n" + info, color=Color["red"])
                    self.parties[indk].members.remove(ch)
                    break
            self.parties[ind-1].members.append(ch)
            info = "\n파티 %d의 정보\n%s"%(ind, self.parties[ind-1])
            info += "\n파티 %d의 정보\n%s"%(indk+1, self.parties[indk])
            embed = interactions.Embed(description="캐릭터 %s를 파티 %d번에서 파티 %d번으로 이동시켰습니다.\n"%(ch.name, indk+1, ind)+info, color=Color["green"])
        
        return embed
    
    def PartyLeave(self, name):
        ch = self.GetCharacterByName(name)
        if ch == None:
            return interactions.Embed(description="존재하지 않는 캐릭터입니다.", color=Color["red"])
        if ch in self.leftovers:
            return interactions.Embed(description="이미 대기 명단에 있는 캐릭터입니다.", color=Color["red"])
        for ind in range(len(self.parties)):
            if ch in self.parties[ind].members:
                if self.parties[ind].isCleared():
                    return interactions.Embed(description="이미 클리어된 파티입니다.", color=Color["red"])
                self.parties[ind].members.remove(ch)
                break
        info = "\n파티 %d의 정보\n%s"%(ind+1, self.parties[ind])
        self.leftovers.append(ch)
        return interactions.Embed(description="캐릭터 %s를 파티에서 제거하고 대기 명단으로 이동시켰습니다.\n"%ch.name + info, color=Color["green"])



    
    def _PartyLeave(self, ch):
        if ch in self.leftovers:
            return False
        for ind in range(len(self.parties)):
            if ch in self.parties[ind].members:
                if self.parties[ind].isCleared():
                    return False
                self.parties[ind].members.remove(ch)                
                break
        self.leftovers.append(ch)
        return True

    def _PartyJoin(self, ind, ch):
        if ind < 1 or ind > len(self.parties):
            return False
        if self.parties[ind].isCleared():
            return False
        if self.parties[ind].isPartyFull():
            return False  
        if self.parties[ind].isOwnerExists(ch.owner):
            return False
        if self.parties[ind].isNameExists(ch.name):
            return False
        self.leftovers.remove(ch)
        self.parties[ind].members.append(ch)
        return True
    
    def _Info(self, c1, c2, ind1, ind2):
        info = "\n"
        if c1 not in self.leftovers:
            info += "\n파티 %d의 정보\n%s"%(ind1+1, self.parties[ind1])
        if c2 not in self.leftovers:
            info += "\n파티 %d의 정보\n%s"%(ind2+1, self.parties[ind2])
        if c1 in self.leftovers or c2 in self.leftovers:
            info += "\n대기 명단에 있는 캐릭터\n"
            for i in self.leftovers:
                info += str(i) + "\n"
        return info

    def PartySwap(self, name1, name2):
        c1 = self.GetCharacterByName(name1)
        c2 = self.GetCharacterByName(name2)
        if c1 == None or c2 == None:
            return interactions.Embed(description="존재하지 않는 캐릭터입니다.", color=Color["red"])
        for ind1 in range(len(self.parties)):
            if c1 in self.parties[ind1].members:
                break
        for ind2 in range(len(self.parties)):
            if c2 in self.parties[ind2].members:
                break
        if c1 == c2:
            return interactions.Embed(description="같은 캐릭터입니다.", color=Color["red"])
        if c1 in self.leftovers and c2 in self.leftovers:
            return interactions.Embed(description="둘 다 대기 명단에 있는 캐릭터입니다.", color=Color["red"])
        if c1 in self.leftovers:
            v1 = self._PartyLeave(c2)
            v2 = self._PartyJoin(ind2, c1)
            if v1 and v2:
                
                return interactions.Embed(description="캐릭터 %s를 파티에 참여시키고 %s를 대기 명단으로 보냈습니다."%(c1.name, c2.name) + self._Info(c1, c2, ind1, ind2), color=Color["green"])
            else:
                self._PartyLeave(c1)
                self._PartyJoin(ind2, c2)
                return interactions.Embed(description="두 캐릭터의 위치를 바꾸는 데 실패했습니다." + self._Info(c1, c2, ind1, ind2), color=Color["red"])
        elif c2 in self.leftovers:
            v1 = self._PartyLeave(c1)
            v2 = self._PartyJoin(ind1, c2)
            if v1 and v2:
                return interactions.Embed(description="캐릭터 %s를 파티에 참여시키고 %s를 대기 명단으로 보냈습니다."%(c2.name, c1.name) + self._Info(c1, c2, ind1, ind2), color=Color["green"])
            else:
                self._PartyLeave(c2)
                self._PartyJoin(ind1, c1)
                return interactions.Embed(description="두 캐릭터의 위치를 바꾸는 데 실패했습니다." + self._Info(c1, c2, ind1, ind2), color=Color["red"])
        else:
            v1 = self._PartyLeave(c1)
            v1 = self._PartyLeave(c2)
            v3 = self._PartyJoin(ind1, c2)
            v2 = self._PartyJoin(ind2, c1)
            if v1 and v2 and v3:
                return interactions.Embed(description="캐릭터 %s와 %s의 위치를 바꿨습니다."%(c1.name, c2.name) + self._Info(c1, c2, ind1, ind2), color=Color["green"])
            else:
                self._PartyLeave(c1)
                self._PartyLeave(c2)
                self._PartyJoin(ind2, c2)
                self._PartyJoin(ind1, c1)
                return interactions.Embed(description="두 캐릭터의 위치를 바꾸는 데 실패했습니다." + self._Info(c1, c2, ind1, ind2), color=Color["red"])