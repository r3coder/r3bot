import random
import interactions

# Return desired auction value for a given value
def Rice(value):
    embed = interactions.Embed(description="경매 %d를 쌀산합니다..."%value, color=0x4444ff)
    s4 = value*3/4*0.95*0.95
    s8 = value*7/8*0.95*0.95
    embed.add_field(name="4인", value="손익분기: %d\n경매입찰: %d"%(s4, s4/1.1), inline=True)
    embed.add_field(name="8인", value="손익분기: %d\n경매입찰: %d"%(s8, s8/1.1), inline=True)
    return embed


def Luck():
    v = random.randint(0, 100)
    if v < 5:
        return "매우 나쁨", "쿠크세이튼이 음흉한 미소를 내뿜습니다.\n매우 조심하는 게 좋을 거 같습니다.", 0xdd0000
    elif v < 15:
        return "나쁨", "쿠크세이튼이 실소를 지으며 지긋이 바라봅니다.\n조심하는 게 좋을 거 같습니다.", 0xff6522
    elif v < 30:
        return "조금 나쁨", "돌 부리에 걸려 넘어질 뻔했지만, 다행히 안 넘어진 것 같습니다.", 0xEDC521
    elif v < 55:
        return "보통", "무난한 하루가 될 것 같습니다", 0xE7ED21
    elif v < 75:
        return "조금 좋음", "시원한 에어컨 바람이 느껴지는 정도의 좋은 기분이 드는 날입니다", 0x16D97D
    elif v < 85:
        return "좋음", "생각지도 못 한 곳에서 아이템을 얻을지도?", 0x22ECF0
    elif v < 95:
        return "매우 좋음", "행운의 여신이 뺨따구를 살짝 치고 간 듯한 느낌입니다.", 0x007EDC
    else:
        return "최고조", "오늘 품질을 누르거나 무기 강화를 하면 잘 될지도?", 0xffffff

def TodayLuck():
    c, t, v = Luck()
    embed = interactions.Embed(description="오늘의 운세를 알려드립니다.", color=v)
    embed.add_field(name=t, value=c, inline=True)
    return embed