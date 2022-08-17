# bot.py
import os
from re import S
import pickle
from turtle import left
import discord
from dotenv import load_dotenv
from manager import Manager, Party, Character, ROLE_LIST

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

IDENTIFIER = "[["
MESSAGE_CHANNEL = "🤖쿠크세이튼-파티"
ADMIN = ["R3C0D3r#0210"]

M = Manager()
client = discord.Client()

def Save():
    # save parties to file
    with open('data_pinglist.pkl', 'wb') as save_file:
        pickle.dump(M.pingList, save_file)
    saveDict = dict()
    for i in M.characters:
        ess = 1 if i.essential else 0
        saveDict[i.name] = "%s|%s|%s|%s|%s"%(i.owner, i.name, i.role, ess, str(i.power))
    with open('data_characters.pkl', 'wb') as save_file:
        pickle.dump(saveDict, save_file)

    partyDict = dict()
    with open('data_partylist.pkl', 'wb') as save_file:
        for char in M.characters:
            partyDict[char.name] = M.GetPartyOfCharacter(char.name)
            partyDict["#party_count"] = len(M.parties)
        pickle.dump(partyDict, save_file)

def Load():
    global M
    if os.path.exists("data_pinglist.pkl"):
        with open('data_pinglist.pkl', 'rb') as save_file:
            M.pingList = pickle.load(save_file)
    M.parties = []
    M.characters = []
    saveDict = dict()
    if os.path.exists("data_characters.pkl"):
        with open('data_characters.pkl', 'rb') as save_file:
            saveDict = pickle.load(save_file)
    for i in saveDict:
        sv = saveDict[i].split("|")
        ess = True if sv[3] == "1" else False
        M.AddCharacter(sv[0], sv[1], sv[2], ess, float(sv[4]))
    
    partyDict = dict()
    if os.path.exists("data_partylist.pkl"):
        with open('data_partylist.pkl', 'rb') as save_file:
            partyDict = pickle.load(save_file)
        party_count = partyDict["#party_count"]
        del partyDict["#party_count"]
        for i in range(party_count):
            M.parties.append(Party())
        for k, v in partyDict.items():
            if v == -1:
                M.leftovers.append(M.GetCharacterByName(k))
            else:
                M.parties[v].members.append(M.GetCharacterByName(k))


@client.event
async def on_ready():
    global M
    for guild in client.guilds:
        if guild.name == GUILD:
            break
    Load()
    print(M.pingList)
    
    print(
        f'{client.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})'
    )


from emote import emote_dict
def PartyHelp():
   embed=discord.Embed(description="사용 가능한 메세지 목록입니다.", color=discord.Color.green())
   embed.add_field(name="캐릭터추가 [캐릭이름] [직업]", value="캐릭터 이름을 파티 풀에 추가합니다. (ca)\n 직업 리스트 : %s"%str(ROLE_LIST), inline=False)
   embed.add_field(name="캐릭터제거 [캐릭이름]", value="캐릭터 이름을 파티 풀에서 제거합니다. (cr)", inline=False)
   embed.add_field(name="캐릭터목록", value="현재 쿠크세이튼 풀에 있는 캐릭터 목록을 불러옵니다. (cl)", inline=False)
   embed.add_field(name="유저정보 \{유저이름\}", value="입력한 유저의 캐릭터와 파티가 결성되어 있다면 소속된 파티를 출력합니다. \n 만일 유저 이름을 입력하지 않을 경우, 메세지를 입력한 유저의 정보를 출력합니다.(u)", inline=False)
   embed.add_field(name="파티목록", value="현재 쿠크세이튼 파티 목록을 확인합니다. (파티, l)", inline=False)
   embed.add_field(name="파티호출 [파티번호]", value="[파티번호]번 파티 사람들을 호출합니다. (호출, p)", inline=False)
   embed.add_field(name="클리어 [파티번호]", value="남은 파티 조정을 위해서 클리어 후 이 명령어를 쳐 주세요. (c)", inline=False)
   embed.add_field(name="클리어취소 [파티번호]", value="실수로 클리어를 입력했을 때, 이 명령어로 취소가 가능합니다. (취소, cc)", inline=False)
   embed.add_field(name="파티탈퇴 [캐릭이름]", value="파티에서 캐릭터를 제외시킵니다. 이미 클리어 된 파티는 변경이 불가능합니다. (탈퇴, x)", inline=False)
   embed.add_field(name="파티참여 [캐릭이름] [파티번호]", value="파티에 캐릭터를 참여시킵니다. 직업/폿유무 여부를 확인하지 않습니다. 이미 클리어 되었거나, 4명이 모두 차 있는 파티에는 참가 불가능합니다. (참여, i)", inline=False)
   embed.add_field(name="인원교체 [캐릭이름1] [캐릭이름2]", value="배정된 인원의 위치를 교환시킵니다. (교체, cn)", inline=False)
   embed.add_field(name="딜량설정 [캐릭이름] [값]", value="딜러의 세기를 설정합니다. 기본값은 1입니다. 딜폿은 딜로 표시될 때를 기준딜량으로 삼습니다. (cd)", inline=False)
   embed.add_field(name="필수설정 [캐릭이름] [예/아니오]", value="꼭 돌지 않아도 되는 캐릭을 표시할 수 있습니다. (ce)", inline=False)
   embed.add_field(name="파티결성", value="쿠크세이튼 파티를 결성합니다. 관리자만 사용할 수 있습니다. (ppp)", inline=False)
   return embed

def IsAdmin(user):
    if user in ADMIN:
        return None
    return discord.Embed(description=message_text["NOT_ADMIN"], color=discord.Color.red())

@client.event
async def on_message(message):
    global IDENTIFIER, MESSAGE_CHANNEL
    if message.author == client.user:
        return
    
    # Automatically add message sender to db to ping someone
    if message.author not in M.pingList:
        M.pingList[str(message.author)] = message.author.mention

    # send emote
    if message.content in emote_dict:
        await message.channel.send(emote_dict[message.content])

    # check if message starts with "!!"
    if not message.content.startswith(IDENTIFIER):
        return
    # remove identifier
    msg = message.content.replace(IDENTIFIER,"")
    if msg == '채널':
        # embed=discord.Embed(title="채널 설정", description="채널이 ", color=discord.Color.blue())
        embed=discord.Embed(description="이 봇의 메세지 채널이 이 채널로 설정되었습니다.", color=discord.Color.blue())
        MESSAGE_CHANNEL = message.channel.name
        await message.channel.send(embed=embed)
        return
    
    msg = msg.split(' ')
    content = ""

    if msg[0] in ["쌀", "경매", "T", "ㅆ"]:
        v = int(msg[1])
        embed = discord.Embed(description="경매 %d를 쌀산합니다..."%v, color=discord.Color.blue())
        s4 = v*3/4*0.95*0.95
        s8 = v*7/8*0.95*0.95
        embed.add_field(name="4인", value="손익분기: %d\n경매입찰: %d"%(s4, s4/1.1), inline=True)
        embed.add_field(name="8인", value="손익분기: %d\n경매입찰: %d"%(s8, s8/1.1), inline=True)

        # try:
        # except:
        #     embed = discord.Embed(description="값을 정확히 입력하지 않았습니다.", color=discord.Color.red())
        await message.channel.send(embed=embed)
        return
    # for bot feature, check if message channel is correct
    if message.channel.name != MESSAGE_CHANNEL:
        return
    
    # Help
    if msg[0] in ['명령어', 'h']:
        embed = PartyHelp()

    # Admin Feature
    elif msg[0] in ['캐릭터추가고급', 'caa']: # Add dummy character, ping will not work if user haven't input any message on any textchannel
        embed = IsAdmin(str(message.author))
        if embed == None:
            c = M.AddCharacter(msg[3], msg[1], msg[2], power=float(msg[4]))
            embed = discord.Embed(description="캐릭터를 고급 기능으로 추가하였습니다",color=discord.Color.blue())
    elif msg[0] in ["파티리셋", "ppx"]:
        embed = IsAdmin(str(message.author))
        if embed == None:
            M.ResetParties()
            embed = discord.Embed(description="파티가 리셋되었습니다.", color=discord.Color.red())
        Save()
    elif msg[0] == "파티결성" or msg[0] == "ppp":
        embed = IsAdmin(str(message.author))
        if embed == None:
            M.MakeParties()
            embed=discord.Embed(description="파티가 결성되었습니다.\n`%s파티목록` 으로 파티 결성 정보를 확인할 수 있습니다."%IDENTIFIER, color=discord.Color.blue())
        Save()
    elif msg[0] == '파티최대딜' or msg[0] == "ppdM":
        embed = IsAdmin(str(message.author))
        if embed == None:
            try:
                M.partyPowerMaxThreshold = float(msg[1])
                embed=discord.Embed(description="파티최대딜량이 정해졌습니다.", color=discord.Color.blue())
            except:
                embed=discord.Embed(description="명령어를 잘못 사용했습니다.", color=discord.Color.red())
    elif msg[0] == '파티최소딜' or msg[0] == "ppdm":
        embed = IsAdmin(str(message.author))
        if embed == None:
            try:
                M.partyPowerMinThreshold = float(msg[1])
                embed=discord.Embed(description="파티최소딜량이 정해졌습니다.", color=discord.Color.blue())
            except:
                embed=discord.Embed(description="명령어를 잘못 사용했습니다.", color=discord.Color.red())
    elif msg[0] == '우선배정세기' or msg[0] == "ppdp":
        embed = IsAdmin(str(message.author))
        if embed == None:
            try:
                M.priorityPower = float(msg[1])
                embed=discord.Embed(description="딜러의 우선배정세기가 정해졌습니다.", color=discord.Color.blue())
            except:
                embed=discord.Embed(description="명령어를 잘못 사용했습니다.", color=discord.Color.red())
    elif msg[0] == "전부호출" or msg[0] == "ppc":
        embed = IsAdmin(str(message.author))
        if embed == None:
            l = []
            for member in M.characters:
                if M.pingList[str(member.owner)] not in l and str(member.owner) in M.pingList:
                    l.append(M.pingList[str(member.owner)])
            for ist in l:
                content += ist + " "
            embed=discord.Embed(description="캐릭터 리스트에 있는 사람을 모두 호출했습니다.", color=discord.Color.blue())

    #######################################################
    # Edit from here
    #######################################################

    # Things that user can input
    elif msg[0] == '캐릭터추가' or msg[0] == 'ca':
        if len(msg) < 3: # Parse error
            embed = discord.Embed(description="캐릭터 형식을 정확히 입력해 주세요.\n`%s캐릭터추가 [캐릭이름] [직업]`\n\n직업 리스트 : %s"%(IDENTIFIER, str(ROLE_LIST)), color=discord.Color.red())
        else:
            embed = M.AddCharacter(message.author, msg[1], msg[2])
            Save() # Save information if character is added
    elif msg[0] == "캐릭터제거" or msg[0] == "cr":
        if len(msg) < 2:
            embed=discord.Embed(description="메세지 형식을 정확히 입력해 주세요.\n`%s캐릭터제거 [캐릭이름]"%IDENTIFIER, color=discord.Color.red())
        else:
            M.RemoveCharacter(msg[1])
            embed = discord.Embed(description="캐릭터가 제거되었습니다.", color=discord.Color.blue())
            Save() # Save information if character is deleted
    elif msg[0] == "캐릭터목록" or msg[0] == "ll":
        embed=discord.Embed(description="현재 쿠크세이튼 풀에 있는 캐릭터 목록입니다.\n현재 %d개의 캐릭터가 풀에 있습니다.\n%s"%(M.GetCharacterCount(),M.GetCharactersText()), color=discord.Color.blue())
    elif msg[0] == "파티목록" or msg[0] == "파티" or msg[0] == "l":
        embed = M.GetPartyEmbed()
    elif msg[0] == "클리어" or msg[0] == "cl":
        if len(msg) < 2:
            embed = discord.Embed(description="메세지 형식을 정확히 입력해 주세요.\n`%s클리어 [파티번호]"%IDENTIFIER, color=discord.Color.red())
        else:
            embed = M.SetPartyClear(msg[1], True)
        Save()
    elif msg[0] == "클리어취소" or msg[0] == "취소" or msg[0] == "cc":
        if len(msg) < 2:
            embed = discord.Embed(description="메세지 형식을 정확히 입력해 주세요.\n`%s클리어취소 [파티번호]"%IDENTIFIER, color=discord.Color.red())
        else:
            embed = M.SetPartyClear(msg[1], False)
        Save()
    elif msg[0] == "유저정보" or msg[0] == "u":
        user = str(message.author) if len(msg) < 2 else msg[1]
        embed = M.GetUserEmbed(user)
    elif msg[0] == "파티호출" or msg[0] == "호출" or msg[0] == "p":
        if len(msg) < 2:
            embed=discord.Embed(description="메세지 형식을 정확히 입력해 주세요.\n`%s파티호출 [파티번호]"%IDENTIFIER, color=discord.Color.red())
        else:
            try:
                p = int(msg[1])
            except:
                p = -1
            if p < 1 or p > len(M.parties):
                embed=discord.Embed(description="존재하지 않는 파티 번호입니다.", color=discord.Color.red())
            else:
                r = M.GetPartyOwners(p-1)
                for i in r:
                    if i in M.pingList:
                        content += M.pingList[i] + " "
                    else:
                        content += " "
                embed=discord.Embed(description="파티가 호출되었습니다.", color=discord.Color.blue())
    elif msg[0] == "파티참여" or msg[0] == "참여" or msg[0] == "i":
        if len(msg) < 3:
            embed=discord.Embed(description="메세지 형식을 정확히 입력해 주세요.\n`%s파티참여 [캐릭이름] [파티번호]"%IDENTIFIER, color=discord.Color.red())
        c1 = M.GetCharacterByName(msg[1])

        if c1 == None:
            embed=discord.Embed(description="존재하지 않는 캐릭이름입니다.", color=discord.Color.red())
        else:
            try:
                p = int(msg[2])
            except:
                p = -1
            if p < 1 or p > len(M.parties):
                embed=discord.Embed(description="존재하지 않는 파티 번호입니다.", color=discord.Color.red())
            else:
                if M.parties[p-1].isCleared:
                    embed=discord.Embed(description="이미 클리어된 파티입니다.", color=discord.Color.red())
                elif len(M.parties[p-1].members) == 4:
                    embed=discord.Embed(description="이미 최대 인원입니다.", color=discord.Color.red())
                else:
                    if M.parties[p-1].isOwnerExists(c1.owner):
                        embed=discord.Embed(description="해당 파티에는 이미 %s이(가) 참여하고 있습니다."%c1.owner, color=discord.Color.red())
                    elif c1 in M.leftovers:
                        M.parties[p-1].members.append(c1)
                        M.leftovers.remove(c1)
                        embed=discord.Embed(description="캐릭터 %s를 대기 명단에서 제외하고 파티 %d번에 참여시켰습니다."%(c1.name, p), color=discord.Color.blue())
                    else:
                        for ind in range(len(M.parties)):
                            if c1 in M.parties[ind].members:
                                if (ind+1 == p):
                                    embed=discord.Embed(description="이미 캐릭터 %s는 파티 %d번에 있습니다."%(c1.name, ind+1), color=discord.Color.red())
                                else:
                                    M.parties[p-1].members.append(c1)
                                    M.parties[ind].members.remove(c1)
                                    embed=discord.Embed(description="캐릭터 %s를 파티 %d번에서 파티 %d번으로 이동시켰습니다."%(c1.name, ind+1, p), color=discord.Color.blue())
                                break
        Save()
    elif msg[0] == "파티탈퇴" or msg[0] == "탈퇴" or msg[0] == "x":
        if len(msg) < 2:
            embed=discord.Embed(description="메세지 형식을 정확히 입력해 주세요.\n`%s파티탈퇴 [캐릭이름]"%IDENTIFIER, color=discord.Color.red())
        else:
            c1 = M.GetCharacterByName(msg[1])
            if c1 == None:
                embed=discord.Embed(description="존재하지 않는 캐릭이름입니다.", color=discord.Color.red())
            else:
                for i in range(len(M.parties)):
                    if c1 in M.parties[i].members:
                        if M.parties[i].isCleared:
                            embed=discord.Embed(description="이미 클리어된 파티입니다.", color=discord.Color.red())
                            break
                        M.parties[i].RemoveCharacter(c1)
                        M.leftovers.append(c1)
                        embed=discord.Embed(description="캐릭터 %s 파티에서 탈퇴했습니다."%c1.name, color=discord.Color.blue())
                        break
                else:
                    embed=discord.Embed(description="캐릭터 %s는 파티에 없습니다."%c1.name, color=discord.Color.red())
        Save()
    elif msg[0] == "인원교체" or msg[0] == "교체" or msg[0] == "cn":
        if len(msg) < 3:
            embed=discord.Embed(description="메세지 형식을 정확히 입력해 주세요.\n`%s인원교체 [캐릭이름1] [캐릭이름2]"%IDENTIFIER, color=discord.Color.red())
        else:
            c1 = M.GetCharacterByName(msg[1])
            c2 = M.GetCharacterByName(msg[2])
            if c1 == None or c2 == None:
                embed=discord.Embed(description="존재하지 않는 캐릭이름입니다.", color=discord.Color.red())
            else:
                if c1 in M.leftovers and c2 in M.leftovers:
                    embed=discord.Embed(description="두 캐릭터가 모두 파티에 소속되지 않았습니다.", color=discord.Color.red())
                elif c1 in M.leftovers:
                    ind = M.GetPartyOfCharacter(c2.name)
                    M.parties[ind].RemoveCharacter(c2)
                    M.leftovers.append(c2)
                    if M.parties[ind].isOwnerExists(c1.owner):
                        embed=discord.Embed(description="%s이(가) 있는 파티에는 이미 %s이(가) 참여하고 있습니다."%(c2.name, c1.owner), color=discord.Color.red())
                        M.parties[ind].members.append(c2)
                        M.leftovers.remove(c2)
                    else:
                        M.parties[ind].members.append(c1)
                        M.leftovers.remove(c1)
                        embed=discord.Embed(description="%s이 대기자 명단으로 이동하고, %s가 파티 %d에 참가했습니다."%(c2.name, c1.name, ind), color=discord.Color.blue())
                elif c2 in M.leftovers:
                    ind = M.GetPartyOfCharacter(c1.name)
                    M.parties[ind].RemoveCharacter(c1)
                    M.leftovers.append(c1)
                    if M.parties[ind].isOwnerExists(c2.owner):
                        embed=discord.Embed(description="%s이(가) 있는 파티에는 이미 %s이(가) 참여하고 있습니다."%(c1.name, c2.owner), color=discord.Color.red())
                        M.parties[ind].members.append(c1)
                        M.leftovers.remove(c1)
                    else:
                        M.parties[ind].members.append(c2)
                        M.leftovers.remove(c2)
                        embed=discord.Embed(description="%s이 대기자 명단으로 이동하고, %s가 파티 %d에 참가했습니다."%(c1.name, c2.name, ind), color=discord.Color.blue())
                else:
                    ind1 = M.GetPartyOfCharacter(c1.name)
                    ind2 = M.GetPartyOfCharacter(c2.name)
                    M.parties[ind1].RemoveCharacter(c1)
                    M.parties[ind2].RemoveCharacter(c2)
                    M.leftovers.append(c1)
                    M.leftovers.append(c2)
                    if M.parties[ind1].isOwnerExists(c2.owner) or M.parties[ind2].isOwnerExists(c1.owner):
                        embed=discord.Embed(description="%s와 %s의 위치를 바꿀 수 없습니다. 한 파티에 한 유저가 두 명 생깁니다."%(c1.name, c2.name), color=discord.Color.red())
                        M.parties[ind2].members.append(c2)
                        M.leftovers.remove(c2)
                        M.parties[ind1].members.append(c1)
                        M.leftovers.remove(c1)
                    else:
                        M.parties[ind1].members.append(c2)
                        M.leftovers.remove(c2)
                        M.parties[ind2].members.append(c1)
                        M.leftovers.remove(c1)
                        embed=discord.Embed(description="%s이 파티 %d에 참가하고, %s가 파티 %d에 참가했습니다."%(c1.name, ind2, c2.name, ind1), color=discord.Color.blue())


    elif msg[0] == "딜량설정" or msg[0] == "cd":
        if len(msg) < 3:
            embed=discord.Embed(description="형식을 정확히 입력해 주세요.\n`%s위치변경 [캐릭이름] [딜량]", color=discord.Color.red())
        c = M.GetCharacterByName(msg[1])
        if c != None:
            try:
                c.power = float(msg[2])
                embed=discord.Embed(description="딜량을 설정했습니다.", color=discord.Color.blue())
            except:
                embed=discord.Embed(description="유효하지 않은 딜량입니다.", color=discord.Color.red())
        else:
            embed=discord.Embed(description="존재하지 않는 캐릭터입니다.", color=discord.Color.red())
        Save()
    elif msg[0] == "필수설정" or msg[0] == "ce":
        if len(msg) < 3:
            embed=discord.Embed(description="형식을 정확히 입력해 주세요.\n`%s위치변경 [캐릭이름] [필수여부]", color=discord.Color.red())
        c = M.GetCharacterByName(msg[1])
        if c != None:
            if msg[2] in ["예", "y", "Y"]:
                c.essential = True
                embed=discord.Embed(description="파티 배정이 우선적으로 되도록 설정했습니다.", color=discord.Color.blue())
            elif msg[2] in ["아니오", "N", "n"]:
                c.essential = False
                embed=discord.Embed(description="파티 배정이 우선적으로 되지 않도록 설정했습니다.", color=discord.Color.blue())
            else:
                embed=discord.Embed(description="유효하지 않은 필수여부입니다.", color=discord.Color.red())
        else:
            embed=discord.Embed(description="존재하지 않는 캐릭터입니다.", color=discord.Color.red())
        Save()
    else:
        embed=discord.Embed(description="알수없는 명령어입니다.\n`%s명령어`을 입력해 입력 가능한 명령어를 확인하세요."%IDENTIFIER, color=discord.Color.red())

    # Actually send the message
    if content == "":
        await message.channel.send(embed=embed)
    else:
        await message.channel.send(content, embed=embed)

client.run(TOKEN)
