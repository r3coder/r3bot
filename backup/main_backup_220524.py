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

def Load():
    global M
    if os.path.exists("data_pinglist.pkl"):
        with open('data_pinglist.pkl', 'rb') as save_file:
            M.pingList = pickle.load(save_file)

    saveDict = dict()
    if os.path.exists("data_characters.pkl"):
        with open('data_characters.pkl', 'rb') as save_file:
            saveDict = pickle.load(save_file)
    for i in saveDict:
        sv = saveDict[i].split("|")
        ess = True if sv[3] == "1" else False
        M.AddCharacter(sv[0], sv[1], sv[2], ess, float(sv[4]))

@client.event
async def on_ready():
    global M
    for guild in client.guilds:
        if guild.name == GUILD:
            break
    Load()
    
    print(
        f'{client.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})'
    )

from emote import emote_dict

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
    # for bot feature, check if message channel is correct
    if message.channel.name != MESSAGE_CHANNEL:
        return
    
    msg = msg.split(' ')
    if msg[0] == '명령어' or msg[0] == 'h':
        embed=discord.Embed(description="사용 가능한 메세지 목록입니다.", color=discord.Color.green())
        embed.add_field(name="캐릭터추가 [캐릭이름] [직업]", value="캐릭터 이름을 파티 풀에 추가합니다. (ca)\n 직업 리스트 : %s"%str(ROLE_LIST), inline=False)
        embed.add_field(name="캐릭터제거 [캐릭이름]", value="캐릭터 이름을 파티 풀에서 제거합니다. (cr)", inline=False)
        embed.add_field(name="캐릭터목록", value="현재 쿠크세이튼 풀에 있는 캐릭터 목록을 불러옵니다. (cl)", inline=False)
        embed.add_field(name="유저정보 \{유저이름\}", value="입력한 유저의 캐릭터와 파티가 결성되어 있다면 소속된 파티를 출력합니다. (u)", inline=False)
        embed.add_field(name="파티목록", value="현재 쿠크세이튼 파티 목록을 확인합니다. (파티, l)", inline=False)
        embed.add_field(name="파티호출 [파티번호]", value="[파티번호]번 파티 사람들을 호출합니다. (호출, p)", inline=False)
        embed.add_field(name="클리어 [파티번호]", value="남은 파티 조정을 위해서 클리어 후 이 명령어를 쳐 주세요. (c)", inline=False)
        embed.add_field(name="클리어취소 [파티번호]", value="실수로 클리어를 입력했을 때, 이 명령어로 취소가 가능합니다. (취소, cc)", inline=False)
        embed.add_field(name="파티탈퇴 [캐릭이름]", value="파티에서 캐릭터를 제외시킵니다. 이미 클리어 된 파티는 변경이 불가능합니다. (탈퇴, x)", inline=False)
        embed.add_field(name="파티참여 [캐릭이름] [파티번호]", value="파티에 캐릭터를 참여시킵니다. 직업/폿유무 여부를 확인하지 않습니다. 이미 클리어 되었거나, 4명이 모두 차 있는 파티에는 참가 불가능합니다. (참여, i)", inline=False)
        embed.add_field(name="딜량설정 [캐릭이름] [값]", value="딜러의 세기를 설정합니다. 기본값은 1입니다. 딜폿은 딜로 표시될 때를 기준딜량으로 삼습니다. (cd)", inline=False)
        embed.add_field(name="필수설정 [캐릭이름] [예/아니오]", value="꼭 돌지 않아도 되는 캐릭을 표시할 수 있습니다. (ce)", inline=False)
        embed.add_field(name="파티결성", value="쿠크세이튼 파티를 결성합니다. 관리자만 사용할 수 있습니다. (ppp)", inline=False)
        await message.channel.send(embed=embed)
    elif msg[0] == '캐':
        if str(message.author) != "R3C0D3r#0210":
            embed=discord.Embed(description="관리자만 입력 가능합니다.", color=discord.Color.red())
        else:
            c = M.AddCharacter(msg[3], msg[1], msg[2])
            embed=discord.Embed(description="가상 캐릭터 추가",color=discord.Color.blue())
        await message.channel.send(embed=embed)
        Save()
    elif msg[0] == "파티리셋" or msg[0] == "ppx":
        if str(message.author) != "R3C0D3r#0210":
            embed=discord.Embed(description="관리자만 입력 가능합니다.", color=discord.Color.red())
        else:
            M.ResetParties()
            embed=discord.Embed(description="파티가 리셋되었습니다.", color=discord.Color.red())
        await message.channel.send(embed=embed)
    elif msg[0] == "파티결성" or msg[0] == "ppp":
        if str(message.author) != "R3C0D3r#0210":
            embed=discord.Embed(description="관리자만 입력 가능합니다.", color=discord.Color.red())
        else:
            M.MakeParties()
            embed=discord.Embed(description="파티가 결성되었습니다. `%s파티목록` 으로 파티 결성 정보를 확인할 수 있습니다."%IDENTIFIER, color=discord.Color.blue())
        await message.channel.send(embed=embed)
    elif msg[0] == '파티최대딜' or msg[0] == "ppmd":
        if str(message.author) != "R3C0D3r#0210":
            embed=discord.Embed(description="관리자만 입력 가능합니다.", color=discord.Color.red())
        else:
            try:
                a = float(msg[1])
                M.partyPowerThreshold = a
                embed=discord.Embed(description="파티최대딜량이 정해졌습니다.", color=discord.Color.blue())
            except:
                embed=discord.Embed(description="딜량에 정확하지 않은 값이 들어갔습니다", color=discord.Color.red())
        await message.channel.send(embed=embed)
    elif msg[0] == "전부호출" or msg[0] == "ppc":
        s = "호출: "
        if str(message.author) != "R3C0D3r#0210":
            embed=discord.Embed(description="관리자만 입력 가능합니다.", color=discord.Color.red())
        else:
            l = []
            for member in M.characters:
                if M.pingList[member.owner] not in l and member.owner in M.pingList:
                    l.append(M.pingList[member.owner])
            for ist in l:
                s += ist + " "
            embed=discord.Embed(description="캐릭터 리스트에 있는 사람을 모두 호출했습니다.", color=discord.Color.blue())
            
        await message.channel.send(s, embed=embed)
    # Things that user can input
    elif msg[0] == '캐릭터추가' or msg[0] == 'ca':
        if len(msg) < 3:
            embed=discord.Embed(description="캐릭터 형식을 정확히 입력해 주세요.\n`%s캐릭터추가 [캐릭이름] [직업]`\n\n직업 리스트 : %s"%(IDENTIFIER, str(ROLE_LIST)), color=discord.Color.red())
        else:
            if msg[2] not in ROLE_LIST:
                embed=discord.Embed(description="직업이 잘못되었습니다.\n\n직업 리스트 : %s"%str(ROLE_LIST), color=discord.Color.red())
            elif M.IsCharacterExists(msg[1]):
                embed=discord.Embed(description="이미 존재하는 캐릭터입니다.", color=discord.Color.red())
            else:
                s = ""
                c = M.AddCharacter(message.author, msg[1], msg[2])
                s += "캐릭터 %s가 쿠크세이튼 파티 풀에 추가되었습니다."%(c.name)
                if len(M.parties) > 0:
                    M.leftovers.append(c)
                    s += "\n이미 결성된 파티가 있어서, 파티에 소속되지 못한 캐릭터에 추가되었습니다."
                embed=discord.Embed(description= s, color=discord.Color.blue())
        Save()
        await message.channel.send(embed=embed)
    elif msg[0] == "캐릭터제거" or msg[0] == "cr":
        if len(msg) < 2:
            embed=discord.Embed(description="메세지 형식을 정확히 입력해 주세요.\n`%s캐릭터제거 [캐릭이름]"%IDENTIFIER, color=discord.Color.red())
        else:
            v = M.RemoveCharacterByName(msg[1])
            if v:
                s = "%s 캐릭터가 쿠크세이튼 파티 풀에서 제거되었습니다. 이미 결성된 파티에서는 제거되지 않습니다."%msg[1]
                """
                if v in M.leftovers:
                    M.leftovers.remove(v)
                    s += "\n파티 없는 캐릭터 명단에서 또한 제거되었습니다."
                for idx in range(len(M.parties)):
                    if v in M.parties[idx].members:
                        M.parties[idx].members.remove(v)
                        s = "\n파티 %d 번에서 제거되었습니다."%(idx+1)
                        break
                """
                embed=discord.Embed(description=s, color=discord.Color.blue())
            else:
                embed=discord.Embed(description="존재하지 않는 캐릭터입니다.", color=discord.Color.red())
        Save()
        await message.channel.send(embed=embed)
    elif msg[0] == "캐릭터목록" or msg[0] == "cl":
        ss = ""
        for c in M.characters:
            ss += "%s\n"%c
        embed=discord.Embed(description="현재 쿠크세이튼 풀에 있는 캐릭터 목록입니다.\n현재 %d개의 캐릭터가 풀에 있습니다.\n%s"%(len(M.characters),ss), color=discord.Color.blue())
        await message.channel.send(embed=embed)
    elif msg[0] == "파티목록" or msg[0] == "파티" or msg[0] == "l":
        if len(M.parties) == 0:
            embed=discord.Embed(description="결성되어 있는 파티가 없습니다. 관리자에게 문의해 파티결성 명령을 입력해 주세요.", color=discord.Color.red())
        else:
            embed=discord.Embed(description="현재 쿠크세이튼 풀에 있는 파티 목록입니다.\n참가가 불가능하거나 파티 멤버 변경이 필요할 경우, 각 파티원들과 직접 조율 바랍니다.", color=discord.Color.blue())
            for v, p in enumerate(M.parties):
                stv = "(인원부족)" if len(p.members) < 4 else ""
                embed.add_field(name="파티 %d %s"%((v+1),stv), value="%s"%p, inline=False)
            p = "파티에 소속되지 못한 캐릭터들입니다.\n"
            for i in M.leftovers:
                p += "%s\n"%i
            embed.add_field(name="파티 없음", value="%s"%p, inline=False)
        await message.channel.send(embed=embed)
    elif msg[0] == "클리어" or msg[0] == "c":
        if len(msg) < 2:
            embed=discord.Embed(description="메세지 형식을 정확히 입력해 주세요.\n`%s클리어 [파티번호]"%IDENTIFIER, color=discord.Color.red())
        else:
            try:
                p = int(msg[1])
            except:
                p = -1
            if p < 1 or p > len(M.parties):
                embed=discord.Embed(description="존재하지 않는 파티 번호입니다.", color=discord.Color.red())
            else:
                if M.parties[p-1].isCleared:
                    embed=discord.Embed(description="이미 클리어된 파티입니다.", color=discord.Color.red())
                else:
                    M.parties[p-1].isCleared = True
                    embed=discord.Embed(description="파티 %d번 클리어 완료!"%p, color=discord.Color.blue())
        await message.channel.send(embed=embed)
    elif msg[0] == "클리어취소" or msg[0] == "취소" or msg[0] == "cc":
        if len(msg) < 2:
            embed=discord.Embed(description="메세지 형식을 정확히 입력해 주세요.\n`%s클리어 [파티번호]"%IDENTIFIER, color=discord.Color.red())
        else:
            try:
                p = int(msg[1])
            except:
                p = -1
            if p < 1 or p > len(M.parties):
                embed=discord.Embed(description="존재하지 않는 파티 번호입니다.", color=discord.Color.red())
            else:
                M.parties[p-1].isCleared = False
                embed=discord.Embed(description="파티 %d번 클리어 처리를 취소했습니다."%p, color=discord.Color.blue())
        await message.channel.send(embed=embed)
    elif msg[0] == "유저정보" or msg[0] == "u":
        if len(msg) < 2:
            user = str(message.author)
        else:
            user = msg[1]
        embed=discord.Embed(description="유저 %s의 정보입니다."%user, color=discord.Color.blue())
        cnt = 0
        s = ""
        for i in M.characters:
            if i.owner == user:
                cnt+=1
                s += str(i) + "\n"
        if s == "":
            "파티 풀에 포함된 캐릭터가 없습니다."
        embed.add_field(name="파티 풀에 포함된 캐릭터 수 %d"%(cnt), value="%s"%s, inline=False)
        if len(M.parties) > 0:
            for v, p in enumerate(M.parties):
                if p.isOwnerExists(user):
                    stv = "(인원부족)" if len(p.members) < 4 else ""
                    embed.add_field(name="파티 %d %s"%((v+1),stv), value="%s"%p, inline=False)
        await message.channel.send(embed=embed)
    elif msg[0] == "파티호출" or msg[0] == "호출" or msg[0] == "p":
        s = ""
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
                r = M.PartyOwners(p-1)
                for i in r:
                    if i in M.pingList:
                        s += M.pingList[i] + " "
                    else:
                        s += " "
                embed=discord.Embed(description="파티가 호출되었습니다.", color=discord.Color.blue())
        await message.channel.send(s, embed=embed)
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
                    if c1 in M.leftovers:
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
        await message.channel.send(embed=embed)
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

        await message.channel.send(embed=embed)
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
        await message.channel.send(embed=embed)
    elif msg[0] == "필수설정" or msg[0] == "ce":
        if len(msg) < 3:
            embed=discord.Embed(description="형식을 정확히 입력해 주세요.\n`%s위치변경 [캐릭이름] [필수여부]", color=discord.Color.red())
        c = M.GetCharacterByName(msg[1])
        if c != None:
            if msg[2] == "예":
                c.isRequired = True
                embed=discord.Embed(description="필수여부를 설정했습니다.", color=discord.Color.blue())
            elif msg[2] == "아니오":
                c.isRequired = False
                embed=discord.Embed(description="필수여부를 설정했습니다.", color=discord.Color.blue())
            else:
                embed=discord.Embed(description="유효하지 않은 필수여부입니다.", color=discord.Color.red())
        else:
            embed=discord.Embed(description="존재하지 않는 캐릭터입니다.", color=discord.Color.red())
        Save()
        await message.channel.send(embed=embed)
    else:
        embed=discord.Embed(description="알수없는 명령어입니다.\n`%s명령어`을 입력해 입력 가능한 명령어를 확인하세요."%IDENTIFIER, color=discord.Color.red())
        await message.channel.send(embed=embed)


client.run(TOKEN)