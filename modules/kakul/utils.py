#-*- coding:utf-8 -*-

import time
import datetime
def Now():
    now = datetime.datetime.now() + datetime.timedelta(hours=9)
    return now

file_path = "logs/log_" + Now().strftime("%Y%m%d_%H%M%S") + ".txt"

def printl(text, end="\n"):
    # Current time as YYYY/MM/DD HH:MM:SS
    timeT = Now().strftime("[%Y/%m/%d %H:%M:%S] ")
    print(timeT + text, end="\n")
    with open(file_path, "a") as f:
        f.write(timeT + text + end)
    return

def GetRoleRaw(role):
    return role.replace("(딜)", "").replace("(폿)", "").replace("(딜폿)", "")


ROLE_LIST = ["디스트로이어", "버서커", "워로드", "홀리나이트(딜)", "홀리나이트(폿)", "홀리나이트(딜폿)", "기공사", "배틀마스터", "스트라이커", "인파이터", "창술사", "건슬링어", "데빌헌터", "블래스터", "스카우터", "호크아이", "바드(딜)", "바드(폿)", "바드(딜폿)", "서머너", "소서리스", "아르카나", "도화가(딜)", "도화가(폿)", "도화가(딜폿)", "리퍼", "블레이드", "데모닉", "기상술사", "슬레이어"]

ROLE_SUP = ["홀리나이트(폿)", "바드(폿)", "도화가(폿)"]

ROLE_SUP_BOTH = ["홀리나이트(딜폿)", "바드(딜폿)", "도화가(딜폿)"]

ROLE_ICON = ["<:loa_destroyer:1009187088798863380>", "<:loa_berserker:1009187084029935717>", "<:loa_gunlancer:1009187095702671380>", "<:loa_paladin:1009187101264314460>", "<:loa_paladin:1009187101264314460>", "<:loa_paladin:1009187101264314460>", "<:loa_soulfist:1009187110508560534>", "<:loa_wardancer:1009187116594511933>", "<:loa_striker:1009187112505069669>", "<:loa_scrapper:1009187104464576632>", "<:loa_glaivier:1009187093794275409>", "<:loa_gunslinger:1009187097556566088>", "<:loa_deadeye:1009187085611188244>", "<:loa_artillerist:1009187080468967476>", "<:loa_machinist:1009187099213307976>", "<:loa_sharpshooter:1009187107257987082>", "<:loa_bard:1009187082205409333>", "<:loa_bard:1009187082205409333>", "<:loa_bard:1009187082205409333>", "<:loa_summoner:1009187114954530907>", "<:loa_sorceress:1009187108424003825>", "<:loa_arcanist:1009187078829002793>", "<:loa_dohwaga:1009187090329784381>", "<:loa_dohwaga:1009187090329784381>", "<:loa_dohwaga:1009187090329784381>", "<:loa_reaper:1009187102518423645>", "<:loa_deathblade:1009187087385362502>", "<:loa_shadowhunter:1009187105915809844>", "<:loa_gisang:1009187092296892597>", "<:loa_slayer:1072893448341962843>"]

Color = {
    "red": 0xff4444,
    "blue": 0x4444ff,
    "green": 0x44ff44,
    "white": 0xffffff
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

# Parse time text as "수 12:00" to day, hour, minute
def _ParseTimeText(str):
    day, time = str.split(" ")
    hour, minute = time.split(":")
    days = ["월", "화", "수", "목", "금", "토", "일"]
    try:
        day = days.index(day)
        return day, int(hour), int(minute)
    except:
        return None, None, None

import pickle


def KPMSave(kpm):
    saveDict = {}
    saveDict["version"] = 1.0
    saveDict["time"] = time.time()
    saveDict["channel"] = kpm.channel

    saveDict["groups"] = kpm.groups

    # "owner/[ownerind]" : name/card/card_demon/pause
    saveDict["user_count"] = len(kpm.users)
    for pind in range(len(kpm.users)):
        saveDict["owner/" + str(pind)] = [kpm.users[pind].name, kpm.users[pind].ping, kpm.users[pind].active, kpm.users[pind].avoiddays]

    # "party/ind" : clear/name/name/name/name
    saveDict["party_count"] = len(kpm.parties)
    for i in range(len(kpm.parties)):
        saveDict["party/" + str(i)] = [kpm.parties[i].members[j].name for j in range(len(kpm.parties[i].members))]
        saveDict["party/" + str(i) + "/C"] = kpm.parties[i].cleared
        saveDict["party/" + str(i) + "/D"] = kpm.parties[i].daytime

    # "char/[charind]" : name/owner/role/power/essential/isSupportMode
    saveDict["char_count"] = len(kpm.characters)
    for char, ind in zip(kpm.characters, range(len(kpm.characters))):
        saveDict["char/" + str(ind)] = [char.owner, char.name, char.role, char.power, char.essential, char.active, char.isSupportMode]

    pickle.dump(saveDict, open("./data/kakul/latest.save", "wb"))
    print("Save Complete")

def KPMLoad(path, kpm):
    pickleData = pickle.load(open(path, "rb"))

    kpm.characters = []
    kpm.users = []
    kpm.parties = []
    kpm.leftovers = []
    kpm.groups = pickleData["groups"]
    try:
        kpm.channel = pickleData["channel"]
    except:
        pass
    
    for i in range(pickleData["user_count"]):
        pp = pickleData["owner/" + str(i)]
        try:
            kpm.AddUserRaw(pp[0], pp[1], pp[2], pp[3])
        except:
            kpm.AddUserRaw(pp[0], pp[1], pp[2], "")

    for i in range(pickleData["char_count"]):
        pp = pickleData["char/" + str(i)]
        kpm.AddCharacterRaw(pp[0], pp[1], pp[2], pp[3], pp[4], pp[5], pp[6])
    
    for i in range(pickleData["party_count"]):
        pp = pickleData["party/" + str(i)]
        clear = pickleData["party/" + str(i) + "/C"]
        try:
            daytime = pickleData["party/" + str(i) + "/D"]
        except:
            daytime = ""
        kpm.AddPartyRaw(pp, clear, daytime)
        # kpm.AddPartyRaw(pp, clear)


    kpm.Validate()

    print("Load Complete")
