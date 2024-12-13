import os
import time
import shutil
from datetime import datetime

import teamDictionary
months = teamDictionary.months
allTeams = teamDictionary.allTeams
elos = teamDictionary.elos

import dkScraper
DLCSV = dkScraper.dlcsv

import eloScraper
eloScraper = eloScraper.eloScraper

import teamNameGetters
SDTNG = teamNameGetters.showdownTeamNameGetter

import wfScraper
wfScrape = wfScraper.wf

import csvScrapersBefore
SDcsvBefore = csvScrapersBefore.showdownCsvScrape

import optimizers
SDOptimizer = optimizers.showdownModelMaker

import csvScrapersAfter
SDcsvAfter = csvScrapersAfter.showdownCsvAfterScrape
percentile = csvScrapersAfter.findPercentile

def makeLineup():
    average = 0.0
    successfulGames = 0
    #proactive games
    if input("Scrape active games or run retroactively? (P/R): ").lower() == "p":

        loc = os.path.join("C:\\","Users\Ben Yokoyama\Desktop\soccer\excellentcode","temp\\")
        os.mkdir(loc)
        contestType = "SHOWDOWN"
        if input("Showdown or Classic (S/C): ").lower() == "c":
            contestType = "CLASSIC"
        #rethink how to save information into teamsInfo, use teamNameGetter from the retroactive
        teamsInfo = DLCSV(loc, contestType)
        # give computer time to download
        time.sleep(3)
        counter = 1
        files = os.listdir(loc)
        print(teamsInfo)
        for f in files:
            if (teamsInfo[0][0] not in allTeams) or (teamsInfo[0][1] not in allTeams):
                counter+=1
                continue
            
            if counter == len(files):
                os.rename(r"C:\\Users\\Ben Yokoyama\\Desktop\\soccer\\excellentcode\\temp\\"+f,
                      r"C:\\Users\\Ben Yokoyama\\Desktop\\soccer\\excellentcode\\temp\\"+
                          teamsInfo[0][0].lower()+teamsInfo[0][1].lower()+teamsInfo[0][2][0]+"20.csv")        
            else:
                os.rename(r"C:\\Users\\Ben Yokoyama\\Desktop\\soccer\\excellentcode\\temp\\"+f,
                      r"C:\\Users\\Ben Yokoyama\\Desktop\\soccer\\excellentcode\\temp\\"+
                          teamsInfo[counter][0].lower()+teamsInfo[counter][1].lower()+teamsInfo[counter][2][0]+"20.csv")        
            counter+=1
            
        print(os.listdir(loc))
    #retroactive games
    else:
        if input("sample or run (S/R)").lower() == "s":
            loc = "./realsamples/"
        else:
            loc = "./run/"
    
    scoring = input("What scoring mechanism? (N/R/W) ").lower()
    if scoring == "r":
        scoring = "R"
    elif scoring == "w":
        scoring  = "W"
    else:
        scoring  = "N"
        
    teamElos = input("ELO? (Y/N) ").lower()
    if teamElos == "y":
        teamElos = "Y"
    else:
        teamElos = "N"
    
    files = os.listdir(loc)
    
    for f in files:
        if "after" in f:
            continue
        
        if "ipynb" in f:
            continue
        
        print(f)
        
        fileName = f.split(".")[0]
        date = []
        date.append(fileName[-6:-4])
        date.append(fileName[-4:-2])
        date.append(fileName[-2:])
        
        currLoc = loc + f
        teams = SDTNG(currLoc)
        #print(teams)
        teamAbbrs = [teams[0],teams[1]]
        
    #scrape wf for starters
        starters, teams = wfScrape(teams, date)
    #select scoring method
        #change the before scraper to allow for different mechanisms
    #csvscrapebefore with scrape of frbref
        #parse to datetime object
        date = date[2]+"20 "+months[date[0]]+" "+date[1]
        date = datetime.strptime(date, "%Y %b %d")
    
    #scrape elo
        eloWeights = [1,1]
        if teamElos == "Y":
            elo1 = eloScraper(elos[teamAbbrs[0]], date)
            elo2 = eloScraper(elos[teamAbbrs[1]], date)
            if elo1 > elo2:
                eloWeights[0] = float(elo1)/float(elo2)
            else:
                eloWeights[1] = float(elo1)/float(elo2)
        
            #print(elo1,elo2,eloWeights)
        
        players = SDcsvBefore(currLoc, starters, teams, date, scoring, eloWeights)

        if len(players) != 22:
            continue
    #optimize
        optim = SDOptimizer(players)
    #come up with way to pair before and after
        f = f.split(".csv")[0]+"after.csv"
        if f in files:

            currLoc = loc + f
            points = SDcsvAfter(currLoc, optim)
            place = percentile(currLoc, points)
            
            average += place
            successfulGames += 1.0
            
        print(average,successfulGames, round(average / successfulGames,6))
    
    if successfulGames != 0:
        print(round(average / successfulGames,6))


makeLineup()