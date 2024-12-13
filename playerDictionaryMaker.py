# "DK name": ["WF name", "pid"]
import fbrefIDs
ids = fbrefIDs.ids

import wfteams
names = wfteams.hardPlayers

for key in ids:
    dkName = key
    wfName = key
    if key in names:
        wfName = names[key]
    
    print('"'+dkName+'"'+': ["'+wfName+'", "'+ids[key]+'"],')
        
    