

import random
import interactions
import os
import pickle
import time

ARMOR_NAME = ["머리장식", "어깨장식", "상의", "하의", "장갑", "무기"]

MAX_TOKENS = 72
TOKEN_TIME = 3600
db_base = "./data/qs/"

def GetRandomQuality():
    random_table = [99.24, 98.23, 96.98, 94.46, 88.16, 78.09, 64.23, 46.60, 25.19, 0]
    random_value = random.random()*100
    for i in range(len(random_table)):
        if random_value > random_table[i]:
            return random.randint((9-i)*10+1, (10-i)*10)

def GetBar(value):
    squ = (value - 1) // 5 + 1
    if value == 0:
        return ":black_large_square:" * 20
    elif value <= 9:
        return ":red_square:" * squ + ":black_large_square:" * (20 - squ)
    elif value <= 29:
        return ":yellow_square:" * squ + ":black_large_square:" * (20 - squ)
    elif value <= 69:
        return ":green_square:" * squ + ":black_large_square:" * (20 - squ)
    elif value <= 89:
        return ":blue_square:" * squ + ":black_large_square:" * (20 - squ)
    elif value <= 99:
        return ":purple_square:" * squ + ":black_large_square:" * (20 - squ)
    elif value == 100:
        return ":orange_square:" * 20

def GetCol(value):
    if value == 0:
        return ":black_large_square:"
    elif value <= 9:
        return ":red_square:"
    elif value <= 29:
        return ":yellow_square:"
    elif value <= 69:
        return ":green_square:"
    elif value <= 89:
        return ":blue_square:"
    elif value <= 99:
        return ":purple_square:"
    elif value == 100:
        return ":orange_square:"

def LoadData(name):
    with open(db_base + "users/" + name, "rb") as f:
        return pickle.load(f)

def SaveData(name, data):
    with open(db_base + "users/" + name, "wb") as f:
        pickle.dump(data, f)

class UserStat:
    def __init__(self, name, data):
        self.name = name
        self.score = 0
        for i in range(5):
            self.score += data["q%d"%i] + 100 * (data["l%d"%i] - 1)
        self.score += (data["q5"] + 100 * (data["l5"] - 1)) * 3

        self.tries = 0
        for i in range(6):
            self.tries += data["tt%d"%i]

        self.tier = ""
        tierRank = ["", ":one:", ":two:", ":three:", ":four:"]
        for i in range(6):
            self.tier += tierRank[data["l%d"%i]] + GetCol(data["q%d"%i]) + " "

    def GetInfo(self):
        return self.score, self.tries, self.tier


class QualitySim:
    def __init__(self):
        pass

    def Initialize(self, owner):
        data = {}
        data["owner"] = owner
        for i in range(6):
            data["q%d"%i] = GetRandomQuality()
            data["t%d"%i] = 1
            data["tt%d"%i] = 1
            data["l%d"%i] = 1
        data["tokens"] = MAX_TOKENS
        # current time as int
        data["lasttime"] = int(time.time())
        SaveData(owner, data)
        return data

    def GetEmbed(self, owner):
        if not os.path.exists(db_base + "users/" + owner):
            data = self.Initialize(owner)
        else:
            data = LoadData(owner)
        
        newTokens = (int(time.time()) - data["lasttime"]) // TOKEN_TIME

        if newTokens > 0:
            data["tokens"] += newTokens
            if data["tokens"] > MAX_TOKENS:
                data["tokens"] = MAX_TOKENS
            data["lasttime"] = int(time.time())
            SaveData(owner, data)
        current_token = data["tokens"]
        embed = interactions.Embed(title="품질 업글 시뮬레이터 : %s"%(owner), description="혼돈의 돌 수 : %d / %d "%(current_token, MAX_TOKENS), color=0xED9021)
        for i in range(6):
            embed.add_field(name="[%d] 환상의 %s 티어 %d `(시도: %d/%d)`"%(data["q%d"%i], ARMOR_NAME[i], data["l%d"%i],  data["t%d"%i], data["tt%d"%i]), value="%s"%GetBar(data["q%d"%i]), inline=False)
        return embed

    def GetButtons(self, owner):
        btns = [[], []]
        data = LoadData(owner)
        v = 1 if data["q0"] != 100 else 3
        btns[0].append(interactions.Button(style=v, custom_id="qub0", label=ARMOR_NAME[0]))
        v = 1 if data["q1"] != 100 else 3
        btns[0].append(interactions.Button(style=v, custom_id="qub1", label=ARMOR_NAME[1]))
        v = 1 if data["q2"] != 100 else 3
        btns[0].append(interactions.Button(style=v, custom_id="qub2", label=ARMOR_NAME[2]))
        v = 1 if data["q3"] != 100 else 3
        btns[1].append(interactions.Button(style=v, custom_id="qub3", label=ARMOR_NAME[3]))
        v = 1 if data["q4"] != 100 else 3
        btns[1].append(interactions.Button(style=v, custom_id="qub4", label=ARMOR_NAME[4]))
        v = 1 if data["q5"] != 100 else 3
        btns[1].append(interactions.Button(style=v, custom_id="qub5", label=ARMOR_NAME[5]))
        return btns
    
    def UpgradeQuality(self, owner, type):
        embed = self.GetEmbed(owner)
        if not os.path.exists(db_base + "users/" + owner):
            return embed
        else:
            data = LoadData(owner)

        # Upgrade Tier
        if data["q%d"%type] == 100:
            data["q%d"%type] = GetRandomQuality()
            data["l%d"%type] += 1
            data["t%d"%type] = 1
            data["tt%d"%type] += 1
            SaveData(owner, data)
            embed = self.GetEmbed(owner)
            embed.add_field(name="장비 티어 업그레이드", value="품질을 초기화하고 티어가 올라갑니다.", inline=False)
            return embed
        
        if data["tokens"] < 1:
            embed.add_field(name="혼돈의 돌이 부족합니다.", value="`[장비 티어 * 1]`개의 돌이 필요하며, 돌은 %d초에 하나씩 채워집니다"%TOKEN_TIME, inline=False)
            return embed
        if type == 5 and data["tokens"] < 3:
            embed.add_field(name="혼돈의 돌이 부족합니다.", value="`[장비 티어 * 3]`개의 돌이 필요하며, 돌은 %d초에 하나씩 채워집니다"%TOKEN_TIME, inline=False)
            return embed
        newQ = GetRandomQuality()

        data["t%d"%type] += 1
        data["tt%d"%type] += 1
        oldQ = data["q%d"%type]
        data["tokens"] -= 1 * data["l%d"%type] if type < 5 else 3 * data["l%d"%type]
        if data["q%d"%type] >= newQ:
            SaveData(owner, data)
            embed = self.GetEmbed(owner)
            embed.add_field(name=":confounded: 품질 업그레이드 실패", value="%d > %d"%(oldQ, newQ), inline=False)
        else:
            data["q%d"%type] = newQ
            SaveData(owner, data)
            embed = self.GetEmbed(owner)
            embed.add_field(name=":partying_face: 품질 업그레이드 성공!", value="%d > %d"%(oldQ, newQ), inline=False)

        return embed

    def GetRank(self):
        files = os.listdir(db_base + "users")
        l = []
        for f in files:
            data = LoadData(f)
            l.append(UserStat(f.split("/")[-1], data))
        l.sort(key=lambda x: x.score, reverse=True)

        emb0 = ""
        emb1 = ""
        emb2 = ""
        for ind in l:
            a0, a1, a2 = ind.GetInfo()
            emb0 += ind.name + "\n"
            emb1 += "`%5d (%4d)`\n"%(a0, a1)
            emb2 += "%s\n"%a2
        
        embed = interactions.Embed(title="품질작 랭킹", description = "", color=0xED9021)
        embed.add_field(name="이름", value=emb0, inline=True)
        embed.add_field(name="점수 (시도횟수)", value=emb1, inline=True)
        embed.add_field(name="정보", value=emb2, inline=True)
        return embed