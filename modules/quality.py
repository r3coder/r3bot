

import random
import interactions
import os
import pickle
import time

ARMOR_NAME = ["머리장식", "어깨장식", "상의", "하의", "장갑", "무기"]
PREFIX_NAME = ["", "환상의", "환장의", "극한의", "존재하지 않는", "초월한", "무한의", "영겁의"]
TIER_EMOTE  = ["", ":one:", ":two:", ":three:", ":four:", ":five:", ":six:", ":seven:"]

MAX_TOKENS = 300
TOKEN_TIME = 600
db_base = "./data/qs/"

def GetRandomQuality():
    random_table = [99.24, 98.23, 96.98, 94.46, 88.16, 78.09, 64.23, 46.60, 25.19, 0]
    random_value = random.random()*100
    for i in range(len(random_table)):
        if random_value > random_table[i]:
            if i == len(random_table) - 1:
                return random.randint(0, 10)
            else:
                return random.randint((9-i)*10+1, (10-i)*10)


def GetScore(value):
    return 30 + value * value / 100 * 0.7

def GetProb(value):
    random_table = [0.76, 1.01, 1.25, 2.52, 6.32, 10.07, 13.86, 17.63, 21.41, 25.19]
    if value == 100:
        return 0
    elif value <= 10:
        return 25.19 * (11 - value - 1) / 11 + 74.81
    prob = 0
    for i in range((100-value)//10):
        prob += random_table[i]
    prob += (random_table[(100-value)//10]) * (9 - (value - 1) % 10) / 10
    return prob 

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
            self.score += GetScore(data["q%d"%i]) + 100 * (data["l%d"%i] - 1)
        self.score += (GetScore(data["q5"]) + 100 * (data["l5"] - 1)) * 3

        self.tries = 0
        for i in range(6):
            self.tries += data["tt%d"%i]

        self.stone = 0
        for i in range(5):
            self.stone += data["tt%d"%i]
        self.stone += data["tt5"] * 3

        self.tier = ""
        for i in range(6):
            self.tier += TIER_EMOTE[data["l%d"%i]] + GetCol(data["q%d"%i]) + " "

    def GetInfo(self):
        return self.score, self.tries, self.tier, self.stone


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

    def Update(self, owner):
        if not os.path.exists(db_base + "users/" + owner):
            data = self.Initialize(owner)
        else:
            data = LoadData(owner)
        newTokens = (int(time.time()) - data["lasttime"]) // TOKEN_TIME
        if newTokens > 0 and data["tokens"] < MAX_TOKENS:
            data["tokens"] += newTokens
            if data["tokens"] > MAX_TOKENS:
                data["tokens"] = MAX_TOKENS
            data["lasttime"] = int(time.time())
            SaveData(owner, data)

    def GetEmbed(self, owner):
        if not os.path.exists(db_base + "users/" + owner):
            data = self.Initialize(owner)
        
        self.Update(owner)
        data = LoadData(owner)

        current_token = data["tokens"]
        embed = interactions.Embed(title="품질 업글 시뮬레이터 : %s"%(owner), description="혼돈의 돌 수 : %d / %d "%(current_token, MAX_TOKENS), color=0xED9021)
        for i in range(6):
            embed.add_field(name="[%d] %s %s (티어 %d) `(시도: %d/%d)`"%(data["q%d"%i], PREFIX_NAME[data["l%d"%i]], ARMOR_NAME[i], data["l%d"%i],  data["t%d"%i], data["tt%d"%i]), value="%s `%6.2f%%`"%(GetBar(data["q%d"%i]), GetProb(data["q%d"%i])), inline=False)
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
        
        if type == 5 and data["tokens"] < 3 * data["l%d"%type] or type != 5 and data["tokens"] < data["l%d"%type]:
            embed.add_field(name="혼돈의 돌이 부족합니다.", value="`[장비 티어 * 1]`개의 돌이 필요하며, 돌은 %d초에 하나씩 채워집니다"%TOKEN_TIME, inline=False)
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

        embed = interactions.Embed(title="품질작 랭킹", description = "점수 계산법 : `(30+[품질 수치]^2÷100×0.7+[티어]×100)×[무기=3, 장비=1]`", color=0xED9021)
        for ini in range((len(l)-1)//5 + 1):
            emb0 = ""
            emb1 = ""
            emb2 = ""
            for i in range(ini*5, min((ini+1)*5, len(l))):
                a0, a1, a2, a3 = l[i].GetInfo()
                emb0 += l[i].name + "\n"
                emb1 += "%5d (%d/%d)\n"%(a0, a1, a3)
                emb2 += "%s\n"%a2
            if ini == 0:
                embed.add_field(name="이름", value=emb0, inline=True)
                embed.add_field(name="점수 (횟수/혼돌)", value=emb1, inline=True)
                embed.add_field(name="정보", value=emb2, inline=True)
            else:
                embed.add_field(name="===", value=emb0, inline=True)
                embed.add_field(name="===", value=emb1, inline=True)
                embed.add_field(name="===", value=emb2, inline=True)
        return embed

    
    def AddStone(self, owner, amount):
        if not os.path.exists(db_base + "users/" + owner):
            return interactions.Embed(title="유저가 존재하지 않습니다", description = "", color=0xED9021)
        self.Update(owner)
        data = LoadData(owner)
        data["tokens"] += amount
        SaveData(owner, data)
        return interactions.Embed(title="유저 %s에게 돌을 %d개 지급해 현재 돌은 %d개입니다."%(owner, amount, data["tokens"]), description = "", color=0xED9021)
    
    def SubStone(self, owner, amount):
        if not os.path.exists(db_base + "users/" + owner):
            return interactions.Embed(title="유저가 존재하지 않습니다", description = "", color=0xED9021)

        self.Update(owner)
        data = LoadData(owner)
        data["tokens"] -= amount
        SaveData(owner, data)
        return interactions.Embed(title="유저 %s에게 돌을 %d개 압수해 현재 돌은 %d개입니다."%(owner, amount, data["tokens"]), description = "", color=0xED9021)