#############################

import os
from dotenv import load_dotenv
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

#############################

import interactions
import asyncio

from misc import Rice, TodayLuck
from emote import emote_dict
from utils import SavePartyManager, LoadPartyManager
from manager import Manager
PM = Manager()

from mahjong import MahjongScore
MS = MahjongScore()

bot = interactions.Client(TOKEN, intents=interactions.Intents.DEFAULT | interactions.Intents.GUILD_MESSAGE_CONTENT)


@bot.event
async def on_ready():
    LoadPartyManager(PM)
    print(PM.pingList)
    print("Bot is prepared!")

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
    name = str(ctx.author)
    if name not in PM.pingList:
        PM.pingList[name] = ctx.author.mention
        print("Added PingList:"% name)
    # if ctx.content in emote_dict:
    #     await ctx.send(emote_dict[ctx.content])




# Rice
@bot.command(
    name="auction",
    description="경매 입찰 값을 계산합니다",
    scope=GUILD,
    options = [
        interactions.Option(
            name="value",
            description="계산할 값",
            type=interactions.OptionType.INTEGER,
            required=True,
        ),
    ]
)
async def CommandRice(ctx: interactions.CommandContext, value: int):
    embeds = Rice(value)
    await ctx.send("", embeds=embeds)

# Luck
@bot.command(
    name="kuku",
    description="오늘의 쿠크세이튼 리트 확률을 알려드립니다.",
    scope=GUILD
)
async def CommandLuck(ctx: interactions.CommandContext):
    embeds = TodayLuck()
    await ctx.send("", embeds=embeds)

# Party Manager Functions

@bot.command(
    name="party_generate",
    description="파티를 결성합니다 (관리자용)",
    default_member_permissions=interactions.Permissions.ADMINISTRATOR,
    scope=GUILD,
    options = [
        interactions.Option(
            name="max_power",
            description="파티의 최대 딜량",
            type=interactions.OptionType.INTEGER,
            required=False
        ),
        interactions.Option(
            name="min_power",
            description="파티의 최소 딜량",
            type=interactions.OptionType.INTEGER,
            required=False
        ),
        interactions.Option(
            name="priority_power",
            description="우선 배정 딜러의 딜량",
            type=interactions.OptionType.INTEGER,
            required=False
        )
    ]
)
async def CommandPartyGenerate(ctx: interactions.CommandContext, max_power: float = 5.0, min_power: float = 4.0, priority_power: float = 3.0):
    embeds = PM.PartyGenerate(max_power, min_power, priority_power)
    SavePartyManager(PM)
    await ctx.send("", embeds=embeds)

@bot.command(
    name="party_reset",
    description="파티를 리셋합니다 (관리자용)",
    default_member_permissions=interactions.Permissions.ADMINISTRATOR,
    scope=GUILD
)
async def CommandPartyReset(ctx: interactions.CommandContext):
    embeds = PM.ResetParty()
    await ctx.send("", embeds=embeds)


@bot.command(
    name="party_call_everyone",
    description="모든 파티원을 호출합니다.",
    default_member_permissions=interactions.Permissions.ADMINISTRATOR,
    scope=GUILD
)
async def CommandPartyCallEveryone(ctx: interactions.CommandContext):
    msg = ""
    pl = []
    for i in PM.characters:
        pl.append(i.owner)
    pl = list(set(pl))
    for i in pl:
        msg += PM.pingList[i] + " "
    msg += "\n이번 주 쿠크세이튼 파티 목록입니다."
    embeds = PM.PartyList(False, None)
    await ctx.send(msg, embeds=embeds)

@bot.command(
    name="party_list",
    description="파티 목록을 보여줍니다",
    scope=GUILD,
    options = [
        interactions.Option(
            name="uncleared",
            description="참일 경우, 클리어 되지 않은 파티만 보여줍니다.",
            type=interactions.OptionType.BOOLEAN,
            required=False
        ),
        interactions.Option(
            name="owner",
            description="값을 입력할 경우, 해당 유저가 포함된 파티만 보여줍니다.",
            type=interactions.OptionType.USER,
            required=False
        ),
    ]
)
async def CommandPartyList(ctx: interactions.CommandContext, uncleared: bool = False, owner: interactions.Member = None):
    if owner is not None:
        owner = str(owner.user)
    embeds = PM.PartyList(uncleared, owner)
    await ctx.send("", embeds=embeds)

@bot.command(
    name="character_list",
    description="캐릭터 목록을 보여줍니다",
    scope=GUILD,
    options = [
        interactions.Option(
            name="owner",
            description="특정 유저의 캐릭터만 보여줍니다.",
            type=interactions.OptionType.USER,
            required=False
        ),
    ]
)
async def CommandCharacterList(ctx: interactions.CommandContext, owner: interactions.Member = None):
    if owner is not None:
        owner = str(owner.user)
    embeds = PM.CharacterList(owner)
    await ctx.send("", embeds=embeds)

@bot.command(
    name="character_add",
    description="캐릭터를 추가합니다",
    scope=GUILD,
    options = [
        interactions.Option(
            name="name",
            description="추가할 캐릭터의 이름",
            type=interactions.OptionType.STRING,
            required=True
        ),
        interactions.Option(
            name="role",
            description="추가할 캐릭터의 직업 (딜이 가능한 폿은 (딜폿)을 직업 뒤에 붙여주세요)",
            type=interactions.OptionType.STRING,
            required=True
        ),
        interactions.Option(
            name="owner",
            description="추가할 캐릭터의 소유자 (미입력시 자동으로 소유자는 자신입니다)",
            type=interactions.OptionType.USER,
            required=False
        ),
        interactions.Option(
            name="power",
            description="추가할 캐릭터의 딜량 (미입력시 자동으로 딜량은 1.0입니다)",
            type=interactions.OptionType.INTEGER,
            required=False
        ),
        interactions.Option(
            name="is_essential",
            description="파티에 필수 포함 여부 (미입력시 파티에 우선적으로 배정되도록 설정합니다)",
            type=interactions.OptionType.BOOLEAN,
            required=False
        )
    ]
)
async def CommandCharacterAdd(ctx: interactions.CommandContext, name: str, role: str, owner: interactions.Member = None, power: float = 1.0, is_essential: bool = True):
    if owner is None:
        owner = str(ctx.author.user)
    else:
        owner = str(owner.user)
    embeds = PM.AddCharacter(owner, name, role, is_essential, power)
    SavePartyManager(PM)
    await ctx.send("", embeds=embeds)

@bot.command(
    name="character_changeinfo",
    description="캐릭터의 정보를 변경합니다",
    scope=GUILD,
    options = [
        interactions.Option(
            name="name",
            description="변경할 캐릭터의 이름",
            type=interactions.OptionType.STRING,
            required=True
        ),
        interactions.Option(
            name="power",
            description="변경할 딜량",
            type=interactions.OptionType.NUMBER,
            required=False
        ),
        interactions.Option(
            name="is_essential",
            description="파티에 필수 포함 여부",
            type=interactions.OptionType.BOOLEAN,
            required=False
        ),
        interactions.Option(
            name="is_support",
            description="딜폿의 서포터 모드",
            type=interactions.OptionType.BOOLEAN,
            required=False
        )
    ]        
)
async def CommandCharacterChangeInfo(ctx: interactions.CommandContext, name: str, power: float = None, is_essential: bool = None, is_support: bool = None):
    embeds = PM.ChangeCharacterInfo(name, power, is_essential, is_support)
    SavePartyManager(PM)
    await ctx.send("", embeds=embeds)

@bot.command(
    name="character_remove",
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
    embeds = PM.RemoveCharacter(name)
    SavePartyManager(PM)
    await ctx.send("", embeds=embeds)

@bot.command(
    name="party_clear",
    description="파티를 클리어 처리합니다",
    scope=GUILD,
    options = [
        interactions.Option(
            name="number",
            description="클리어 처리할 파티의 번호",
            type=interactions.OptionType.INTEGER,
            required=True
        )
    ]
)
async def CommandSetPartyClear(ctx: interactions.CommandContext, number: int):
    embeds = PM.SetPartyClear(number, True)
    SavePartyManager(PM)
    await ctx.send("", embeds=embeds)

@bot.command(
    name="party_clear_cancel",
    description="클리어 처리한 파티를 취소 처리합니다",
    scope=GUILD,
    options = [
        interactions.Option(
            name="number",
            description="클리어 처리를 취소할 파티의 번호",
            type=interactions.OptionType.INTEGER,
            required=True
        )
    ]
)
async def CommandSetPartyClear(ctx: interactions.CommandContext, number: int):
    embeds = PM.SetPartyClear(number, False)
    SavePartyManager(PM)
    await ctx.send("", embeds=embeds)

@bot.command(
    name="party_call",
    description="파티 멤버를 호출합니다.",
    scope=GUILD,
    options = [
        interactions.Option(
            name="number",
            description="호출할 파티의 번호",
            type=interactions.OptionType.INTEGER,
            required=True
        )
    ]
)
async def CommandPartyCall(ctx: interactions.CommandContext, number: int):
    text, embeds = PM.PartyCall(number)
    await ctx.send(text, embeds=embeds)

@bot.command(
    name="party_join",
    description="파티에 캐릭터를 참여시킵니다",
    scope=GUILD,
    options = [
        interactions.Option(
            name="party",
            description="참여할 파티의 번호",
            type=interactions.OptionType.INTEGER,
            required=True,
        ),
        interactions.Option(
            name="character",
            description="참여할 캐릭터의 이름",
            type=interactions.OptionType.STRING,
            required=True,
        ),
    ]
)
async def CommandPartyJoin(ctx: interactions.CommandContext, party: int, character: str):
    embeds = PM.PartyJoin(party, character)
    SavePartyManager(PM)
    await ctx.send("", embeds=embeds)

@bot.command(
    name="party_leave",
    description="파티에서 캐릭터를 제거합니다",
    scope=GUILD,
    options = [
        interactions.Option(
            name="character",
            description="제거할 캐릭터의 이름",
            type=interactions.OptionType.STRING,
            required=True
        )
    ]
)
async def CommandPartyJoin(ctx: interactions.CommandContext, character: str):
    embeds = PM.PartyLeave(character)
    SavePartyManager(PM)
    await ctx.send("", embeds=embeds)

@bot.command(
    name="party_swap",
    description="파티원을 서로 교환합니다",
    scope=GUILD,
    options = [
        interactions.Option(
            name="name1",
            description="교환할 캐릭터의 이름",
            type=interactions.OptionType.STRING,
            required=True
        ),
        interactions.Option(
            name="name2",
            description="교환할 캐릭터의 이름",
            type=interactions.OptionType.STRING,
            required=True
        )
    ]
)
async def CommandPartySwap(ctx: interactions.CommandContext, name1: str, name2: str):
    embeds = PM.PartySwap(name1, name2)
    SavePartyManager(PM)
    await ctx.send("", embeds=embeds)

# Mahjong Commands

@bot.command(
    name="mahjong_playeradd",
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
    description="마작 점수를 기록합니다. 공탁금은 1등 플레이어에게 주세요",
    scope=GUILD,
    options = [
        interactions.Option(
            name="east_name",
            description="동 플레이어",
            type=interactions.OptionType.STRING,
            required=True
        ),
        interactions.Option(
            name="south_name",
            description="남 플레이어",
            type=interactions.OptionType.STRING,
            required=True
        ),
        interactions.Option(
            name="west_name",
            description="서 플레이어",
            type=interactions.OptionType.STRING,
            required=True
        ),
        interactions.Option(
            name="north_name",
            description="북 플레이어",
            type=interactions.OptionType.STRING,
            required=True
        ),
        interactions.Option(
            name="east_score",
            description="동 플레이어의 점수 (0점 기준 점수를 입력하세요)",
            type=interactions.OptionType.INTEGER,
            required=True
        ),
        interactions.Option(
            name="south_score",
            description="남 플레이어의 점수 (0점 기준 점수를 입력하세요)",
            type=interactions.OptionType.INTEGER,
            required=True
        ),
        interactions.Option(
            name="west_score",
            description="서 플레이어의 점수 (0점 기준 점수를 입력하세요)",
            type=interactions.OptionType.INTEGER,
            required=True
        ),
        interactions.Option(
            name="north_score",
            description="북 플레이어의 점수 (0점 기준 점수를 입력하세요)",
            type=interactions.OptionType.INTEGER,
            required=True
        ),
        interactions.Option(
            name="note",
            description="메모",
            type=interactions.OptionType.STRING,
            required=False
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
    description="마작 총합 랭킹을 표시합니다",
    scope=GUILD
)
async def CommandMahjongRecent(ctx: interactions.CommandContext):
    embeds = MS.ShowRanking()
    await ctx.send("", embeds=embeds)


bot.start()
