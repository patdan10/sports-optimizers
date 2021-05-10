from gurobipy import *
import sys
import csv

import wfteams

hardPlayers = wfteams.hardPlayers

def showdownModelMaker(players):
    
    length = len(players)
    #print(length)
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
    '''
    print()
    print()
    print()
    print("GAME")
    print(team1 + " VS. " + team2)
    print()
    '''
    for i in range(len(ourVars)):
        if ourVars[i].x >= .1:
            if "CPT" in ourVars[i].varName:
                player = players[int(i/2)]
                #print(player[0] + ", CPT, $" + str(int(int(player[2])*1.5)) + ", " + str(round(float(player[4])*1.5, 2)) + " PTS")
                optim.append((player[0], 1))
                money += int(player[2])*1.5
            else:
                player = players[int(i/2)]
                #print(player[0] + ", UTIL, $" + str(int(player[2])) + ", " + str(round(float(player[4]), 2)) + " PTS")
                optim.append((player[0], 0))
                money += int(player[2])

            #print()
    '''
    print("TOTAL POINTS: " + str(round(lineup.objVal,2)))
    print("TOTAL SALARY: " + str(int(money)))
    print()
    '''
    return optim
    
def classicModelMaker(players):
    length = len(players)
    lineup = Model("lbp")
    lineup.setParam('OutputFlag', 0)
    
    ts = []
    index = 1

    while True:
        #CHANGE BACK
        if len(players)/11 == len(ts):
            break
        
        if not players[index][4] in ts:
            ts.append(players[index][4])
        
        index += 1
    
    
    pos = ["F", "M/F", "M", "M/D", "D", "GK"]
    
    teams = [[[], [], [], [], [], []] for s in range(len(ts))]
    teamVars = [[[], [], [], [], [], []] for s in range(len(ts))]
    
    control = []
    
    for i in range(len(players)):
        cPos = pos.index(players[i][0])
        pTeam = ts.index(players[i][4])
        teams[pTeam][cPos].append(players[i])
        teamVars[pTeam][cPos].append(lineup.addVar(vtype=GRB.BINARY, name=players[i][1]))
        
        control.append(players[i])

    lineup.update()
    
    # 3 Teams constraint
    #lineup.addConstr(sum(or_(or_((teamVars[i][j][k]) for k in range(len(teamVars[i][j]))) for j in range(len(teamVars[i]))) for i in range(len(teamVars))), GRB.GREATER_EQUAL, 3, name="3teamcon")
    
    #sum(or_(or_((teamVars[i][j][k]) for k in range(len(teamVars[i][j]))) for j in range(len(teamVars[i]))) for i in range(len(teamVars)))
    '''
    counter = 0
    for i in range(len(teamVars)):
        if (sum(sum(teamVars[i][j][k] for k in range(len(teamVars[i][j]))) for j in range(len(teamVars[i]))) >= 1):
            counter += 1
    '''
    #lineup.addConstr(sum(sum(teamVars[3][j][k] for k in range(len(teamVars[3][j]))) for j in range(len(teamVars[3]))), GRB.GREATER_EQUAL, 1, name="3teamcon")
    
    # Money constraint
    lineup.addConstr(sum(sum(sum((teamVars[i][j][k] * teams[i][j][k][3]) for k in range(len(teamVars[i][j]))) for j in range(len(teamVars[i]))) for i in range(len(teamVars))), GRB.LESS_EQUAL, 50000.0, name="moneycon")
    
    # Position constraint    
    lineup.addConstr(sum(sum(teamVars[i][5][k] for k in range(len(teamVars[i][5]))) for i in range(len(teamVars))), GRB.EQUAL, 1, name="GKcon")
    
    lineup.addConstr(sum(sum(teamVars[i][0][k] for k in range(len(teamVars[i][0]))) for i in range(len(teamVars))), GRB.LESS_EQUAL, 3, name="Fcon")
    
    lineup.addConstr(sum(sum(teamVars[i][1][k] for k in range(len(teamVars[i][1]))) for i in range(len(teamVars))), GRB.LESS_EQUAL, 5, name="FMcon")
    
    lineup.addConstr(sum(sum(teamVars[i][2][k] for k in range(len(teamVars[i][2]))) for i in range(len(teamVars))), GRB.LESS_EQUAL, 3, name="Mcon")
    
    lineup.addConstr(sum(sum(teamVars[i][3][k] for k in range(len(teamVars[i][3]))) for i in range(len(teamVars))), GRB.LESS_EQUAL, 5, name="MDcon")
    
    lineup.addConstr(sum(sum(teamVars[i][4][k] for k in range(len(teamVars[i][4]))) for i in range(len(teamVars))), GRB.LESS_EQUAL, 3, name="Dcon")
    
    lineup.addConstr(sum(sum(teamVars[i][0][k] for k in range(len(teamVars[i][0]))) for i in range(len(teamVars))) + sum(sum(teamVars[i][1][k] for k in range(len(teamVars[i][1]))) for i in range(len(teamVars))), GRB.GREATER_EQUAL, 2, name="AllFconG")
    lineup.addConstr(sum(sum(teamVars[i][0][k] for k in range(len(teamVars[i][0]))) for i in range(len(teamVars))) + sum(sum(teamVars[i][1][k] for k in range(len(teamVars[i][1]))) for i in range(len(teamVars))), GRB.LESS_EQUAL, 5, name="AllFconL")
    
    lineup.addConstr(sum(sum(teamVars[i][1][k] for k in range(len(teamVars[i][1]))) for i in range(len(teamVars))) + sum(sum(teamVars[i][2][k] for k in range(len(teamVars[i][2]))) for i in range(len(teamVars))) + sum(sum(teamVars[i][3][k] for k in range(len(teamVars[i][3]))) for i in range(len(teamVars))), GRB.GREATER_EQUAL, 2, name="AllMconG")
    lineup.addConstr(sum(sum(teamVars[i][1][k] for k in range(len(teamVars[i][1]))) for i in range(len(teamVars))) + sum(sum(teamVars[i][2][k] for k in range(len(teamVars[i][2]))) for i in range(len(teamVars))) + sum(sum(teamVars[i][3][k] for k in range(len(teamVars[i][3]))) for i in range(len(teamVars))), GRB.LESS_EQUAL, 7, name="AllMconL")
    
    lineup.addConstr(sum(sum(teamVars[i][3][k] for k in range(len(teamVars[i][3]))) for i in range(len(teamVars))) + sum(sum(teamVars[i][4][k] for k in range(len(teamVars[i][4]))) for i in range(len(teamVars))), GRB.GREATER_EQUAL, 2, name="AllDconG")
    lineup.addConstr(sum(sum(teamVars[i][3][k] for k in range(len(teamVars[i][3]))) for i in range(len(teamVars))) + sum(sum(teamVars[i][4][k] for k in range(len(teamVars[i][4]))) for i in range(len(teamVars))), GRB.LESS_EQUAL, 5, name="AllDconL")
        
    lineup.addConstr(sum(sum(sum(teamVars[i][j][k] for k in range(len(teamVars[i][j]))) for j in range(len(teamVars[i]))) for i in range(len(teamVars))), GRB.EQUAL, 8, name="totalCon")
    
    
    
    # Objective function
    lineup.setObjective(sum(sum(sum((teamVars[i][j][k] * teams[i][j][k][5]) for k in range(len(teamVars[i][j]))) for j in range(len(teamVars[i]))) for i in range(len(teamVars))), GRB.MAXIMIZE)
        
    lineup.update()
    
    lineup.optimize()
    
    ourVars = lineup.getVars()
    money = 0
    optim = []
    points = 0
    
    for i in range(len(ourVars)):
        if (ourVars[i].x > 0.0):
            money += int(control[i][3])
            points += float(control[i][5])
            optim.append((control[i][1],0))
            print(control[i][0]+" "+control[i][1]+" "+control[i][4]+" "+control[i][3])
    
    print("TOTAL POINTS: " + str(points))
    print("TOTAL SALARY: " + str(money))
    
    return optim
    
    
    
    
    
    
    
    