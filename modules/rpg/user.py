

import json

db_base = "./data/rpg/"

class User:
    def __init__(self, name):
        self.name = name
        self.balance = 0


    def Save(self):
        data = {}
        data["name"] = self.name
        data["balance"] = self.balance
        
        with open(db_base + self.name, "w") as f:
            json.dump(d, f)