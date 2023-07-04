
import json

class AliasManager:
    def __init__(self):
        self.aliases = {}
        # load aliases from file
        self.load()
    

    def AddAlias(self, alias, name):
        if alias not in self.aliases:
            self.aliases[alias] = name
            self.save()
            return True

    def load(self):
        try:
            with open('data/aliases.json', 'r') as f:
                self.aliases = json.load(f)
        except FileNotFoundError:
            pass

    def save(self):
        with open('data/aliases.json', 'w') as f:
            json.dump(self.aliases, f, indent=4)
