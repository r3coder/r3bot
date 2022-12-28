
import interactions
import os
import pickle

db_base = "./data/bal/"




def LoadData(owner):
    with open(db_base + "users/" + owner, "rb") as f:
        data = pickle.load(f)
    # Data Integrity Check
    if "golds" not in data:
        data["golds"] = 0
    return data

def SaveData(owner, data=None):
    if data is None:
        data = dict()
        data["golds"] = 0
    with open(db_base + "users/" + owner, "wb") as f:
        pickle.dump(data, f)

class BalanceManager:
    def __init__(self):
        pass
    
    def ShowBalance(self, owner):
        if not os.path.exists(db_base + owner):
            SaveData(owner)
        data = LoadData(owner)
        embed = interactions.Embed(title="%s님의 잔고" % owner, description="현재 잔고: %d" % data["golds"])        
        return embed
    
    def AddGold(self, owner, amount):
        if not os.path.exists(db_base + owner):
            SaveData(owner)
        data = LoadData(owner)
        data["golds"] += amount
        SaveData(owner, data)
        if amount > 0:
            embed = interactions.Embed(description="%s님에게 %d원을 추가해 현재 잔고는 %d 원입니다." % (owner, amount, data["golds"]))
        else:
            embed = interactions.Embed(description="%s님에게 %d원을 차감해 현재 잔고는 %d 원입니다." % (owner, -amount, data["golds"]))
        return embed