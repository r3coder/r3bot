
import interactions
import os

Color = {
    "red": 0xdd2222,
    "blue": 0x2222dd,
    "green": 0x22dd22,
}

db_base = "./data_mj/"

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

def RankScore(score, uma = [20000, 10000], oka = 0):
    v = score.copy()
    v.sort()
    score[score.index(v[3])] += 0 + uma[0] + oka * 3
    score[score.index(v[2])] += 0 + uma[1] - oka * 1
    score[score.index(v[1])] += 0 - uma[1] - oka * 1
    score[score.index(v[0])] += 0 - uma[0] - oka * 1
    for i in range(len(score)):
        score[i] = score[i] / 1000.0
    return score

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
            return interactions.Embed(description="점수의 합이 0이 아닙니다", color=Color["red"])

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
        total_score, play_count = {}, {}
        # parse each file
        for f in files:
            user, score, note = ParseScoreFile(db_base + "games/" + f)
            rscore = RankScore(score)
            for ind in range(len(user)):
                if user[ind] in total_score:
                    total_score[user[ind]] += rscore[ind]
                    play_count[user[ind]] += 1
                else:
                    total_score[user[ind]] = rscore[ind]
                    play_count[user[ind]] = 1
        # sort by total score
        total_score = sorted(total_score.items(), key=lambda x: x[1], reverse=True)
        # add embed to each user
        rank = "```\n"
        rank += "          이름      총점     평균     국수\n"
        for i, v in enumerate(total_score):
            rank += "%12s   %6.1f   %6.1f     %3d\n"%(v[0], v[1], v[1]/play_count[v[0]],play_count[v[0]])
        rank += "```"
        embed = interactions.Embed(title="마작 점수 랭킹", description = rank, color=Color["blue"])
        return embed
