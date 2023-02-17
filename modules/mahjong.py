
import interactions
import os

Color = {
    "red": 0xdd2222,
    "blue": 0x2222dd,
    "green": 0x22dd22,
}

db_base = "./data/mj/"

RANK_SCORE = [None, 20000, 10000, -10000, -20000]
WIND = ["東", "南", "西", "北"]

class UserScore:
    def __init__(self, name):
        self.name = name
        self.totalScore = 0
        self.games = 0
        self.scores = list()
        self.ranks = list()
        self.positions = list()

    def AddScore(self, score, rank, position):
        self.scores.append(score)
        self.ranks.append(rank)
        self.positions.append(position)
        self.totalScore += score + RANK_SCORE[rank]
        self.games += 1
    
    def GetScoreText(self):
        return self.totalScore, self.totalScore/self.games
    
    def GetGames(self):
        r = [0, 0, 0, 0, 0]
        for ind in range(self.games):
            r[self.ranks[ind]] += 1
        return self.games, r[1] / self.games * 100, r[2] / self.games * 100, r[3] / self.games * 100, r[4] / self.games * 100


    def __str__(self):
        r = [0, 0, 0, 0, 0]
        for ind in range(self.games):
            r[self.ranks[ind]] += 1
        v1 = " 100%" if r[1] == self.games else "%04.1f%%"%(r[1] / self.games * 100)
        v2 = " 100%" if r[2] == self.games else "%04.1f%%"%(r[2] / self.games * 100)
        v3 = " 100%" if r[3] == self.games else "%04.1f%%"%(r[3] / self.games * 100)
        v4 = " 100%" if r[4] == self.games else "%04.1f%%"%(r[4] / self.games * 100)
        return "%12s│%6.1f│%6.1f│%6d│%s│%s│%s│%s"%(self.name, self.totalScore/1000, self.totalScore/1000/self.games, self.games, v1, v2, v3 ,v4)
       

# Parse score file, return a list, list
# First line is user, second line is score, separated by ","
# Third line is note
def ParseScoreFile(file):
    with open(file, "r") as f:
        lines = f.readlines()
        if len(lines) < 3:
            return None
        user = lines[0].strip().split(",")
        score = lines[1].strip().split(",")
        for i in range(len(score)):
            score[i] = int(score[i])
        note = lines[2].strip()
        return user, score, note

class MahjongScore:
    def __init__(self):
        pass
    
    def AddPlayer(self, name):
        if not os.path.exists(db_base + "users/" + name):
            with open(db_base + "users/" + name, "w") as f:
                f.write("")
            return interactions.Embed(description="유저가 생성되었습니다.", color=Color["green"])
        else:
            return interactions.Embed(description="유저가 이미 존재합니다.", color=Color["red"])

    def AddGame(self, name, score, timestamp, note):
        for i in name:
            if not os.path.exists(db_base + "users/" + i):
                return interactions.Embed(description="존재하지 않는 유저입니다.: %s"%i, color=Color["red"])
        time = str(timestamp).replace(" ", "_").replace("-","").replace(":","")

        if score[0] + score[1] + score[2] + score[3] != 0:
            return interactions.Embed(description="점수의 합이 0이 아닙니다. 합계: %d 점입니다."%(score[0] + score[1] + score[2] + score[3]), color=Color["red"])

        with open(db_base + "games/" + time, "a") as f:
            f.write("%s,%s,%s,%s\n"%(name[0], name[1], name[2], name[3]))
            f.write("%d,%d,%d,%d\n"%(score[0], score[1], score[2], score[3]))
            f.write("%s\n"%(note))
        for i in name:
            with open(db_base + "users/" + i, "a") as f:
                f.write("%s\n"%(time))

        stn = "東 %s, %d\n"%(name[0], score[0])
        stn += "南 %s, %d\n"%(name[1], score[1])
        stn += "西 %s, %d\n"%(name[2], score[2])
        stn += "北 %s, %d\n"%(name[3], score[3])
        embed = interactions.Embed(description="마작 점수가 기록되었습니다.\n"+stn, color=Color["blue"])
        
        return embed
    
    # Show recent games
    def ShowRecentGames(self, amount):
        embed = interactions.Embed(title="최근 %d 게임"%amount, color=Color["blue"])
        files = os.listdir(db_base + "games")
        files.sort(key=lambda x: int(x.split(".")[0]))
        for f in files[-amount:]:
            user, score, note = ParseScoreFile(db_base + "games/" + f)
            note = "" if len(note) < 1 else "특이사항 : " + note + "\n"
            embed.add_field(name=str(f).split("/")[-1].split("'")[0], value="東 %s %s 南 %s %s 西 %s %s 北 %s %s\n"%(user[0],score[0],user[1],score[1],user[2],score[2],user[3],score[3]) + note, inline=False)
        return embed

    def ShowRanking(self):
        # read all files in games folder and sort by timestamp
        # temp coding, change to class later on
        files = os.listdir(db_base + "games")
        files.sort(key=lambda x: int(x.split(".")[0]))

        userscores = {}
        # parse each file
        for f in files:
            user, score, note = ParseScoreFile(db_base + "games/" + f)
            rank = [4, 3, 2, 1]
            sr = [sum(x) for x in zip(score, rank)]
            vl = sr.copy()
            vl.sort(reverse=True)
            for ind in range(len(user)):
                if user[ind] not in userscores:
                    userscores[user[ind]] = UserScore(user[ind])
                userscores[user[ind]].AddScore(score[ind], vl.index(sr[ind])+1, ind+1)
        
        # sort by totalScore
        userscores = sorted(userscores.values(), key=lambda x: x.totalScore, reverse=True)

        name = ""
        score = ""
        rank = ""
        for i, v in enumerate(userscores):
            name += "`%s`"%v.name + "\n"
            score += "`%6.1f (%6.1f)`\n"%(v.totalScore/1000, v.totalScore/v.games/1000)
            t, v1, v2, v3, v4 = v.GetGames()
            rank += "`%3d (%03d%%/%03d%%/%03d%%/%03d%%)`\n"%(t, v1, v2, v3, v4)
        
        embed = interactions.Embed(title="마작 점수 랭킹", description = "", color=Color["blue"])
        embed.add_field(name="이름", value=name, inline=True)
        embed.add_field(name="총점 (평균)", value=score, inline=True)
        embed.add_field(name="국수 (1등/2등/3등/4등)", value=rank, inline=True)
        return embed