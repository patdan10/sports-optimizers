from gurobipy import *
import xlrd


def makeLineup():
    players = sheetScrape()
    modelMaker(players)
    
    


def sheetScrape():
    loc = "/Users/patrick/Desktop/utator.xls"

    wb = xlrd.open_workbook(loc)

    sheet = wb.sheet_by_index(0)

    utilPlayers = []

    info = [9, 11, 12, 14, 15]

    for row in range(sheet.nrows)[8:]:
        if sheet.cell_value(row, info[0]) == xlrd.empty_cell.value:
            break
        
        if sheet.cell_value(row, info[1]) == "CPT":
            continue
        
            
        util = []
        
        for piece in info:
            util.append(sheet.cell_value(row,piece))
        
        utilPlayers.append(util)
    
    return utilPlayers



def modelMaker(players):
    length = len(players)
    lineup = Model("lbp")
    cptT1 = {}
    utilT1 = {}
    
    cptT2 = {}
    utilT2 = {}
    
    
    index = 1
    team1 = players[0][3]
    team2 = ""
    while True:
        if players[index][3] != team1:
            team2 = players[index][3]
            break
        
        index += 1
    
    
    print(team1, team2)
    
    
    for i in range(len(players)):
        if players[i][3] == team1:
            utilT1[players[i][0] + " UTIL"] = lineup.addVar(vtype=GRB.BINARY, name=players[i][0] + " UTIL")
            cptT1[players[i][0] + " CPT"] = lineup.addVar(vtype=GRB.BINARY, name=players[i][0] + " CPT")
        else:
            utilT2[players[i][0] + " UTIL"] = lineup.addVar(vtype=GRB.BINARY, name=players[i][0] + " UTIL")
            cptT2[players[i][0] + " CPT"] = lineup.addVar(vtype=GRB.BINARY, name=players[i][0] + " CPT")

    lineup.update()
    
    # Team 1 constraint
    #lineup.addConstr(sum(utilT1[i]) + sum(cptT1[i]) for i in range(length), GRB.GREATER_EQUAL, 1, name="t1con")
    lineup.addConstr(sum(utilT1[players[i][0] + " UTIL"] + cptT1[players[i][0] + " CPT"] for i in range(length)), GRB.GREATER_EQUAL, 1, name="t1con")
    
    # Team 2 constraint
    #lineup.addConstr(sum(utilT2[i]) + sum(cptT2[i]) for i in range(length), GRB.GREATER_EQUAL, 1, name="t2con")
    
    # Util constraint
    #lineup.addConstr(sum(utilVars[i]) for i in range(len(players)), GRB.EQUAL, 5, "utilcon")
    
    # CPT constraint
    #lineup.addConstr(sum(cptVars[i]) for i in range(len(players)), GRB.EQUAL, 1, "cptcon")
    
    # Money constraint
    #lineup.addConstr(sum(utilVars[i] * players[i][2]) + sum(cptVars[i] * players[i][2] * 1.5) for i in range(len(players)), GRB.LESS_EQUAL, 50000.0, "moneycon")
    
    # Individual constraint (need looping)
    # model.addConstrs((utilVars.sum() == 1
                  #for i in range(n)
                  #for j in range(n)), name='V') 
    
    print(lineup)

makeLineup()

"""m = Model("mip1")

x = m.addVar(vtype=GRB.BINARY, name='x')
y = m.addVar(vtype=GRB.BINARY, name='y')
z = m.addVar(vtype=GRB.BINARY, name='z')
m.update()

m.setObjective(x + y + 2 * z, GRB.MAXIMIZE)

m.addConstr(x + 2 * y + 3 * z <= 4, 'c0')
m.addConstr(x + y >= 1, 'c1')

m.optimize()
m.printAttr('X')"""
