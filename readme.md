# r3bot
This repository is personal discord bot using interactions.py
There's no limitation to use this code, but I don't sure if it works or not
This is meant to work on Linux machines

개인 서버에서 사용하는 다용도 디스코드 봇입니다.
사용에 딱히 제한은 없으나, 책임은 안 집니다.
리눅스 머신에서의 사용을 상정하고 만들어졌습니다.

# Install
## English
Put the `.env` file on same directory, and put the content as
```
DISCORD_TOKEN = Discord bot token
DISCORD_GUILD = Server number
```
Additionally, docker containers are recommended. Otherwise, install requirements on dockefile.
`docker build . -t lb:latest`

## 한국어
같은 디렉토리에 `.env` 파일을 추가하고 다음 내용을 적용해야 작동합니다.
```
DISCORD_TOKEN=[디스코드 봇 토큰]
DISCORD_GUILD=[서버 번호]
```
추가로, 도커 컨테이너를 만들어야 합니다.
`docker build . -t lb:latest`
도커 사용법은 [이 링크](https://docs.docker.com/engine/install/ubuntu/)를 참조하세요.
만일 도커를 사용하고 싶지 않다면, dockerfile에 있는 요구사항을 적당히 pip 같은 거로 설치해 주세요.
# 기능

현재 지원하는 기능은 다음과 같습니다.

## 미니 기능
- `/auction` : 기존 쌀산기 기능 (빠르게 입력하려면 /a 엔터 누르면 됩니다) (로스트 아크 경매 계산기)
- `/kuku` : 오늘의 운세(...?) 를 출력합니다.

## 쿠크세이튼 파티 자동편성 기능

4인 던전 "쿠크세이튼" 파티를 자동으로 편성해 줍니다.

- `/character_add` : 쿠크세이튼 풀에 캐릭터 추가
- `/character_changeinfo` : 쿠크세이튼 풀에 있는 캐릭터 정보 변경 (기존 딜량 설정, 필수 설정을 포함하는 기능)
- `/character_list` : 캐릭터 정보를 보여줍니다 (추가로 원하는 사람의 캐릭터 정보를 볼 수 있음)
- `/character_remove` : 쿠크세이튼 풀에서 캐릭터를 삭제합니다
- `/party_call` : 파티에 포함된 사람들을 호출합니다. (이제 파티에 어떤 캐릭터가 있는지 파티 정보를 포함해서 호출합니다)
- `/party_clear` : 해당 파티를 클리어 처리합니다
- `/party_clear_cancel` 실수로 클리어 처리한 파티를 취소합니다
- `/party_join` : 캐릭터를 파티에 참가시킵니다
- `/party_leave` : 캐릭터를 파티에서 제거합니다
- `/party_list` : 전체 파티 목록을 보여줍니다. 
- `/party_swap` : 파티 멤버를 교환합니다

서버 관리자 권한이 있다면, 다음과 같은 기능을 추가로 사용할 수 있습니다.
- `/party_generate` : 파티를 만듭니다 (파티 최대딜, 파티 최소딜, 우선 딜) 설정을 할 수 있습니다
- `/party_reset` : 파티를 초기화합니다
- `/party_call_everyone` : 파티 목록에 있는 모든 사람을 호출하고, 파티 내역을 보여줍니다

### 딜량에 대해
특정하게 어디서 데이터를 가져오는 건 아니고, 손으로 설정하면 됩니다.
```
0.5 = 6유물 안 나온 🚌 캐릭
1.0 = 무기 계승 전 20~21
1.5 = 무기 계승 전 20~21 / 무기 계승 후 ~13, 쿠크 세트 업글 완료, 주력기 7멸+
2.0 = 무기 계승 후 14~16강, 방어구 계승 완료
2.5 = 계승 후 17~19강, 고대악세 세팅 
3.0 = 계승 20~23강, 9멸+
3.5 = 계승 24강+, 카양겔 쿠크 업글 완료
직업에 따라 알아서 +- 0.2 정도 넣으셔도 상관 없음, 세구30이면 0.2~3 더하시면 됨. 세구18도 없으면 0.2~3 정도 빼면 됨
```

### 파티를 만드는 기능에 대해

파티는 다음과 같은 순서로 만들어집니다.
1. 우선 파티에 필수로 포함되는 캐릭터와 아닌 캐릭터를 분리합니다.
2. 인원수에 맞춰 파티의 개수를 만듭니다.
3. 서포터의 수를 조정합니다. 딜폿이 딜이 될 수도 있고, 필수로 포함하지 않은 캐릭터가 포함될 수 있습니다.
4. 4명이서 4개의 파티를 만들 수 있는지 검사하고, 가능할 경우 4개의 파티를 배정합니다. 이 때, 파티의 딜량은 평균치에서 크게 벗어나지 않도록 합니다.
5. 4명이서 2개의 파티를 만들 수 있는지 검사하고, 가능할 경우 2개의 파티를 배정합니다. 이 때, 파티의 딜량은 평균치에서 크게 벗어나지 않도록 합니다.
6. 남은 캐릭터들을 적당히 배치합니다.
7. 만일 남는 자리가 있다면, 필수로 배정될 필요가 없는 캐릭터를 배정합니다.

## 마작 점수 기록 기능
- `/mahjong_adduser`로 새 유저를 추가합니다.
- `/mahjong_score`로 새 점수 추가가 가능하며, 사람 이름을 동남서북 순서로 입력하고, 0점을 기준으로 +- 점수를 입력하면 됩니다. 마지막 추가 인자로 노트를 적을 수 있습니다
- `/mahjong_recent`로 최근 게임 정보를 확인 가능합니다
- `/mahjong_ranking`으로 현재 랭킹을 볼 수 있습니다.

## 품질작 시뮬레이터
- `/quality_upgrade`로 품질작 시뮬레이터를 열 수 있습니다. 
- 로스트 아크의 품질작과 동일하게 작동되며, 별도의 설정을 건드리지 않는다면 3600초에 하나씩 혼돈의 돌이 채워지고, 최대 72개까지 채워집니다.
- 품질 100을 달성할 경우, 티어를 다음 티어로 올릴 수 있으며, 이 때 품질은 리셋되고, 한 번 누르는데 들어가는 혼돈의 돌의 수가 늘어납니다.
- `/quality_rank`로 랭크를 볼 수 있습니다.