#-*- coding:utf-8 -*-
import interactions

from ..kakul.character import Character
from ..kakul.user import User
from ..kakul.loainfo import GetApproxStrength
from ..kakul.utils import *


def KPMPartyGenerate(kpm, sample_steps=1024, optimize_steps=256, weight_power=2, weight_group=0.25, weight_duperole=1):
    printl("KPMGenerateParty")
    param = dict()
    param["sample_steps"] = sample_steps
    param["optimize_steps"] = optimize_steps
    param["weight_power"] = weight_power
    param["weight_group"] = weight_group
    param["weight_duperole"] = weight_duperole
    sco = kpm.GeneratePartyV3(param, verbose = False)
    KPMSave(kpm)
    return interactions.Embed(description="%d개의 큐브를 관측하고, 최선의 결과를 찾았습니다.\n최종 점수 : %s"%(param["sample_steps"], sco), color=Color["white"])

def KPMResetParty(kpm):
    printl("KPMResetParty")
    kpm.ResetParty()
    KPMSave(kpm)
    return interactions.Embed(description="파티가 성공적으로 초기화되었습니다.", color=Color["white"])

def KPMCallEveryBody(kpm):
    printl("KPMCallEveryBody")
    lst = []
    for party in kpm.parties:
        for char in party.members:
            lst.append(char.owner)
    lst = list(set(lst))
    msg = ""
    for user in kpm.users:
        if user.name in lst:
            msg += "%s "%user.ping
    return msg
    
def KPMPartyList(kpm, uncleared=True, owner=None):
    printl("KPMPartyList")
    if len(kpm.parties) == 0:
        return interactions.Embed(description="결성되어 있는 파티가 없습니다. 관리자에게 문의해 파티결성 명령을 입력해 주세요.", color=0xff0000)
        
    kpm.Validate()
    s = ""
    if uncleared:
        s += "\n클리어되지 않은 파티만 출력합니다."
    if owner != None:
        s += "\n%s님이 있는 파티만 출력합니다."%owner

    embed = interactions.Embed(description="현재 쿠크세이튼 풀에 있는 파티 목록입니다.\n여기서만 쿠크세이튼이 %d마리 죽고, %d 골드가 생깁니다...\n참가가 불가능하거나 파티 멤버 변경이 필요할 경우, 각 파티원들과 직접 조율 바랍니다.%s"%(len(kpm.parties), len(kpm.parties)*4500*4, s), color=Color["blue"])

    ggs = dict()

    for ind in range(len(kpm.parties)):
        key = kpm.parties[ind].GetPartyOwnerString()
        if key in ggs:
            ggs[key].append(ind)
        else:
            ggs[key] = [ind]

    gind = 0
    for key in ggs:
        gind += 1
        pps = []
        for ind in ggs[key]:
            if kpm.parties[ind].cleared and uncleared:
                continue
            if owner != None and owner not in key:
                continue
            pps.append(kpm.parties[ind])
        if len(pps) == 0:
            continue
        val, val2 = "", ""
        for p in pps:
            ln = "%s\n"%(p.ShortStr())
            if len(val) + len(val2) + len(ln) > 1000:
                val2 += "%s\n"%(p.ShortStr())
            else:
                val += "%s\n"%(p.ShortStr())
        vv = " %d연공"%len(pps) if len(pps) > 1 else " "
        tt = " " + pps[0].daytime
        embed.add_field(name="그룹 %d [%s]%s%s"%(gind, key, vv, tt), value=val, inline=False)
        if val2 != "":
            embed.add_field(name="===", value=val2, inline=False)

    if len(kpm.leftovers) > 0:
        v = ""
        for char in kpm.leftovers:
            v += "%s,  "%char.StrOwner()
        v = v[:-2]
        embed.add_field(name="예비 인원", value=v, inline=False)
    v = ""
    for key in kpm.users:
        if key.active == False:
            v += key.name + ", "
    v = v[:-2]
    if v != "":
        embed.add_field(name="배정을 중지한 유저들", value=v, inline=False)
    return embed

def KPMCharacterList(kpm, owner, summary, sort=True):
    printl("KPMCharacterList")
    kpm.Validate()
    if sort:
        embed = interactions.Embed(title = "캐릭터 목록", description = "총 %d개의 캐릭터가 있습니다."%len(kpm.characters), color=Color["blue"])
        for user in kpm.users:
            s = ""
            cnt_plu, cnt_ess, cnt_non = 0, 0, 0
            cnt_plu_sup, cnt_ess_sup, cnt_non_sup = 0, 0, 0
            cn, cna = 0, 0
            for char in kpm.characters:
                if owner != None and char.owner != owner:
                    continue
                if char.owner == user.name:
                    if summary:
                        s += "%s, "%(char.GetIcon() + char.name + char.GetIconStatus())
                    else:
                        s += "%s\n"%char.StrFull()
                    
                    
                    if char.isSupporter():
                        if char.active and char.essential:
                            cnt_ess_sup += 1
                        if not char.essential:
                            cnt_plu_sup += 1
                        if not char.active:
                            cnt_non_sup += 1
                    else:
                        if char.active and char.essential:
                            cnt_ess += 1
                        if not char.essential:
                            cnt_plu += 1
                        if not char.active:
                            cnt_non += 1

            if s != "":
                if summary:
                    s = s[:-2]
                nm = "`%s`의 캐릭터"%user.name
                if user.active == False:
                    nm += ", 배정 중지됨"
                else:
                    if cnt_plu + cnt_plu_sup > 0:
                        nm += ", 딜러 %d(+%d), 서폿 %d(+%d)"%(cnt_ess, cnt_plu, cnt_ess_sup, cnt_plu_sup)
                    else:
                        nm += ", 딜러 %d, 서폿 %d"%(cnt_ess, cnt_ess_sup)
                    if cnt_non + cnt_non_sup > 0:
                        nm += ", 비활성 %d"%(cnt_non + cnt_non_sup)
                if user.avoiddays != "":
                    nm += ", 기피요일: %s"%user.avoiddays
                embed.add_field(name=nm, value=s, inline=False)
        return embed
    else:
        s = ""
        for char in kpm.characters:
            if owner != None and char.owner != owner:
                continue
            if summary:
                s += "%s,"%char.name
            else:
                s += "%s\n"%char.StrFull()
        if summary:
            s = s[:-2]
        embed = interactions.Embed(title = "캐릭터 목록",description = s, color=Color["blue"])
        return embed

def KPMAddCharacter(kpm, name, role, user, ping, essential=True):
    printl(f"KPMAddCharacter({name}, {role}, {user}, {essential})")
    if not isinstance(name, str):
        return interactions.Embed(description="이름이 잘못되었습니다", color=Color["red"])
    if role not in ROLE_LIST:
        return interactions.Embed(description="직업이 잘못되었습니다.\n\n직업 리스트 : %s"%str(ROLE_LIST), color=Color["red"])
    if not isinstance(user, str):
        return interactions.Embed(description="유저는 String이어야 합니다.", color=Color["red"])
    content = ""
    try:
        power = GetApproxStrength(name) / 30000
        content = "전투정보실에서 캐릭터의 세기를 불러왔습니다."
    except:
        power = 1.0
        content = "전투정보실에서 캐릭터의 세기를 불러오는데 실패했습니다."
    c = Character(user, name, role, power, essential)
    res = kpm.AddCharacter(c)
    # Add User if not exists
    addUser = True
    for u in kpm.users:
        if u.name == user:
            addUser = False
            break
    if addUser:
        u = User(user, ping, True, "")
        kpm.users.append(u)
    KPMSave(kpm)
    if res:
        return interactions.Embed(description="성공적으로 추가되었습니다.\n%s"%content, color=Color["green"])
    else:
        return interactions.Embed(description="캐릭터를 추가하는데 실패했습니다.", color=Color["red"])

def KPMEditCharacter(kpm, name, is_essential=None, is_support=None):
    if not isinstance(name, str):
        return interactions.Embed(description="이름이 잘못되었습니다", color=Color["red"])
    res = kpm.EditCharacter(name, is_essential, is_support)
    KPMSave(kpm)
    if res:
        return interactions.Embed(description="성공적으로 수정되었습니다.\n%s"%kpm.GetCharacterByName(name).StrFull(), color=Color["green"])
    else:
        return interactions.Embed(description="캐릭터를 수정하는데 실패했습니다.", color=Color["red"])

def KPMUpdateCharacter(kpm, name = None, force = False):
    printl(f"KPMUpdateCharacter({name}, {force})")
    kpm.UpdateStrength(name, force)
    KPMSave(kpm)
    if name == None:
        return interactions.Embed(description="캐릭터들의 정보가 업데이트되었습니다.", color=Color["white"])
    else:
        return interactions.Embed(description="캐릭터 %s의 정보가 업데이트되었습니다."%name, color=Color["white"])

def KPMRemoveCharacter(kpm, name):
    printl(f"KPMRemoveCharacter({name})")
    if not isinstance(name, str):
        return interactions.Embed(description="이름이 잘못되었습니다", color=Color["red"])
    res = kpm.RemoveCharacterbyName(name)
    KPMSave(kpm)
    if res:
        return interactions.Embed(description="%s 캐릭터가 성공적으로 제거되었습니다."%name, color=Color["green"])
    else:
        return interactions.Embed(description="캐릭터를 제거하는데 실패했습니다.", color=Color["red"])

def KPMSetPartyClearState(kpm, index, state):
    printl(f"KPMSetPartyClearState({index}, {state})")
    if not isinstance(index, int) or index <= 0 or index > len(kpm.parties):
        return interactions.Embed(description="파티 번호가 잘못되었습니다", color=Color["red"])
    if not isinstance(state, bool):
        return interactions.Embed(description="상태가 잘못되었습니다", color=Color["red"])
    kpm.SetPartyClearState(index - 1, state)
    KPMSave(kpm)
    if state:
        return interactions.Embed(description="파티 %s 클리어!"%index, color=Color["green"])
    else:
        return interactions.Embed(description="파티 %s 클리어 취소!"%index, color=Color["red"])

def KPMPartyCall(kpm, index):
    printl(f"KPMPartyCall({index})")
    if not isinstance(index, int) or index < 1 or index > len(kpm.parties):
        return "", interactions.Embed(description="파티 번호가 잘못되었습니다", color=Color["red"])
    msg = ""
    for mem in kpm.parties[index - 1].members:
        msg += "%s "%kpm.GetUserByName(mem.owner).ping
    return msg, interactions.Embed(description="파티 %d 호출\n%s"%(index, kpm.parties[index - 1].StrFull()), color=Color["white"])

def KPMPartyJoin(kpm, index, name):
    printl(f"KPMPartyJoin({index}, {name})")
    if not isinstance(index, int) or index <= 0 or index > len(kpm.parties):
        return interactions.Embed(description="파티 번호가 잘못되었습니다", color=Color["red"])
    if kpm.GetCharacterByName(name) is None:
        return interactions.Embed(description="캐릭터 %s가 존재하지 않습니다"%name, color=Color["red"])
    res = kpm.AddCharacterToParty(kpm.GetCharacterByName(name), index - 1)
    KPMSave(kpm)
    if res:
        return interactions.Embed(description="%s 캐릭터가 %d번 파티에 성공적으로 참가되었습니다."%(name, index), color=Color["green"])
    else:
        return interactions.Embed(description="%s 캐릭터를 파티에 추가하는데 실패했습니다."%name, color=Color["red"])

def KPMPartyLeave(kpm, name):
    printl(f"KPMPartyLeave({name})")
    if kpm.GetCharacterByName(name) is None:
        return interactions.Embed(description="캐릭터 %s가 존재하지 않습니다"%name, color=Color["red"])
    res = kpm.RemoveCharacterFromParty(kpm.GetCharacterByName(name))
    KPMSave(kpm)
    if res:
        return interactions.Embed(description="%s 캐릭터가 성공적으로 파티에서 제거되었습니다."%name, color=Color["green"])
    else:
        return interactions.Embed(description="%s 캐릭터를 파티에서 제거하는데 실패했습니다."%name, color=Color["red"])

def KPMPartySwap(kpm, name1, name2):
    printl(f"KPMPartySwap({name1}, {name2})")
    if kpm.GetCharacterByName(name1) is None:
        return interactions.Embed(description="캐릭터 %s가 존재하지 않습니다"%name1, color=Color["red"])
    if kpm.GetCharacterByName(name2) is None:
        return interactions.Embed(description="캐릭터 %s가 존재하지 않습니다"%name2, color=Color["red"])
    res = kpm.ReplaceCharacters(kpm.GetCharacterByName(name1), kpm.GetCharacterByName(name2))
    KPMSave(kpm)
    if res:
        return interactions.Embed(description="%s 캐릭터와 %s 캐릭터가 성공적으로 교체되었습니다."%(name1, name2), color=Color["green"])
    else:
        return interactions.Embed(description="%s 캐릭터와 %s 캐릭터를 교체하는데 실패했습니다."%(name1, name2), color=Color["red"])

def KPMPartyAdd(kpm):
    printl(f"KPMPartyAdd()")
    res = kpm.AddEmptyParty()
    KPMSave(kpm)
    if res:
        return interactions.Embed(description="빈 파티를 추가했습니다", color=Color["green"])
    else:
        return interactions.Embed(description="빈 파티를 추가하는데 실패했습니다", color=Color["red"])

def KPMPartyEditTime(kpm, index, time):
    if not isinstance(index, int) or index <= 0 or index > len(kpm.parties):
        return interactions.Embed(description="파티 번호가 잘못되었습니다", color=Color["red"])
    if time[0] not in ["월", "화", "수", "목", "금", "토", "일"]:
        return interactions.Embed(description="요일이 잘못되었습니다. 양식: (요일 시:분) ex) 월 22:00", color=Color["red"])
    try:
        h, m = int(time[2:4]), int(time[5:7])
    except:
        return interactions.Embed(description="시간이 잘못되었습니다 양식: (요일 시:분) ex) 월 22:00", color=Color["red"])
    printl(f"KPMPartyEditTime({index}, {time})")
    kpm.EditPartyTime(index - 1, time)
    KPMSave(kpm)
    return interactions.Embed(description="%d번 파티의 시간이 %s로 변경되었습니다."%(index, time), color=Color["green"])

def KPMUserActive(kpm, user, state):
    printl(f"KPMUserActive({user}, {state})")
    if not isinstance(state, bool):
        return interactions.Embed(description="상태가 잘못되었습니다", color=Color["red"])
    res = kpm.SetUserActive(user, state)
    KPMSave(kpm)
    if res:
        return interactions.Embed(description="%s를 파티 배정에서 %s."%(user, "포함시켰습니다" if state else "제외시켰습니다"), color=Color["green"])
    else:
        return interactions.Embed(description="유저 배정 상태 변경에 실패했습니다.", color=Color["red"])


def KPMUserSetAvoidDays(kpm, owner, avoiddays):
    printl(f"KPMUserSetAvoidDays({owner}, {avoiddays})")
    if len(avoiddays) > 3:
        return interactions.Embed(description="요일은 3개까지만 설정할 수 있습니다", color=Color["red"])
    for stri in avoiddays:
        if stri not in ["월", "화", "수", "목", "금", "토", "일"]:
            return interactions.Embed(description="요일이 잘못되었습니다", color=Color["red"])
    res = kpm.SetUserAvoidDays(owner, avoiddays)
    KPMSave(kpm)
    if res:
        return interactions.Embed(description="%s의 기피 요일을 '%s'요일로 설정했습니다."%(owner, avoiddays), color=Color["green"])
    else:
        return interactions.Embed(description="기피 요일 설정에 실패했습니다.", color=Color["red"])
        

def KPMCharacterActive(kpm, character, state):
    printl(f"KPMCharacterActive({character}, {state})")
    if not isinstance(state, bool):
        return interactions.Embed(description="상태가 잘못되었습니다", color=Color["red"])
    res = kpm.SetCharacterActive(character, state)
    KPMSave(kpm)
    if res:
        return interactions.Embed(description="%s를 파티 배정에서 %s."%(character, "포함시켰습니다" if state else "제외시켰습니다"), color=Color["green"])
    else:
        return interactions.Embed(description="캐릭터 배정 상태 변경에 실패했습니다.", color=Color["red"])

def KPMCharacterEssential(kpm, character, state):
    printl(f"KPMCharacterEssential({character}, {state})")
    if not isinstance(state, bool):
        return interactions.Embed(description="상태가 잘못되었습니다", color=Color["red"])
    res = kpm.SetCharacterEssential(character, state)
    KPMSave(kpm)
    if res:
        return interactions.Embed(description="%s를 파티 배정에서 %s."%(character, "필수로 설정했습니다" if state else "필수로 설정하지 않았습니다"), color=Color["green"])
    else:
        return interactions.Embed(description="캐릭터 필수 설정 변경에 실패했습니다.", color=Color["red"])
    

def KPMRecalculateTime(kpm):
    printl(f"KPMRecalculateTime()")
    kpm.RecalculateTime()
    KPMSave(kpm)
    return interactions.Embed(description="파티 시간을 재배정했습니다", color=Color["green"])
    