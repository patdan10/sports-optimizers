from gurobipy import *
import sys
import csv

def modelMaker(players, no):
    length = len(players)
    lineup = Model("lbp")
    lineup.setParam('OutputFlag', 0)
    cptT1 = []
    utilT1 = []
    
    cptT2 = []
    utilT2 = []
    
    t1 = []
    t2 = []
    
    index = 1
    team1 = players[0][3]
    team2 = ""
    
    while True:
        if players[index][3] != team1:
            team2 = players[index][3]
            break
        
        index += 1
    
    
    for i in range(len(players)):
        if players[i][3] == team1:
            utilT1.append(lineup.addVar(vtype=GRB.BINARY, name=players[i][0] + " UTIL"))
            cptT1.append(lineup.addVar(vtype=GRB.BINARY, name=players[i][0] + " CPT"))
            t1.append(players[i])
        else:
            utilT2.append(lineup.addVar(vtype=GRB.BINARY, name=players[i][0] + " UTIL"))
            cptT2.append(lineup.addVar(vtype=GRB.BINARY, name=players[i][0] + " CPT"))
            t2.append(players[i])

    lineup.update()
    
    # Team 1 constraint
    lineup.addConstr(sum(utilT1[i] + cptT1[i] for i in range(len(utilT1))), GRB.GREATER_EQUAL, 1, name="t1con")
    

    # Team 2 constraint
    lineup.addConstr(sum(utilT2[i] + cptT2[i] for i in range(len(utilT2))), GRB.GREATER_EQUAL, 1, name="t2con")
    
    # Util constraint
    lineup.addConstr(sum(utilT1[i] for i in range(len(utilT1))) + sum(utilT2[i] for i in range(len(utilT2))), GRB.EQUAL, 5, "utilcon")
    
    # CPT constraint
    lineup.addConstr(sum(cptT1[i] for i in range(len(cptT1))) + sum(cptT2[i] for i in range(len(cptT2))), GRB.EQUAL, 1, "utilcon")
    
    # Money constraint
    lineup.addConstr(sum((utilT1[i] * t1[i][2]) + (cptT1[i] * t1[i][2] * 1.5) for i in range(len(utilT1))) + sum((utilT2[i] * t2[i][2]) + (cptT2[i] * t2[i][2] * 1.5) for i in range(len(utilT2))), GRB.LESS_EQUAL, 50000.0, "moneycon")
    
    # Individual constraint
    for i in range(len(utilT1)):
        lineup.addConstr(utilT1[i] + cptT1[i], GRB.LESS_EQUAL, 1, "X")
   
    for i in range(len(utilT2)):
        lineup.addConstr(utilT2[i] + cptT2[i], GRB.LESS_EQUAL, 1, "Y")
        
    # Objective Function
    lineup.setObjective(sum((utilT1[i] * t1[i][4]) + (cptT1[i] * t1[i][4] * 1.5) for i in range(len(utilT1))) + sum((utilT2[i] * t2[i][4]) + (cptT2[i] * t2[i][4] * 1.5) for i in range(len(utilT2))), GRB.MAXIMIZE)
    lineup.update()
    
    lineup.optimize()
    
    ourVars = lineup.getVars()
    money = 0
    optim = []
    print()
    print()
    print()
    print("GAME " + str(no))
    print(team1 + " VS. " + team2)
    print()
    
    for i in range(len(ourVars)):
        if ourVars[i].x == 1:
            if "CPT" in ourVars[i].varName:
                player = players[int(i/2)]
                print(player[0] + ", CPT, $" + str(int(int(player[2])*1.5)) + ", " + str(round(float(player[4])*1.5, 2)) + " PTS")
                optim.append((player[5], 1))
                money += int(player[2])*1.5
            else:
                player = players[int(i/2)]
                print(player[0] + ", UTIL, $" + str(int(player[2])) + ", " + str(round(float(player[4]), 2)) + " PTS")
                optim.append((player[5], 0))
                money += int(player[2])

            print()
    
    print("TOTAL POINTS: " + str(round(lineup.objVal,2)))
    print("TOTAL SALARY: " + str(int(money)))
    
    
    
    print()
    
    return optim
    

#JUST FOR SINGLE CSV TESTING, NO CHROMEDRIVER
def csvScrape():
    
    loc = input("PUT IN CSV: ")
    loc = loc[:-1]

    utilPlayers = []

    info = [9, 11, 12, 14, 15, 10]
    
    with open(loc, encoding='mac_roman') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        counter = 0
        
        for row in reader:
            if counter < 8:
                counter += 1
                continue
                
            if row[info[1]] == "CPT":
                continue
            
                
            util = []
            
            for piece in info:
                util.append(row[piece])
            
            utilPlayers.append(util)
    
    
    return utilPlayers

if __name__ == "__main__":
    modelMaker(csvScrape(), 1)
