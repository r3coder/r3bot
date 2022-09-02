
import random
import interactions
import time

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

# print and save to the file
def printl(text, end="\n"):
    print(text, end="\n")
    with open("logs/log.txt", "a") as f:
        f.write(text + end)
    return

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
        v = ":no_entry_sign:" if not self.essential else ""
        axe = ""
        t = ""
        p = self.power if not self.isSupporter() else "   "
        if self.role in ["홀리나이트(딜폿)", "바드(딜폿)", "도화가(딜폿)"]:
            axe = ":axe:"
            t = "`%3.1f`"%self.power
        rr = ROLE_ICON[ROLE_LIST.index(self.role)]
        if self.isSupporter():
            return f":fuelpump: `{p}` {self.name} {rr}{axe} ({self.owner}) {v} {t}"
        else:
            return f"{GetPowerEmoji(self.power)} `{p}` {self.name} {rr}{axe} ({self.owner}) {v}"

    def GetPower(self, dp = False):
        if dp:
            return 0 if self.role in ["홀리나이트(폿)", "바드(폿)", "도화가(폿)"] else self.power
        return 0.0 if self.isSupporter() else self.power
    
    def isSupporter(self):
        return True if self.role in ["홀리나이트(폿)", "바드(폿)", "도화가(폿)"] or self.isSupportMode else False
    
    def isRoleSupporter(self):
        return True if self.role in ["홀리나이트(폿)", "바드(폿)", "도화가(폿)"] else False
    
    def isBoth(self):
        return True if self.role in ["홀리나이트(딜폿)", "바드(딜폿)", "도화가(딜폿)"] else False
    
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

    def isSupporterExists(self):
        for member in self.members:
            if member.isSupporter():
                return True
        return False

    def GetPartyPower(self):
        f = 0
        for member in self.members:
            f += member.GetPower()
        return f

    def isSupporterExists(self):
        for member in self.members:
            if member.isSupporter():
                return True
        return False

    def AddCharacter(self, member):
        if len(self.members) < 4 and not self.isNameExists(member.name) and not self.isOwnerExists(member.owner):
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
        s = "인원:%d/4, 딜량:%2.2f, 클리어:%s\n"%(len(self.members), self.GetPartyPower(), v)
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
        self.assigned = {}

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


    # Generate Parties Based on Enrolled Characters, returns embed
    def PartyGenerate(self, power_party_min = 3.0, power_party_max = 5.0, power_priority = -1, owner_priority = -1):
        # Reset parties and leftovers
        self.ResetParty()

        # Reset all dealer/supporter to supporter, reset party status
        for character in self.characters:
            if character.isBoth():
                character.isSupportMode = True

        ### main Party making Logic ###
        # Count essential characters that is required to be included in a party
        essentialCharcterCount = 0
        for ch in self.characters:
            if ch.essential:
                essentialCharcterCount += 1

        # Return nothing if there is no characters
        if essentialCharcterCount < 1:
            return
        
        # If there is less then 4 people, make one party
        if essentialCharcterCount <= 4:
            self.parties.append(Party())
            for character in self.characters:
                self.parties[-1].AddCharacter(character)
            return

        # Create number of parties 
        partyCount = essentialCharcterCount//4+1
        for i in range(partyCount):
            self.parties.append(Party())
        
        for character in self.characters:
            self.assigned[character.name] = False

        def GetOwnerNotAssigned():
            res = {}
            for character in self.characters:
                if not self.assigned[character.name] and character.essential:
                    if character.owner not in res:
                        res[character.owner] = 0
                    res[character.owner] += 1
            res = sorted(res.items(), key=lambda x: x[1], reverse=True)

            # Suffle order between value within same elements 
            lst = []
            for v in range(res[0][1]):
                lst.append(list())
            lst.append(list())
            for key, value in res:
                lst[value].append(key)
            for i in lst:
                random.shuffle(i)
            res_ = {}
            for ind in range(len(lst)):
                for key in lst[len(lst)-ind-1]:
                    res_[key] = len(lst)-ind-1
            return res_

        def GetOwnerDealerPower():
            res = {}
            for character in self.characters:
                if not self.assigned[character.name]:
                    if character.owner not in res:
                        res[character.owner] = 0
                    res[character.owner] += character.GetPower()
            res = sorted(res.items(), key=lambda x: x[1], reverse=True)
            return res

        def GetMaximumGroup(res):
            for min_num in range(len(res)):
                cnt = 0
                for key, value in res.items():
                    if min_num <= value:
                        cnt += 1
                if cnt < min_num:
                    return min_num - 1

        def GetNumOwnersWithMoreThan(res, val):
            cnt = 0
            for key, value in res.items():
                if val <= value:
                    cnt += 1
            return cnt

        def SupNumberFromOwner(name):
            cnt = 0
            for character in self.characters:
                if not self.assigned[character.name] and character.owner == name and character.isSupporter():
                    cnt += 1
            return cnt

        # Create each member list
        supporters, dealers, leftovers = [], [], []
        for character in self.characters:
            if character.essential:
                if character.isSupporter():
                    supporters.append(character)
                else:
                    dealers.append(character)
            else:
                leftovers.append(character)

        printl("\n"*5)
        printl("Start party generation: %s"%str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
        
        ##################################################
        printl("===== Phase 1 =====")
        printl("Balancing between supporters and dealers")
        printl("supporters: %d, dealers: %d, leftovers: %d, parties: %d"%(len(supporters), len(dealers), len(leftovers), len(self.parties)))
        # Compare number of supporters
        if len(supporters) == len(self.parties):
            printl("Perfect Balance")
        elif len(supporters) > len(self.parties):
            printl("Too many supporters, changing deal/sup to supporters")
            boths = []
            for character in supporters:
                if character.isBoth():
                    boths.append(character)
            if len(boths) > 0:
                boths.sort(key=lambda x:x.power) # Change both to dealer by strongest
                for character in both:
                    printl("Changing %s to dealer"%character.name)
                    character.isSupportMode = False
                    supporters.remove(character)
                    dealers.append(character)
                    if len(supporters) == len(self.parties):
                        printl("Enough Supporters are changed to dealer")
                        break
                if len(supporters) > len(self.parties):
                    printl("Converted all deal/sups to deal, but too many supporters, some party will contain more than 1 supporters...")
            else:
                printl("There's no deal/sup on characters, some party will contain more than 1 supporters...")
        else:
            printl("Supports are not enough, finding additional supporters from leftovers...")
            dellist = []
            for char in leftovers:
                if char.isSupporter():
                    dellist.append(char)
                    supporters.append(char)
                    if len(supporters) == len(self.parties):
                        printl("Enough Supporters are found, quiting...")
                        break
            for char in dellist:
                leftovers.remove(char)
            if len(supporters) < len(self.parties):
                printl("Still lack of supporters, some parties will have no supporters :(")
        printl("Balancing complete!")
        printl("supporters: %d, dealers: %d, leftovers: %d, parties: %d"%(len(supporters), len(dealers), len(leftovers), len(self.parties)))

        powerTotal = 0
        for character in dealers:
            powerTotal += character.GetPower()
        powerAvg = powerTotal/len(self.parties)
        printl("Total power: %5.1f, Average power per party: %6.2f"%(powerTotal, powerAvg))
        
        def AssignGroups(partyInd, groupSize):
            ownerNA = GetOwnerNotAssigned()
            pgOwners = []
            for key, value in ownerNA.items():
                pgOwners.append(key)

            supCnt, dealCnt = 0, 0
            for char in supporters:
                if char.owner in pgOwners:
                    supCnt += 1
            for char in dealers:
                if char.owner in pgOwners:
                    dealCnt += 1
            if supCnt < groupSize:
                printl("Not enough supporters, quiting...")
                return False
            if dealCnt < groupSize * 3:
                printl("Not enough dealers, quiting...")
                return False
            
            pgOwners = pgOwners[:4]
            printl("Making %d parties with %s"%(groupSize, str(pgOwners)))
            # Count nubmer of supporters from pgOwners
            sups = []
            random.shuffle(supporters)
            for char in supporters:
                if char.owner in pgOwners and not self.assigned[char.name]:
                    sups.append(char)
                    if len(sups) == groupSize:
                        break
            deals = []
            for char in dealers:
                if char.owner in pgOwners and not self.assigned[char.name]:
                    deals.append(char)

            if len(sups) < groupSize:
                printl("Not enough supporters, quiting...")
                return False
            if len(deals) < groupSize * 3:
                printl("Not enough dealers, quiting...")
                return False

            # Assign Supporters
            for ind in range(partyInd, partyInd + groupSize):
                self.parties[ind].AddCharacter(sups[ind - partyInd])
                self.assigned[sups[ind - partyInd].name] = True
                printl(" - Assigned %s to party %d"%(sups[ind - partyInd].name, ind))
            printl("Assiging Strong Dealers")
            deals = sorted(deals, key=lambda x:x.power, reverse=True)
            for char in deals:
                if not self.assigned[char.name]:
                    for pind in range(partyInd, partyInd + groupSize):
                        if char.power + self.parties[pind].GetPartyPower() < powerAvg - 1.5:
                            if self.parties[pind].AddCharacter(char):
                                self.assigned[char.name] = True
                                printl(" - Assigned %s to party %d"%(char.name, pind))
                                break

            printl("Fill rest dealers without power condition")
            deals = sorted(deals, key=lambda x:x.power)
            for char in deals:
                if not self.assigned[char.name]:
                    for pind in range(partyInd, partyInd + groupSize):
                        if self.parties[pind].AddCharacter(char):
                            self.assigned[char.name] = True
                            printl(" - Assigned %s to party %d"%(char.name, pind))
                            break
            return True

        ##################################################
        printl("===== Phase 2 =====")
        printl("Assign 4 parties with 4 owners with 4 characters each")
        group4 = 0
        partyInd = 0
        while GetMaximumGroup(GetOwnerNotAssigned()) >= 4:
            if AssignGroups(partyInd, 4):
                partyInd += 4
                group4 += 1
            else:
                break

        ##################################################
        printl("===== Phase 3 =====")
        printl("Assign 2 parties with 4 owners with 2 characters each")     
        group2 = 0   
        while GetNumOwnersWithMoreThan(GetOwnerNotAssigned(), 2) >= 4:
            if AssignGroups(partyInd, 2):
                partyInd += 2
                group2 += 1 
            else:
                break

        ##################################################
        printl("===== Phase 4 =====")
        printl("Assign rest supporters and dealers")
        for char in supporters:
            if not self.assigned[char.name]:
                for pind in range(partyInd, len(self.parties)):
                    if not self.parties[pind].isSupporterExists():
                        self.parties[pind].AddCharacter(char)
                        self.assigned[char.name] = True
                        printl(" - Assigned %s to party %d"%(char.name, pind))
                        break
        
        dealers = sorted(dealers, key=lambda x:x.power, reverse=True)
        for char in dealers:
            if not self.assigned[char.name]:
                for pind in range(partyInd, len(self.parties)):
                    if char.power + self.parties[pind].GetPartyPower() < powerAvg - 1.5:
                        if self.parties[pind].AddCharacter(char):
                            self.assigned[char.name] = True
                            printl(" - Assigned %s to party %d"%(char.name, pind))
                            break

        dealers = sorted(dealers, key=lambda x:x.power)
        for char in dealers:
            if not self.assigned[char.name]:
                for pind in range(partyInd, len(self.parties)):
                    if self.parties[pind].AddCharacter(char):
                        self.assigned[char.name] = True
                        printl(" - Assigned %s to party %d"%(char.name, pind))
                        break

        for char in supporters:
            if not self.assigned[char.name]:
                leftovers.append(char)
        for char in dealers:
            if not self.assigned[char.name]:
                leftovers.append(char)

        ##################################################
        printl("===== Phase 5 =====")
        printl("Assign leftovers")
        for char in leftovers:
            if not self.assigned[char.name]:
                for pind in range(0, len(self.parties)):
                    if self.parties[pind].AddCharacter(char):
                        self.assigned[char.name] = True
                        printl(" - Assigned %s to party %d"%(char.name, pind))
                        break

        for char in leftovers:
            if not self.assigned[char.name]:
                self.leftovers.append(char)
        printl(str(self.leftovers))
        # self.parties.sort(key=lambda x:x.GetPartyPower())
        embed = interactions.Embed(description="%d개의 파티가 결성되었습니다.\n 파티의 평균 딜은 %4.2f입니다.\n4연 그룹 %d개, 2연 그룹 %d개 만들어졌습니다."%(len(self.parties), powerAvg, group4, group2), color=0xffffff)
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
        self.characters = sorted(self.characters, key=lambda x:x.GetPower(True), reverse=True)
        if owner == None:
            s = ""
            for i in self.characters:
                s += "%s\n"%i
            return interactions.Embed(title="현재 쿠크세이튼 풀에는 캐릭터가 %d개 있습니다."%len(self.characters),description="%s"%s, color=Color["blue"])
        s = ""
        cnt_e, tot_e, cnt_t, tot_t = 0, 0, 0, 0
        for i in self.characters:
            if i.owner == owner:
                s += "%s\n"%i
                if not i.isSupporter():
                    if i.essential:
                        cnt_e += 1
                        tot_e += i.GetPower()
                    cnt_t += 1
                    tot_t += i.GetPower()
        return interactions.Embed(title="%s님의 캐릭터 목록입니다."%(owner), description="딜러의 평균딜량: %4.2f (%4.2f) \n%s"%(tot_e/cnt_e, tot_t/cnt_t, s), color=Color["blue"])

    def AddCharacter(self, owner, name, role, ess=True, power=1.0, sup=None):
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
            return "", interactions.Embed(description="존재하지 않는 파티 번호입니다.", color=Color["red"])
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