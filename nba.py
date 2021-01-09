from gurobipy import *
import csv


def makeLineup():
    players = sheetScrape()
    modelMaker(players)
    
    


def sheetScrape():
    game = input("Name of game csv file OR drag and drop: ")
    if game[0] == "/":
        loc = game[:-1]
    else:
        loc = "/Users/patrick/Desktop/socxls/" + game

    utilPlayers = []

    info = [2, 4, 5, 7, 8]
    
    with open(loc) as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        print(reader)
        for row in reader:
            if row[info[1]] == "CPT" or row[0]=="Position":
                continue
            
                
            util = []
            
            for piece in info:
                util.append(row[piece])
            
            utilPlayers.append(util)
    
    
    
    
    return utilPlayers



def modelMaker(players):
    length = len(players)
    lineup = Model("lbp")
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
    #lineup.addConstr(sum(utilT1[i]) + sum(cptT1[i]) for i in range(length), GRB.GREATER_EQUAL, 1, name="t1con")
    lineup.addConstr(sum(utilT1[i] + cptT1[i] for i in range(len(utilT1))), GRB.GREATER_EQUAL, 1, name="t1con")
    

    # Team 2 constraint
    lineup.addConstr(sum(utilT2[i] + cptT2[i] for i in range(len(utilT2))), GRB.GREATER_EQUAL, 1, name="t2con")
    
    # Util constraint
    lineup.addConstr(sum(utilT1[i] for i in range(len(utilT1))) + sum(utilT2[i] for i in range(len(utilT2))), GRB.EQUAL, 5, "utilcon")
    
    # CPT constraint
    lineup.addConstr(sum(cptT1[i] for i in range(len(cptT1))) + sum(cptT2[i] for i in range(len(cptT2))), GRB.EQUAL, 1, "utilcon")
    
    # Money constraint
    lineup.addConstr(sum((utilT1[i] * t1[i][2]) + (cptT1[i] * t1[i][2] * 1.5) for i in range(len(utilT1))) + sum((utilT2[i] * t2[i][2]) + (cptT2[i] * t2[i][2] * 1.5) for i in range(len(utilT2))), GRB.LESS_EQUAL, 50000.0, "moneycon")
    
    # Individual constraint (need looping)
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
    print()
    print()
    
    for i in range(len(ourVars)):
        if ourVars[i].x == 1:
            if "CPT" in ourVars[i].varName:
                player = players[int(i/2)]
                print(player[0] + ", CPT, " + str(int(int(player[2])*1.5)) + ", " + str(round(float(player[4])*1.5, 2)))
                money += int(player[2])*1.5
            else:
                player = players[int(i/2)]
                print(player[0] + ", UTIL, " + str(int(player[2])) + ", " + str(round(float(player[4]), 2)))
                money += int(player[2])

            print()
    
    print("TOTAL POINTS: " + str(round(lineup.objVal,2)))
    print("TOTAL SALARY: " + str(int(money)))
    print()

makeLineup()
