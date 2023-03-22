#############################

import os
from dotenv import load_dotenv
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

#############################

import interactions
import asyncio

from modules.misc import Rice, TodayLuck
from modules.emote import emote_dict

from modules.kakul.manager import Manager
from modules.kakul.interface import *
from modules.kakul.utils import KPMSave, KPMLoad, printl, _ParseTimeText
from modules.mahjong import MahjongScore
from modules.quality import QualitySim
from modules.balance import BalanceManager
KPM = Manager()
MS = MahjongScore()
QS = QualitySim()
BM = BalanceManager()

bot = interactions.Client(TOKEN, intents=interactions.Intents.DEFAULT | interactions.Intents.GUILD_MESSAGE_CONTENT)


from interactions.ext.tasks import IntervalTrigger, create_task
import datetime

CHANNEL_ID = 970775035159654420
task_started = False
# CHANNEL_ID = 882546719194251274 Test Channel

@create_task(IntervalTrigger(60))
async def CallTask():
    # Get channel by name
    channel = await interactions.get(bot, interactions.Channel, object_id=CHANNEL_ID)
    # await channel.send(":)")
    # Call Everyone on Wed 10:00:15 (GMT+9)
    now = datetime.datetime.now() + datetime.timedelta(hours=9)

    # print(f'{now.weekday()} / {now.hour} / {now.minute}')
    if now.weekday() == 2 and now.hour == 10 and now.minute == 5:
        printl("Party Generation Started!")
        KPMPartyGenerate(KPM)
    if now.weekday() == 2 and now.hour == 10 and now.minute == 15:
        msg = KPMCallEveryBody(KPM)
        msg += "\n쿠크세이튼 파티가 결성되었습니다. `/파티목록` 명령어로 파티원을 확인하세요."
        await channel.send(msg)
    if len(KPM.parties) > 0:
        v = ""
        for pid in range(len(KPM.parties)):
            if v != KPM.parties[pid].GetPartyOwnerString():
                if KPM.parties[pid].cleared == False:
                    KPM.parties[pid].daytime
                    day, hour, minute = _ParseTimeText(KPM.parties[pid].daytime)
                    # print(day, hour, minute)
                    if now.weekday() == day and now.hour == hour and now.minute == minute:
                        text, embeds = KPMPartyCall(KPM, pid+1)
                        await channel.send(text, embeds=embeds)
            v = KPM.parties[pid].GetPartyOwnerString()

        # Call party 

@bot.event
async def on_ready():
    global task_started
    KPMLoad("./data/kakul/latest.save", KPM)
    if task_started == False:
        printl("Interval Task Started!")
        CallTask.start()
        task_started = True
    printl("Bot Prepared!")

@bot.event
async def on_message_create(ctx: interactions.CommandContext):
    if ctx.author.bot:
        return
    # print all attributes
    # print(dir(ctx))

    # print("author:", ctx.author)
    # print("message:", ctx.content)

    # if message.author == bot.user:
    #     return

    # Add user to pinglist if not in it
    name = str(ctx.author.username)
    try:
        for key in KPM.users:
            if name == KPM.users[key].name:
                KPM.users[key].mention = ctx.author.mention
        # if name not in PM.pingList:
        #     PM.pingList[name] = ctx.author.mention
        #     print("Added PingList:"% name)
    except:
        pass
    # if ctx.content in emote_dict:
    #     await ctx.send(emote_dict[ctx.content])



##################################################
# Rice
@bot.command(
    name="auction",
    name_localizations={"ko": "경매"},
    description="경매 입찰 값을 계산합니다",
    scope=GUILD,
    options = [
        interactions.Option(
            name="value",
            description="계산할 값",
            type=interactions.OptionType.INTEGER,
            required=True,
            name_localizations={"ko": "값"}
        ),
    ]
)
async def CommandRice(ctx: interactions.CommandContext, value: int):
    print("= CommandRice : %s"%value)
    embeds = Rice(value)
    await ctx.send("", embeds=embeds)

# Luck
@bot.command(
    name="kuku",
    name_localizations={"ko": "운세"},
    description="오늘의 쿠크세이튼 리트 확률을 알려드립니다.",
    scope=GUILD
)
async def CommandLuck(ctx: interactions.CommandContext):
    print("= CommandLuck")
    embeds = TodayLuck()
    await ctx.send("", embeds=embeds)


##################################################
# Party Manager Functions

@bot.command(
    name="set_channel",
    name_localizations={"ko": "채널설정"},
    description="채널을 설정합니다 (관리자용)",
    default_member_permissions=interactions.Permissions.ADMINISTRATOR,
    scope=GUILD,
    options = [
        interactions.Option(
            name="channel",
            description="채널을 선택합니다",
            type=interactions.OptionType.CHANNEL,
            required=True,
            name_localizations={"ko": "채널"}
        ),
    ]
)
async def CommandSetChannel(ctx: interactions.CommandContext, channel: interactions.Channel):
    if channel.type != interactions.ChannelType.GUILD_TEXT:
        await ctx.send("텍스트 채널을 선택해주세요.")
        return
    if channel.guild_id != ctx.guild_id:
        await ctx.send("서버 내의 채널을 선택해주세요.")
        return
    
    KPM.channel = ctx.channel.id
    KPMSave(KPM)
    # send message as embed
    await ctx.send(embeds=interactions.Embed(
        title="채널이 설정되었습니다.",
        description="채널: %s"%channel.mention,
        color=0x00ff00
    ))


@bot.command(
    name="party_generate",
    name_localizations={"ko": "파티생성"},
    description="파티를 결성합니다 (관리자용)",
    default_member_permissions=interactions.Permissions.ADMINISTRATOR,
    scope=GUILD,
    options = [
        interactions.Option(
            name="cubes",
            description="테스트할 경우의 수 (캐릭수**1.2*1000)",
            type=interactions.OptionType.INTEGER,
            required=False,
            name_localizations={"ko": "큐브수"}
        ),
        interactions.Option(
            name="wpb",
            description="파워 밸런스 계수 (30)",
            type=interactions.OptionType.INTEGER,
            required=False,
            name_localizations={"ko": "파워계수"}
        ),
        interactions.Option(
            name="wvs",
            description="폿 필수 계수 (20)",
            type=interactions.OptionType.INTEGER,
            required=False,
            name_localizations={"ko": "폿계수"}
        ),
        interactions.Option(
            name="wvd",
            description="직업 중복 계수 (20)",
            type=interactions.OptionType.INTEGER,
            required=False,
            name_localizations={"ko": "직업계수"}
        ),
        interactions.Option(
            name="wg",
            description="다그룹 포함 계수 (30)",
            type=interactions.OptionType.INTEGER,
            required=False,
            name_localizations={"ko": "다그룹계수"}
        ),
        interactions.Option(
            name="pu",
            description="선호 유저들",
            type=interactions.OptionType.STRING,
            required=False,
            name_localizations={"ko": "선호유저들"}
        ),
        interactions.Option(
            name="wpu",
            description="선호 유저들 계수 (10)",
            type=interactions.OptionType.INTEGER,
            required=False,
            name_localizations={"ko": "선호유저계수"}
        )
    ]
)
async def CommandPartyGenerate(ctx: interactions.CommandContext, cubes: int = 0, wpb: int = 30, wvs: int = 20, wvd: int = 20, wg: int = 30, pu: str = "", wpu: int = 10):
    await ctx.defer(ephemeral = True)
    embeds = KPMPartyGenerate(KPM, cubes, wpb, wvs, wvd, wg, pu, wpu)
    await ctx.send("", embeds=embeds)

@bot.command(
    name="party_reset",
    name_localizations={"ko": "파티리셋"},
    description="파티를 리셋합니다 (관리자용)",
    default_member_permissions=interactions.Permissions.ADMINISTRATOR,
    scope=GUILD
)
async def CommandPartyReset(ctx: interactions.CommandContext):
    embeds = KPMResetParty(KPM)
    await ctx.send("", embeds=embeds)


@bot.command(
    name="party_call_everyone",
    name_localizations={"ko": "파티전체호출"},
    description="모든 파티원을 호출합니다.",
    default_member_permissions=interactions.Permissions.ADMINISTRATOR,
    scope=GUILD
)
async def CommandPartyCallEveryone(ctx: interactions.CommandContext):
    msg = KPMCallEveryBody(KPM)
    msg += "\n쿠크세이튼 파티가 결성되었습니다. `/파티목록` 명령어로 파티원을 확인하세요."
    await ctx.send(msg)

@bot.command(
    name="party_list",
    name_localizations={"ko": "파티목록"},
    description="파티 목록을 보여줍니다",    
    scope=GUILD,
    options = [
        interactions.Option(
            name="uncleared",
            description="참일 경우, 클리어 되지 않은 파티만 보여줍니다.",
            type=interactions.OptionType.BOOLEAN,
            required=False,
            name_localizations={"ko": "클리어_안_됨"}
        ),
        interactions.Option(
            name="owner",
            description="값을 입력할 경우, 해당 유저가 포함된 파티만 보여줍니다.",
            type=interactions.OptionType.USER,
            required=False,
            name_localizations={"ko": "유저"}
        )
    ]
)
async def CommandPartyList(ctx: interactions.CommandContext, uncleared: bool = True, owner: interactions.Member = None):
    if owner is not None:
        owner = str(owner.user.username)
    embeds = KPMPartyList(KPM, uncleared, owner)
    await ctx.send("", embeds=embeds)

@bot.command(
    name="character_list",
    name_localizations={"ko": "캐릭터목록"},
    description="캐릭터 목록을 보여줍니다",
    scope=GUILD,
    options = [
        interactions.Option(
            name="owner",
            description="특정 유저의 캐릭터만 보여줍니다.",
            type=interactions.OptionType.USER,
            required=False,
            name_localizations={"ko": "유저"}
        ),
        interactions.Option(
            name="sort",
            description="유저별로 정리해서 보여줍니다.",
            type=interactions.OptionType.BOOLEAN,
            required=False,
            name_localizations={"ko": "정렬"}
        ),
    ]
)
async def CommandCharacterList(ctx: interactions.CommandContext, owner: interactions.Member = None, sort: bool = True):
    if owner is not None:
        owner = str(owner.user.username)
    embeds = KPMCharacterList(KPM, owner, sort)
    await ctx.send("", embeds=embeds)


@bot.command(
    name="character_add",
    name_localizations={"ko": "캐릭터추가"},
    description="캐릭터를 추가합니다",
    scope=GUILD,
    options = [
        interactions.Option(
            name="name",
            description="추가할 캐릭터의 이름",
            type=interactions.OptionType.STRING,
            required=True,
            name_localizations={"ko": "캐릭터_이름"}
        ),
        interactions.Option(
            name="role",
            description="추가할 캐릭터의 직업 (딜이 가능한 폿은 (딜폿)을 직업 뒤에 붙여주세요)",
            type=interactions.OptionType.STRING,
            required=True,
            name_localizations={"ko": "캐릭터_직업"}
        ),
        interactions.Option(
            name="owner",
            description="추가할 캐릭터의 소유자 (미입력시 자동으로 소유자는 자신입니다)",
            type=interactions.OptionType.USER,
            required=False,
            name_localizations={"ko": "캐릭터_소유자"}
        ),
        interactions.Option(
            name="is_essential",
            description="파티에 필수 포함 여부 (미입력시 파티에 우선적으로 배정되도록 설정합니다)",
            type=interactions.OptionType.BOOLEAN,
            required=False,
            name_localizations={"ko": "필수_포함_여부"}
        )
    ]
)
async def CommandCharacterAdd(ctx: interactions.CommandContext, name: str, role: str, owner: interactions.Member = None, is_essential: bool = True):
    if owner is None:
        owner = str(ctx.author.user.username)
    else:
        owner = str(owner.user.username)
    embeds = KPMAddCharacter(KPM, name, role, owner, is_essential)
    await ctx.send("", embeds=embeds)

@bot.command(
    name="character_changeinfo",
    name_localizations={"ko": "캐릭터정보변경"},
    description="캐릭터의 정보를 변경합니다",
    scope=GUILD,
    options = [
        interactions.Option(
            name="name",
            description="변경할 캐릭터의 이름",
            type=interactions.OptionType.STRING,
            required=True,
            name_localizations={"ko": "캐릭터_이름"}
        ),
        interactions.Option(
            name="is_essential",
            description="파티에 필수 포함 여부",
            type=interactions.OptionType.BOOLEAN,
            required=False,
            name_localizations={"ko": "필수_포함_여부"}
        ),
        interactions.Option(
            name="is_support",
            description="딜폿의 서포터 모드",
            type=interactions.OptionType.BOOLEAN,
            required=False,
            name_localizations={"ko": "서포터_모드"}
        )
    ]        
)
async def CommandCharacterChangeInfo(ctx: interactions.CommandContext, name: str, is_essential: bool = None, is_support: bool = None):
    embeds = KPMEditCharacter(KPM, name, is_essential, is_support)
    await ctx.send("", embeds=embeds)

@bot.command(
    name="character_update",
    name_localizations={"ko": "캐릭터파워업데이트"},
    description="캐릭터의 딜량 정보를 전투정보실에서 불러와 변경합니다",
    scope=GUILD,
    options = [
        interactions.Option(
            name="name",
            description="업데이트할 캐릭터의 이름, 없으면 전체 업데이트",
            type=interactions.OptionType.STRING,
            required=False
        ),
        interactions.Option(
            name="force",
            description="(필수아님) True로 설정시, 캐릭 스펙 낮아질 때도 업데이트 합니다",
            type=interactions.OptionType.BOOLEAN,
            required=False
        )

    ] 
)
async def CommandUpdateCharacter(ctx: interactions.CommandContext, name: str = None, force = False):
    await ctx.defer(ephemeral = True)
    embeds = KPMUpdateCharacter(KPM, name, force)
    await ctx.send("", embeds=embeds)

@bot.command(
    name="character_remove",
    name_localizations={"ko": "캐릭터삭제"},
    description="캐릭터를 삭제합니다",
    scope=GUILD,
    options = [
        interactions.Option(
            name="name",
            description="삭제할 캐릭터의 이름",
            type=interactions.OptionType.STRING,
            required=True
        )
    ]
)
async def CommandCharacterRemove(ctx: interactions.CommandContext, name: str):
    embeds = KPMRemoveCharacter(KPM, name)
    await ctx.send("", embeds=embeds)

@bot.command(
    name="party_clear",
    name_localizations={"ko": "파티클리어"},
    description="파티를 클리어 처리합니다",
    scope=GUILD,
    options = [
        interactions.Option(
            name="number",
            description="클리어 처리할 파티의 번호",
            type=interactions.OptionType.INTEGER,
            required=True,
            name_localizations={"ko": "파티"}
        )
    ]
)
async def CommandSetPartyClear(ctx: interactions.CommandContext, number: int):
    embeds = KPMSetPartyClearState(KPM, number, True)
    await ctx.send("", embeds=embeds)

@bot.command(
    name="party_clear_cancel",
    name_localizations={"ko": "파티클리어취소"},
    description="클리어 처리한 파티를 취소 처리합니다",
    scope=GUILD,
    options = [
        interactions.Option(
            name="number",
            description="클리어 처리를 취소할 파티의 번호",
            type=interactions.OptionType.INTEGER,
            required=True,
            name_localizations={"ko": "파티"}
        )
    ]
)
async def CommandSetPartyClearX(ctx: interactions.CommandContext, number: int):
    embeds = KPMSetPartyClearState(KPM, number, False)
    await ctx.send("", embeds=embeds)

@bot.command(
    name="party_call",
    name_localizations={"ko": "파티호출"},
    description="파티 멤버를 호출합니다.",
    scope=GUILD,
    options = [
        interactions.Option(
            name="number",
            description="호출할 파티의 번호",
            type=interactions.OptionType.INTEGER,
            required=True,
            name_localizations={"ko": "파티"}
        )
    ]
)
async def CommandPartyCall(ctx: interactions.CommandContext, number: int):
    text, embeds = KPMPartyCall(KPM, number)
    await ctx.send(text, embeds=embeds)

@bot.command(
    name="party_join",
    name_localizations={"ko": "파티참여"},
    description="파티에 캐릭터를 참여시킵니다",
    scope=GUILD,
    options = [
        interactions.Option(
            name="party",
            description="참여할 파티의 번호",
            type=interactions.OptionType.INTEGER,
            required=True,
            name_localizations={"ko": "파티"}
        ),
        interactions.Option(
            name="character",
            description="참여할 캐릭터의 이름",
            type=interactions.OptionType.STRING,
            required=True,
            name_localizations={"ko": "캐릭터"}
        ),
    ]
)
async def CommandPartyJoin(ctx: interactions.CommandContext, party: int, character: str):
    embeds = KPMPartyJoin(KPM, party, character)
    await ctx.send("", embeds=embeds)

@bot.command(
    name="party_leave",
    name_localizations={"ko": "파티탈퇴"},
    description="파티에서 캐릭터를 제거합니다",
    scope=GUILD,
    options = [
        interactions.Option(
            name="character",
            description="제거할 캐릭터의 이름",
            type=interactions.OptionType.STRING,
            required=True,
            name_localizations={"ko": "캐릭터"}
        )
    ]
)
async def CommandPartyLeave(ctx: interactions.CommandContext, character: str):
    embeds = KPMPartyLeave(KPM, character)
    await ctx.send("", embeds=embeds)

@bot.command(
    name="party_swap",
    name_localizations={"ko": "파티교환"},
    description="파티원을 서로 교환합니다",
    scope=GUILD,
    options = [
        interactions.Option(
            name="name1",
            description="교환할 캐릭터의 이름",
            type=interactions.OptionType.STRING,
            required=True,
            name_localizations={"ko": "캐릭터1"}
        ),
        interactions.Option(
            name="name2",
            description="교환할 캐릭터의 이름",
            type=interactions.OptionType.STRING,
            required=True,
            name_localizations={"ko": "캐릭터2"}
        )
    ]
)
async def CommandPartySwap(ctx: interactions.CommandContext, name1: str, name2: str):
    embeds = KPMPartySwap(KPM, name1, name2)
    await ctx.send("", embeds=embeds)

@bot.command(
    name="party_add",
    name_localizations={"ko": "파티추가"},
    description="빈 파티를 하나 추가합니다",
    scope=GUILD
)
async def CommandPartyAdd(ctx: interactions.CommandContext):
    embeds = KPMPartyAdd(KPM)
    await ctx.send("", embeds=embeds)


@bot.command(
    name="party_edit_time",
    name_localizations={"ko": "파티시간변경"},
    description="파티 시작 시간을 변경합니다",
    scope=GUILD,
    options = [
        interactions.Option(
            name="party",
            description="변경할 파티의 번호",
            type=interactions.OptionType.INTEGER,
            required=True,
            name_localizations={"ko": "파티"}
        ),
        interactions.Option(
            name="time",
            description="시간 (요일 시:분) ex) 월 20:00",
            type=interactions.OptionType.STRING,
            required=True,
            name_localizations={"ko": "시간"}
        ),
    ]
)
async def CommandPartyEditTime(ctx: interactions.CommandContext, party: int, time: str):
    embeds = KPMPartyEditTime(KPM, party, time)
    await ctx.send("", embeds=embeds)


@bot.command(
    name="user_active",
    name_localizations={"ko": "사용자활성화"},
    description="특정 사용자를 파티 배정에서 제외시킵니다.",
    scope=GUILD,
    options = [
        interactions.Option(
            name="owner",
            description="상태를 변경할 유저",
            type=interactions.OptionType.USER,
            required=False,
            name_localizations={"ko": "유저"}
        ),
        interactions.Option(
            name="state",
            description="False로 설정시 파티 배정에서 제외됩니다.",
            type=interactions.OptionType.BOOLEAN,
            required=False,
            name_localizations={"ko": "상태"}
        )
    ]
)
async def CommandUserActive(ctx: interactions.CommandContext, owner: interactions.Member = None, state: bool = True):
    if owner is None:
        owner = str(ctx.author.user.username)
    else:
        owner = str(owner.user.username)
    embeds = KPMUserActive(KPM, owner, state)
    await ctx.send("", embeds=embeds)


@bot.command(
    name="user_avoidday",
    name_localizations={"ko": "사용자기피요일"},
    description="피하고 싶은 요일을 최대 3개까지 설정 가능합니다.",
    scope=GUILD,
    options = [
        interactions.Option(
            name="avoiddays",
            description="기피할 요일을 입력합니다. 예시) 수목금",
            type=interactions.OptionType.STRING,
            required=True,
            name_localizations={"ko": "기피요일"}
        ),
        interactions.Option(
            name="owner",
            description="상태를 변경할 유저",
            type=interactions.OptionType.USER,
            required=False,
            name_localizations={"ko": "유저"}
        )
    ]
)
async def CommandUserAvoidDays(ctx: interactions.CommandContext, avoiddays: str = "", owner: interactions.Member = None):
    if owner is None:
        owner = str(ctx.author.user.username)
    else:
        owner = str(owner.user.username)
    embeds = KPMUserSetAvoidDays(KPM, owner, avoiddays)
    await ctx.send("", embeds=embeds)



@bot.command(
    name="character_active",
    name_localizations={"ko": "캐릭터활성화"},
    description="특정 캐릭터를 파티 배정에서 제외시킵니다.",
    scope=GUILD,
    options = [
        interactions.Option(
            name="character",
            description="상태를 변경할 캐릭터",
            type=interactions.OptionType.STRING,
            required=True,
            name_localizations={"ko": "캐릭터"}
        ),
        interactions.Option(
            name="state",
            description="False로 설정시 파티 배정에서 제외됩니다.",
            type=interactions.OptionType.BOOLEAN,
            required=True,
            name_localizations={"ko": "상태"}
        )
    ]
)
async def CommandCharaActive(ctx: interactions.CommandContext, character: str, state: bool):
    embeds = KPMCharacterActive(KPM, character, state)
    await ctx.send("", embeds=embeds)


@bot.command(
    name="character_essential",
    name_localizations={"ko": "캐릭터필수설정"},
    description="특정 캐릭터를 파티 배정에서 필수로 설정합니다.",
    scope=GUILD,
    options = [
        interactions.Option(
            name="character",
            description="상태를 변경할 캐릭터",
            type=interactions.OptionType.STRING,
            required=True,
            name_localizations={"ko": "캐릭터"}
        ),
        interactions.Option(
            name="state",
            description="False로 설정시 파티 배정에 무조건 포함되지는 않을 수 있습니다.",
            type=interactions.OptionType.BOOLEAN,
            required=True,
            name_localizations={"ko": "상태"}
        )
    ]
)
async def CommandCharaEssential(ctx: interactions.CommandContext, character: str, state: bool):
    embeds = KPMCharacterEssential(KPM, character, state)
    await ctx.send("", embeds=embeds)


##################################################
# Mahjong Commands

@bot.command(
    name="mahjong_playeradd",
    name_localizations={"ko": "마작플레이어추가"},
    description="마작 플레이어를 추가합니다",
    scope=GUILD,
    options = [
        interactions.Option(
            name="name",
            description="추가할 플레이어의 이름",
            type=interactions.OptionType.STRING,
            required=True
        )
    ]
)
async def CommandMahjongAddPlayer(ctx: interactions.CommandContext, name: str):
    embeds = MS.AddPlayer(name)
    await ctx.send("", embeds=embeds)

@bot.command(
    name="mahjong_score",
    name_localizations={"ko": "마작점수기록"},
    description="마작 점수를 기록합니다. 공탁금은 1등 플레이어에게 주세요",
    scope=GUILD,
    options = [
        interactions.Option(
            name="east_name",
            description="동 플레이어",
            type=interactions.OptionType.STRING,
            required=True,
            name_localizations={"ko": "동"}
        ),
        interactions.Option(
            name="south_name",
            description="남 플레이어",
            type=interactions.OptionType.STRING,
            required=True,
            name_localizations={"ko": "남"}
        ),
        interactions.Option(
            name="west_name",
            description="서 플레이어",
            type=interactions.OptionType.STRING,
            required=True,
            name_localizations={"ko": "서"}
        ),
        interactions.Option(
            name="north_name",
            description="북 플레이어",
            type=interactions.OptionType.STRING,
            required=True,
            name_localizations={"ko": "북"}
        ),
        interactions.Option(
            name="east_score",
            description="동 플레이어의 점수 (0점 기준 점수를 입력하세요)",
            type=interactions.OptionType.INTEGER,
            required=True,
            name_localizations={"ko": "동_점수"}
        ),
        interactions.Option(
            name="south_score",
            description="남 플레이어의 점수 (0점 기준 점수를 입력하세요)",
            type=interactions.OptionType.INTEGER,
            required=True,
            name_localizations={"ko": "남_점수"}
        ),
        interactions.Option(
            name="west_score",
            description="서 플레이어의 점수 (0점 기준 점수를 입력하세요)",
            type=interactions.OptionType.INTEGER,
            required=True,
            name_localizations={"ko": "서_점수"}
        ),
        interactions.Option(
            name="north_score",
            description="북 플레이어의 점수 (0점 기준 점수를 입력하세요)",
            type=interactions.OptionType.INTEGER,
            required=True,
            name_localizations={"ko": "북_점수"}
        ),
        interactions.Option(
            name="note",
            description="메모",
            type=interactions.OptionType.STRING,
            required=False,
            name_localizations={"ko": "메모"}
        )
    ]
)
async def CommandMahjongScore(ctx: interactions.CommandContext, east_name: str, south_name: str, west_name: str, north_name: str, east_score: int, south_score: int, west_score: int, north_score: int, note: str = ""):
    # await ctx.defer()
    embeds = MS.AddGame([east_name, south_name, west_name, north_name], [east_score, south_score, west_score, north_score], ctx.id.timestamp, note)
    # await asyncio.sleep(3)
    await ctx.send("", embeds=embeds)


@bot.command(
    name="mahjong_recent",
    name_localizations={"ko": "마작최근게임"},
    description="최근 게임을 표시합니다",
    scope=GUILD,
    options = [
        interactions.Option(
            name="amount",
            description="표시할 최근 게임의 수",
            type=interactions.OptionType.INTEGER,
            required=False
        )
    ]
)
async def CommandMahjongRecent(ctx: interactions.CommandContext, amount: int = 5):
    embeds = MS.ShowRecentGames(amount)
    await ctx.send("", embeds=embeds)

@bot.command(
    name="mahjong_ranking",
    name_localizations={"ko": "마작총합랭킹"},
    description="마작 총합 랭킹을 표시합니다",
    scope=GUILD
)
async def CommandMahjongRecent(ctx: interactions.CommandContext):
    embeds = MS.ShowRanking()
    await ctx.send("", embeds=embeds)

##################################################
# Quality Upgrade

@bot.command(
    name="quality_upgrade",
    name_localizations={"ko": "품질작"},
    description="품질작 시뮬레이터를 불러옵니다.",
    scope=GUILD
)
async def CommandQualityUpgrade(ctx: interactions.CommandContext):
    owner = str(ctx.author.user.username)
    embeds = QS.GetEmbed(owner)
    btns = QS.GetButtons(owner)
    await ctx.send("", embeds=embeds,
        components=btns)

@bot.command(
    name="quality_rank",
    name_localizations={"ko": "품질작랭킹"},
    description="품질작 시뮬레이터의 랭킹을 보여줍니다.",
    scope=GUILD
)
async def CommandQualityRank(ctx: interactions.CommandContext):
    embeds = QS.GetRank()
    await ctx.send("", embeds=embeds)


@bot.component("qub0")
async def CommandQualityUpgrade0(ctx: interactions.ComponentContext):
    owner = str(ctx.author.user.username)
    embeds = QS.UpgradeQuality(owner, 0)
    btns = QS.GetButtons(owner)
    await ctx.edit("", embeds=embeds,
        components=btns)

@bot.component("qub1")
async def CommandQualityUpgrade1(ctx: interactions.ComponentContext):
    owner = str(ctx.author.user.username)
    embeds = QS.UpgradeQuality(owner, 1)
    btns = QS.GetButtons(owner)
    await ctx.edit("", embeds=embeds,
        components=btns)

@bot.component("qub2")
async def CommandQualityUpgrade2(ctx: interactions.ComponentContext):
    owner = str(ctx.author.user.username)
    embeds = QS.UpgradeQuality(owner, 2)
    btns = QS.GetButtons(owner)
    await ctx.edit("", embeds=embeds,
        components=btns)

@bot.component("qub3")
async def CommandQualityUpgrade3(ctx: interactions.ComponentContext):
    owner = str(ctx.author.user.username)
    embeds = QS.UpgradeQuality(owner, 3)
    btns = QS.GetButtons(owner)
    await ctx.edit("", embeds=embeds,
        components=btns)

@bot.component("qub4")
async def CommandQualityUpgrade4(ctx: interactions.ComponentContext):
    owner = str(ctx.author.user.username)
    embeds = QS.UpgradeQuality(owner, 4)
    btns = QS.GetButtons(owner)
    await ctx.edit("", embeds=embeds,
        components=btns)

@bot.component("qub5")
async def CommandQualityUpgrade5(ctx: interactions.ComponentContext):
    owner = str(ctx.author.user.username)
    embeds = QS.UpgradeQuality(owner, 5)
    btns = QS.GetButtons(owner)
    await ctx.edit("", embeds=embeds,
        components=btns)


@bot.command(
    name="quality_addstone",
    name_localizations={"ko": "품질작돌지급"},
    description="혼돈의 돌을 지급합니다",
    default_member_permissions=interactions.Permissions.ADMINISTRATOR,
    scope=GUILD,
    options = [
        interactions.Option(
            name="owner",
            description="혼돈의 돌을 지급할 사용자",
            type=interactions.OptionType.USER,
            required=False,
            name_localizations={"ko": "지급대상"}
        ),
        interactions.Option(
            name="amount",
            description="지급할 혼돈의 돌의 수",
            type=interactions.OptionType.INTEGER,
            required=False,
            name_localizations={"ko": "지급수량"}
        )
    ]
)
async def CommandQualityAdd(ctx: interactions.CommandContext, owner: interactions.Member = None, amount: int = 0):
    if owner is None:
        owner = str(ctx.author.user.username)
    else:
        owner = str(owner.user.username)
    embeds = QS.AddStone(owner, amount)
    await ctx.send("", embeds = embeds)

@bot.command(
    name="quality_substone",
    name_localizations={"ko": "품질작돌압수"},
    description="혼돈의 돌을 압수합니다",
    default_member_permissions=interactions.Permissions.ADMINISTRATOR,
    scope=GUILD,
    options = [
        interactions.Option(
            name="owner",
            description="혼돈의 돌을 압수할 사용자",
            type=interactions.OptionType.USER,
            required=False,
            name_localizations={"ko": "압수대상"}
        ),
        interactions.Option(
            name="amount",
            description="압수할 혼돈의 돌의 수",
            type=interactions.OptionType.INTEGER,
            required=False,
            name_localizations={"ko": "압수수량"}
        )
    ]
)
async def CommandQualitySub(ctx: interactions.CommandContext, owner: interactions.Member = None, amount: int = 0):
    if owner is None:
        owner = str(ctx.author.user.username)
    else:
        owner = str(owner.user.username)
    embeds = QS.SubStone(owner, amount)
    await ctx.send("", embeds = embeds)


@bot.command(
    name="purge_message",
    name_localizations={"ko": "메세지삭제"},
    description="메세지를 삭제합니다.",
    default_member_permissions=interactions.Permissions.ADMINISTRATOR,
    options=[
        interactions.Option(
            name="amount",
            description="삭제할 메세지의 수",
            type=interactions.OptionType.INTEGER,
            required=False,
            name_localizations={"ko": "삭제수량"}
        )
    ],
    scope=GUILD
)
async def CommandRemoveRecent(ctx: interactions.CommandContext, amount: int = 100):
    await ctx.channel.purge(amount=amount)
    embeds = interactions.Embed(
        title="메세지 삭제 완료",
        description=f"{amount}개의 메세지를 삭제했습니다.",
        color=0xff0000
    )
    await ctx.send("", embeds=embeds)


bot.start()
"""
# Crontab
from datetime import datetime
import threading


def checkTime():
    # This function runs periodically every 1 second
    threading.Timer(1, checkTime).start()

    now = datetime.now()

    current_time = now.strftime("%H:%M:%S")
    print("Current Time =", current_time)

    if(current_time == '06:00:00'):  # check if matches with the desired time
        print('sending message')


checkTime()
"""