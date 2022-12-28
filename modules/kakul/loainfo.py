import urllib.request
from urllib.parse import quote
from html.parser import HTMLParser

def GetApproxStrength(username, minor=False, verbose=False):
    # fp = urllib.request.urlopen("https://lostark.game.onstove.com/Profile/Character/Skyswayer")
    fp = urllib.request.urlopen("https://lostark.game.onstove.com/Profile/Character/" + quote(username))
    mybytes = fp.read()
    mystr = mybytes.decode("utf-8")
    fp.close()

    parser = HTMLParser()
    parser.feed(mystr)

    if verbose:
        print("Character Name:", username)
    # Base Attack
    pos = mystr.find("기본 공격력은")
    atk = int(mystr[pos+30:pos+35])
    if verbose:
        print("Base Attack:", atk)

    # Gems
    gemsD = []
    gemsC = []
    for i in range(1, 10):
        for c in range(mystr.count("%d레벨 멸화의 보석"%(11-i))):
            gemsD.append(11-i)
        for c in range(mystr.count("%d레벨 홍염의 보석"%(11-i))):
            gemsC.append(11-i)
    dmgs = [1.03, 1.06, 1.09, 1.12, 1.15, 1.18, 1.21, 1.24, 1.30, 1.40]
    cools = [1.02, 1.04, 1.06, 1.09, 1.11, 1.14, 1.16, 1.19, 1.22, 1.25]
    
    totd, coef, totx = 0, 1, 0
    for elem in gemsD:
        totd += dmgs[elem-1] * coef
        totx += coef
        coef *= 0.7
    totc = 0
    for elem in gemsC:
        totc += cools[elem-1]
    gemDmg = 1
    gemDmg *= 1 if len(gemsD) == 0 else totd / totx
    gemDmg *= 1 if len(gemsC) == 0 else totc / len(gemsC)
    
    if verbose:
        print("Gem Level:", gemDmg, gemsD, gemsC)

    # Quality
    quality = 0
    qRank = ["유물", "고대"]
    qWeap = ["롱 스태프", "타로카드", "리아네 하프", "지팡이",
                "한손검", "랜스", "해머", "대검", 
                "런쳐", "총", "서브 머신건", "활",
                "건틀릿", "헤비 건틀릿", "창",
                "붓", "우산",
                "데모닉웨폰", "대거", "검"]
    for qri in qRank:
        for qwi in qWeap:
            pos = mystr.find(qri + " " + qwi)
            if pos < 0:
                continue
            quality = int(mystr[pos+167+len(qwi):pos+170+len(qwi)].replace(",",""))
            break
    qualityv = 1.1 + quality * quality / 10000 * 0.2
    if verbose:
        print("Quality:", quality, qualityv)

    cardValue = 1.0
    if mystr.find("세상을 구하는 빛 6세트 (30각성합계)") > 0:
        cardValue = 1.15
    elif mystr.find("세상을 구하는 빛 6세트 (18각성합계)") > 0:
        cardValue = 1.08
    elif mystr.find("카제로스의 군단장 6세트 (30각성합계)") > 0:
        cardValue = 1.15
    elif mystr.find("카제로스의 군단장 6세트 (18각성합계)") > 0:
        cardValue = 1.08
    elif mystr.find("세 우마르가 오리라 3세트 (15각성합계)") > 0:
        cardValue = 1.15
    if verbose:
        print("Card:", cardValue)

    # Role DPS Focus
    rolev = 1
    role = {"황후의 은총":1.1, "점화":1.1, "절정":1.1, "역천지체":1.1, "포격 강화":1.1, "광전사의 비기":1.1}
    for i, v in role.items():
        if mystr.count(i) >= 2:
            if verbose:
                print("Role DPS Focus:", i, v)
            rolev = v
            break

    approx = int(atk * gemDmg * qualityv * cardValue * rolev)
    if minor:
        try:
            ## Minor statstics
            # Properties Total
            pos = mystr.find("<span>신속</span> <span>")
            prop0 = int(mystr[pos+22:pos+26].replace("<", "").replace("/", ""))
            pos = mystr.find("<span>특화</span> <span>")
            prop1 = int(mystr[pos+22:pos+26].replace("<", "").replace("/", ""))
            pos = mystr.find("<span>치명</span> <span>")
            prop2 = int(mystr[pos+22:pos+26].replace("<", "").replace("/", ""))
            pps = (prop0+prop1+prop2)/7500+0.67
            if verbose:
                print("Properties:", prop0, prop1, prop2, prop0+prop1+prop2, pps)

            # bracelet
            bracelet = 1.0
            if mystr.find("순환 : 10초 간격으로 스킬 피해 <FONT COLOR='#99ff99'>2.5%</FONT> 증가") > 0:
                bracelet *= 1.027
            if mystr.find("순환 : 10초 간격으로 스킬 피해 <FONT COLOR='#99ff99'>3%</FONT> 증가") > 0:
                bracelet *= 1.033
            if mystr.find("순환 : 10초 간격으로 스킬 피해 <FONT COLOR='#99ff99'>3.5%</FONT> 증가") > 0:
                bracelet *= 1.04
            if mystr.find("순환 : 10초 간격으로 스킬 피해 <FONT COLOR='#99ff99'>4%</FONT> 증가") > 0:
                bracelet *= 1.045
            if verbose:
                print("Bracelet:", bracelet)
                
            approxx = int(approx*bracelet*pps)
            if verbose:
                print("Approximate Strength (minor):", approxx)
            return approxx
        except:
            print("GetApproxStrength: Error on Minor Statistics, returning approx strength")

    else:
        if verbose:
            print("Approximate Strength:", approx)
        return approx

    """    
    f = open("test.html", 'w', encoding='utf-8')
    f.write(mystr)
    f.close()
    """ 


# lst = ["로아창술사찍먹","후회해줬으면","Skyswayer","라즈비안"]

# lst = ["로아창술사찍먹","후회해줬으면","Skyswayer","라즈비안","폰현수","숨지마라버스커버스커","Crackee소리","플렘아르카나","Crackee서큐","사하라의황제펭귄","데비안레드햇","텔루리온","조레로이","걸어서장판속으로","신림동매콤주먹","폼포코역전만루홈런","돌아와줬으면","아마존의비둘기","사나시은건부슬기","Crackee혈귀","슬랙웨어","센트OS","히말라야의앵무새","CrackeeGS","플렘도아가","초실수","북극산사막여우","알래스카의키위새","시베리아의도요새","질퐁노도이슬비기상술사","일식집사시미도둑","리레퍼이","좋아할것같아","샷건루시안","미워해줬으면","자유수","유리수","마다가스카의호랑이","워레로이","아로나OS","린도우즈","호소구치"]
# for i in lst:
#     print("%3.1f %s"%(GetApproxStrength(i, verbose=True)/27000, i))
# for i in lst:
#     print("%3.2f %s"%(GetApproxStrength(i)/30000, i))