import csv
import unidecode
import math

import teamDictionary
allTeams = teamDictionary.allTeams

import playerDictionary
players = playerDictionary.players

import fbrefScraper
scrape = fbrefScraper.playerScraper

import fbrefScraperWeights
weightScrape = fbrefScraperWeights.playerScraper

'''
Scrapes showdown CSV file once we have found starters in order to bring in the necessary information
Returns players and their information in nested array
'''
def showdownCsvScrape(loc, starters, teams, date, scoring, elos):
    # Create a temp list with all the names to see if anyone doesn't get found
    whos_left = []
    for i in range(len(starters)):
        whos_left.append(starters[i])
        
    # Initialize overall nested list
    utilPlayers = []

    # which columns to collect from
    info = [9, 11, 12, 14, 15, 10]
    
    with open(loc, encoding='mac_roman') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        counter = 0
        
        for row in reader:
            #ignore top rows
            if counter < 8:
                counter += 1
                continue
            #ignore captains
            if row[info[1]] == "CPT":
                continue
            #ignore spaces
            if row[9][0] == ' ':
                row[9] = row[9][1:]
            
            row[9] = unidecode.unidecode(row[9])
            
            #filter by team to maintain order
            if allTeams[row[14]] == teams[0]:
                #find players who aren't in starters
                #check dictionary for dk name
                if (not row[9] in players):
                    #print(row[9], "DK name")
                    continue
                #check validity of WF name
                if (not players[row[9]][0] in starters[0:11]):
                    #print(row[9], "WF name")
                    continue
            #team 2
            if allTeams[row[14]] == teams[1]:
                #check dictionary for dk name
                if (not row[9] in players):
                    #print(row[9], "DK name")
                    continue
                if (not players[row[9]][0] in starters[11:]):
                    #print(row[9], "WF name")
                    continue
            
            #Remove from temp list because player has been found
            if players[row[9]][0] in whos_left:
                whos_left.remove(players[row[9]][0])
            
            #select mechanism
            if scoring == "R":
                pid = players[row[9]][1]
                row[15] = scrape(pid, row[7], date)
                print(row[9], row[15])
            if scoring == "W":
                pid = players[row[9]][1]
                row[15] = weightScrape(pid, row[7], date)
                print(row[9], row[15])
            
            #multiply by Elo multiplier
            if allTeams[row[14]] == teams[0]:
                row[15] = float(row[15])*elos[0]
            if allTeams[row[14]] == teams[1]:
                row[15] = float(row[15])*elos[1]
            
            # instance of the player
            util = []
            for piece in info:
                util.append(row[piece])
            
            utilPlayers.append(util)
    
    # if starters are left in the temp list, not every starter was found
    if len(whos_left) != 0:
        print(whos_left)
    return utilPlayers

'''
Scrapes classic CSV file once we have found starters in order to bring in the necessary information
Returns players and their information in nested array
'''
def classicCsvScrape(loc, starters, teams):
    # Create a temp list with all the names to see if anyone doesn't get found
    whos_left = []
    for i in range(len(starters)):
        whos_left.append(starters[i])
        
    # Initialize overall nested list
    utilPlayers = []

    # which columns to collect from
    info = [9, 11, 12, 14, 16, 17]
    
    with open(loc, encoding='mac_roman') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        counter = 0
        
        for row in reader:
            #ignore top rows
            if counter < 8:
                counter += 1
                continue
            #ignore spaces
            if row[11][0] == ' ':
                row[11] = row[11][1:]
                
            if teams.index(allTeams[row[16]]) == len(teams)-1:
                if (not row[11] in starters[teams.index(allTeams[row[16]])*11:]):
                    if row[11] in hardPlayers:
                        if (not hardPlayers[row[11]] in starters[teams.index(allTeams[row[16]])*11:]):
                            continue
                    else:
                        continue
            else:
                if (not row[11] in starters[teams.index(allTeams[row[16]])*11:teams.index(allTeams[row[16]])*11+12]):
                    if row[11] in hardPlayers:
                        if (not hardPlayers[row[11]] in starters[teams.index(allTeams[row[16]])*11:teams.index(allTeams[row[16]])*11+12]):
                            continue
                    else:
                        continue
            
            #Remove from temp list because player has been found
            if row[11] in whos_left:
                whos_left.remove(row[11])
            elif row[11] in hardPlayers:
                if hardPlayers[row[11]] in whos_left:
                    whos_left.remove(hardPlayers[row[11]])
                
            # instance of the player
            util = []
            for piece in info:
                util.append(row[piece])
            
            utilPlayers.append(util)
    
    # if starters are left in the temp list, not every starter was found
    if len(whos_left) != 0:
        print(whos_left)
    return utilPlayers