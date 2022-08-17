

import os
import pickle
from manager import Party, Character

def SavePartyManager(M):
    # save parties to file
    with open('data_pinglist.pkl', 'wb') as save_file:
        pickle.dump(M.pingList, save_file)
    saveDict = dict()
    for i in M.characters:
        ess = 1 if i.essential else 0
        sup = 1 if i.isSupportMode else 0
        saveDict[i.name] = "%s|%s|%s|%s|%s|%s"%(i.owner, i.name, i.role, ess, str(i.power), sup)
    with open('data_characters.pkl', 'wb') as save_file:
        pickle.dump(saveDict, save_file)

    partyDict = dict()
    with open('data_partylist.pkl', 'wb') as save_file:
        for char in M.characters:
            partyDict[char.name] = M.GetPartyOfCharacter(char.name)
            partyDict["#party_count"] = len(M.parties)
            for i in range(len(M.parties)):
                if M.parties[i].isCleared():
                    partyDict["*"+str(i)] = 1
                else:
                    partyDict["*"+str(i)] = -1
        pickle.dump(partyDict, save_file)
    print("Save Complete")

def LoadPartyManager(M):
    if os.path.exists("data_pinglist.pkl"):
        with open('data_pinglist.pkl', 'rb') as save_file:
            M.pingList = pickle.load(save_file)
        # Temp code
        d = dict()
        for e, v in M.pingList.items():
            d[e.split("#")[0]] = v
        M.pingList = d

    M.parties = []
    M.characters = []
    saveDict = dict()
    if os.path.exists("data_characters.pkl"):
        with open('data_characters.pkl', 'rb') as save_file:
            saveDict = pickle.load(save_file)
    for i in saveDict:
        sv = saveDict[i].split("|")
        ess = True if sv[3] == "1" else False
        sup = True if sv[5] == "1" else False
        # sup = False
        # M.AddCharacter(sv[0], sv[1], sv[2], ess, float(sv[4])) # Temp code
        M.AddCharacter(sv[0].split("#")[0], sv[1], sv[2], ess, float(sv[4]), sup)
    
    partyDict = dict()
    if os.path.exists("data_partylist.pkl"):
        with open('data_partylist.pkl', 'rb') as save_file:
            partyDict = pickle.load(save_file)
        party_count = partyDict["#party_count"]
        del partyDict["#party_count"]
        for i in range(party_count):
            M.parties.append(Party())
        for k, v in partyDict.items():
            if k[0] == "*":
                if v == 1:
                    M.parties[int(k[1:])].cleared = True
                else:
                    M.parties[int(k[1:])].cleared = False
                continue
            if v == -1:
                M.leftovers.append(M.GetCharacterByName(k))
            else:
                M.parties[v].members.append(M.GetCharacterByName(k))

    print("Load Complete")
