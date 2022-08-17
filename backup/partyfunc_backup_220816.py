 
import discord
from manager import Manager, Party, Character, ROLE_LIST

def PartyHelp():
   embed=discord.Embed(description="사용 가능한 메세지 목록입니다.", color=discord.Color.green())
   embed.add_field(name="캐릭터추가 [캐릭이름] [직업]", value="캐릭터 이름을 파티 풀에 추가합니다. (ca)\n 직업 리스트 : %s"%str(ROLE_LIST), inline=False)
   embed.add_field(name="캐릭터제거 [캐릭이름]", value="캐릭터 이름을 파티 풀에서 제거합니다. (cr)", inline=False)
   embed.add_field(name="캐릭터목록", value="현재 쿠크세이튼 풀에 있는 캐릭터 목록을 불러옵니다. (ll)", inline=False)
   embed.add_field(name="유저정보 \{유저이름\}", value="입력한 유저의 캐릭터와 파티가 결성되어 있다면 소속된 파티를 출력합니다. \n 만일 유저 이름을 입력하지 않을 경우, 메세지를 입력한 유저의 정보를 출력합니다.(u)", inline=False)
   embed.add_field(name="파티목록", value="현재 쿠크세이튼 파티 목록을 확인합니다. (파티, l)", inline=False)
   embed.add_field(name="파티호출 [파티번호]", value="[파티번호]번 파티 사람들을 호출합니다. (호출, p)", inline=False)
   embed.add_field(name="클리어 [파티번호]", value="남은 파티 조정을 위해서 클리어 후 이 명령어를 쳐 주세요. (cl)", inline=False)
   embed.add_field(name="클리어취소 [파티번호]", value="실수로 클리어를 입력했을 때, 이 명령어로 취소가 가능합니다. (취소, cc)", inline=False)
   embed.add_field(name="파티탈퇴 [캐릭이름]", value="파티에서 캐릭터를 제외시킵니다. 이미 클리어 된 파티는 변경이 불가능합니다. (탈퇴, x)", inline=False)
   embed.add_field(name="파티참여 [캐릭이름] [파티번호]", value="파티에 캐릭터를 참여시킵니다. 직업/폿유무 여부를 확인하지 않습니다. 이미 클리어 되었거나, 4명이 모두 차 있는 파티에는 참가 불가능합니다. (참여, i)", inline=False)
   embed.add_field(name="인원교체 [캐릭이름1] [캐릭이름2]", value="배정된 인원의 위치를 교환시킵니다. (교체, cn)", inline=False)
   embed.add_field(name="딜량설정 [캐릭이름] [값]", value="딜러의 세기를 설정합니다. 기본값은 1입니다. 딜폿은 딜로 표시될 때를 기준딜량으로 삼습니다. (cd)", inline=False)
   embed.add_field(name="필수설정 [캐릭이름] [예/아니오]", value="꼭 돌지 않아도 되는 캐릭을 표시할 수 있습니다. (ce)", inline=False)
   embed.add_field(name="파티결성", value="쿠크세이튼 파티를 결성합니다. 관리자만 사용할 수 있습니다. (ppp)", inline=False)
   return embed
