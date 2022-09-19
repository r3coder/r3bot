
import interactions
import os
import pickle

db_base = "./data/bal/"


def LoadData(owner):
    with open(db_base + "users/" + owner, "rb") as f:
        data = pickle.load(f)
    return data

class BalanceManager:
    def __init__(self):
        pass
    
    def ShowBalance(self, owner):
        if not os.path.exists(db_base + owner):
            return "You have no balance."
        data = LoadData(owner)
        return "You have %d tokens." % data["tokens"]