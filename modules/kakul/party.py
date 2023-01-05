
from ..kakul.utils import printl, GetRoleRaw

class Party:
    def __init__(self, idx=0):
        self.members = []
        self.cleared = False
        self.idx = idx

    def isOwnerExists(self, owner):
        for member in self.members:
            if member.owner == owner:
                return True
        return False
    
    def isRoleExists(self, role):
        for member in self.members:
            if GetRoleRaw(member.role) == GetRoleRaw(role):
                return True
        return False
    
    def isRoleDupe(self):
        s = []
        for member in self.members:
            s.append(GetRoleRaw(member.role))
        s = set(s)
        if len(self.members) != len(s):
            return True
        return False

    def isFull(self):
        if len(self.members) == 4:
            return True
        return False
    
    def isNameExists(self, name):
        for member in self.members:
            if member.name == name:
                return True
        return False

    def isSupporterExists(self):
        for member in self.members:
            if member.isSupporter():
                return True
        return False

    def GetPartyPower(self):
        f = 0
        for member in self.members:
            f += member.GetPower()
        return f

    def GetPartyOwnerString(self):
        v = []
        for member in self.members:
            v.append(member.owner)
        v.sort()
        return ", ".join(v)

    def AddCharacter(self, character, strict=True, verbose=False):
        if character in self.members:
            if verbose:
                printl(f"Character {character.name} already in party {self.idx}")
            return False
        if len(self.members) >= 4:
            if verbose:
                printl(f"Party {self.idx} is full")
            return False
        if self.isOwnerExists(character.owner):
            if verbose:
                printl(f"Party {self.idx} already has a {character.owner}")
            return False
        if strict:
            if self.isRoleExists(character.role):
                if verbose:
                    printl(f"(Strict) Party {self.idx} already has a {character.role}")
                return False
            if self.isSupporterExists() and character.isSupporter():
                if verbose:
                    printl(f"(Strict) Party {self.idx} already has a supporter")
                return False
        self.members.append(character)
        if verbose:
            printl("Party member added")
        return True

    def RemoveCharacter(self, character):
        if character not in self.members:
            printl(f"Character {character} not in party {self.idx}")
            return False
        self.members.remove(character)

    def isPartyFull(self):
        return len(self.members) == 4
    
    def isCleared(self):
        return self.cleared

    def __repr__(self):
        v = ":o:" if self.cleared else ":x:"
        s = "파티 %d: %2.2f %d/4 "%(self.idx+1, self.GetPartyPower(), len(self.members))+ v + " ["
        for member in self.members:
            s += member.StrShort() + ", "
        s = s[:-2] + "]"
        return s
    
    def OwnerStr(self):
        str = ""
        for member in self.members:
            str += member.owner + ", "
        return str[:-2]

    def ShortStr(self):
        v = ":o:" if self.cleared else ":x:"
        s01 = "`서폿없음`" if self.isSupporterExists() == False else " "
        s02 = "`인원부족`" if len(self.members) < 4 else " "
        s = "`#%d` 딜량:`%2.2f` 클리어: %s %s%s"%(self.idx+1, self.GetPartyPower(), v, s01, s02) + "\n"
        for member in self.members:
            s += member.StrShort() + ", "
        s = s[:-2]
        return s

    def StrFull(self):
        v = ":o:" if self.cleared else ":x:"
        s = "인원:%d/4, 딜량:%2.2f, 클리어:%s\n"%(len(self.members), self.GetPartyPower(), v)
        for member in self.members:
            s += "  " + member.StrFull() + "\n"
        return s
    
    def Embed(self):
        embed = interactions.Embed(title=f"파티 {self.idx}", description=self.__repr__())

    
