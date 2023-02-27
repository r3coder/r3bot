
class User:
    def __init__(self, name, ping, active, avoiddays):
        self.name = name
        self.active = active
        self.ping = ping
        self.avoiddays = avoiddays
    
    def __repr__(self):
        return f"{self.name} ({':o:' if self.active else ':x:'}, {self.ping}, {self.avoiddays})"

    def __eq__(self, other):
        if type(other) != type(self):
            return False
        return self.name == other.name and self.ping == other.ping and self.active == other.active

    def Characters(self, kpm):
        return [c for c in kpm.characters if c.owner == self.name]