
from ..kakul.utils import *

class Character:
    def __init__(self, owner, name, role, power, essential = True, active = True, isSupportMode = None):
        self.owner = owner
        self.name = name
        self.role = role
        self.power = power
        self.essential = essential
        self.active = active
        if isSupportMode is not None:
            self.isSupportMode = isSupportMode
        else:
            if "(폿)" in role or "(딜폿)" in role:
                self.isSupportMode = True
            else:
                self.isSupportMode = False
        
    def __repr__(self):
        v = "SUP" if self.isSupporter() else "%2.1f"%self.power
        return f"{self.name}({self.owner},{v})"

    def StrShort(self):
        ex = ":no_entry_sign:" if not self.active else ""
        v = ":plunger:" if not self.essential else ""
        axe = ":axe:" if self.role in ROLE_SUP_BOTH else ""
        rr = ROLE_ICON[ROLE_LIST.index(self.role)]
        if self.isSupporter():
            return f"{self.name} {rr}{axe} {v}{ex}"
        else:
            return f"{self.name} {rr}{axe} {v}{ex}"

    def GetIcon(self):
        axe = ":axe:" if self.role in ROLE_SUP_BOTH else ""
        return ROLE_ICON[ROLE_LIST.index(self.role)] + axe

    def GetIconStatus(self):
        ex = ":no_entry_sign:" if not self.active else ""
        v = ":plunger:" if not self.essential else ""
        return ex + v

    def StrOwner(self):
        ex = ",:no_entry_sign:" if not self.active else ""
        v = ",:plunger:" if not self.essential else ""
        return f"{self.name} ({self.owner}{v}{ex})"

    def StrFull(self):
        ex = ":no_entry_sign:" if not self.active else ""
        v = ":plunger:" if not self.essential else ""
        axe = ":axe:" if self.role in ROLE_SUP_BOTH else ""
        de = "%2.2f"%self.power
        rr = ROLE_ICON[ROLE_LIST.index(self.role)]
        if self.isSupporter():
            return f":fuelpump: `{de}` {self.name} {rr}{axe} ({self.owner}) {v}{ex}"
        else:
            return f"{GetPowerEmoji(self.power)} `{de}` {self.name} {rr}{axe} ({self.owner}) {v}{ex}"

    def GetPower(self, dealerSettingPower=False):
        if dealerSettingPower:
            return 0.0 if self.role in ROLE_SUP else self.power
        return 0.0 if self.isSupporter() else self.power
    
    def isSupporter(self):
        return True if self.role in ROLE_SUP or self.isSupportMode else False
    
    def isBoth(self):
        return True if self.role in ROLE_SUP_BOTH else False
        
    # equal
    def __eq__(self, other):
        if type(other) != type(self):
            return False
        return self.owner == other.owner and self.name == other.name and self.role == other.role
