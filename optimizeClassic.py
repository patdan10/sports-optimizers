from gurobipy import *
import sys
import csv
import teams as info
import requests
from bs4 import BeautifulSoup

hardNames = info.hardNames

# POS, NAME, ID, SAL, TEAM, FPTS

def modelMaker(players, no):
    length = len(players)
    lineup = Model("lbp")
    lineup.setParam('OutputFlag', 0)
    
    ts = []
    index = 1
    
    while True:
        #CHANGE BACK
        if len(players)/11 == len(ts):
            break
        
        """if len(ts) == 4:
            break"""
        
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
    
    
    # SUM[ OR[OR["F", "F2"], OR["M", "M2"], OR["MD", "MD2"], OR["D", "D2"], OR["GK", "GK2"]], [["F", "F2"], ["M", "M2"], ["MD", "MD2"], ["D", "D2"], ["GK", "GK2"]]]
    # TEAM, POS, PLAYER for team, for pos, for play
    
    counter = 0
    
    """for i in range(len(teams)):
        #for j in range(len(teams[i])):
        for k in range(len(teams[i][5])):
            print(teamVars[i][5][k])"""
    
    # 3 Teams constraint
    #lineup.addConstr(quicksum(or_(or_(teamVars[i][j]) for j in range(len(teamVars[i]))) for i in range(len(teamVars))), GRB.GREATER_EQUAL, 3, name="3teamcon")
    
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
    
    
    """
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
    """
    
    
    lineup.update()
    
    lineup.optimize()
    
    ourVars = lineup.getVars()
    money = 0
    points = 0
    optim = []
    
    for i in range(len(ourVars)):
        if (ourVars[i].x > 0.0):
            money += int(control[i][3])
            points += float(control[i][5])
            print(control[i][0]+" "+control[i][1]+" "+control[i][4]+" "+control[i][3])
    
    
    print("TOTAL POINTS: " + str(points))
    print("TOTAL SALARY: " + str(money))
    
    return optim
    






#JUST FOR SINGLE CSV TESTING, NO CHROMEDRIVER
def csvScrape(starters):
    loc = input("CSV FILE: ")
    loc = loc[:-1]

    utilPlayers = []

    info = [9, 11, 12, 14, 16, 17]
    
    with open(loc, encoding='mac_roman') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        counter = 0
        
        for row in reader:
            if counter < 8:
                counter += 1
                continue
            
            if row[11][0] == " ":
                row[11] = row[11][1:]
            
            if  row[11] in hardNames:
                row[11] = hardNames[row[11]]
            
            if (not row[11] in starters):
                continue
              
            util = []
            
            for piece in info:
                util.append(row[piece])
            
            utilPlayers.append(util)
    
    return utilPlayers



def squadScrape(date, cLeague):
    league = ""
    
    if cLeague == 'Bundesliga':
        league = '?league=BUND'
    elif cLeague == 'LIGA':
        league = '?league=LIGA'
    
    urlRef = "https://www.rotowire.com/soccer/lineups.php" + league
    ref = requests.get(urlRef)
    soupRef = BeautifulSoup(ref.content, features="html.parser")
    
    teams = soupRef.find_all('div', {'class': 'lineup is-soccer'})
    
    gameDay = date[0][3:]
    gameTime = date[1].split(":")
    
    starters = []
    totalGames = 0
    gamesNeeded = int(date[3][1])
    
    for i in teams:
        info = i.find_all('div', {'class': 'lineup__time'})[0].get_text().split(" ")
        day = info[1][:-1]
        time = info[2].split(":")
        
        if (int(gameDay) == int(day) and (totalGames < gamesNeeded)):
            if int(gameTime[0]) == int(time[0]): 
                for play in i.find_all('li', {'class': 'lineup__player'}):
                    starters.append(play.find_all('a')[0]['title'])
                totalGames += 1
            elif (totalGames == 0):
                continue
            else:
                for play in i.find_all('li', {'class': 'lineup__player'}):
                    starters.append(play.find_all('a')[0]['title'])
                totalGames += 1
                
                
    
    return starters


if __name__ == "__main__":
    date = ["06/18", "1:30", "pm", "(2)"]
    leag = "LIGA"
    start = squadScrape(date, leag)
    players = csvScrape(start)
    print(len(players))
    modelMaker(players, 1)
