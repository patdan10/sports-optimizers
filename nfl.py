from bs4 import BeautifulSoup
#from gurobipy import *
import csv
import requests
import sys
import os
import shutil
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

nflNames = ['TB', 'NE']

def makeLineup():
    # scrape csv for team names only
    # scrape web for lineup using team names
    # scrape csv again for only used players
    
        
    loc = "/Users/patrick/Desktop/nflxls/temp"
    os.mkdir(loc)
    
    dlcsv(loc)
    
    time.sleep(1)
    
    
    files = os.listdir(loc)
    
    for f in files:
        if f[0] == '.':
            continue
        teams = getTeams(loc+"/"+f)
        
        if (teams == "NO"):
            continue
        
        #starters = squadScrape(teams)
    
        players = csvScrape(loc+"/"+f)
        
        print("NEWGAME")
        
        
    shutil.rmtree(loc)
    
    
    
    
    
    
    #optimize.modelMaker(players)


def getTeams(loc):
    teams = []
    with open(loc, encoding='mac_roman') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        counter = 0
        for row in reader:
            if counter < 8:
                counter += 1
                continue
            
            teams = row[13]
            break
    
    teams = teams.split(" ")
    teams = teams[0].split("@")
    
    if (not teams[0] in nflNames) or (not teams[1] in nflNames):
        return "NO"
    
    return [teams[0], teams[1]]





def squadScrape(teams):
    team1 = teams[0]
    team2 = teams[1]
    
    urlRef = "https://www.rotowire.com/soccer/lineups.php?league=BUND"
    ref = requests.get(urlRef)
    soupRef = BeautifulSoup(ref.content, features="html.parser")
    
    teams = soupRef.find_all('div', {'class': 'lineup is-soccer'})
    
    for i in teams:
        abbrs = i.find_all('div', {'class': 'lineup__abbr'})
        
        if (abbrs[0].get_text(strip=True) == team1 and abbrs[1].get_text(strip=True) == team2) or (abbrs[0].get_text(strip=True) == team2 and abbrs[1].get_text(strip=True) == team1):
            starters = []
            
            for play in i.find_all('li', {'class': 'lineup__player'}):
                starters.append(play.get_text(strip=True).split(" ")[-1])
        
    
    return starters
    



def csvScrape(loc):

    utilPlayers = []

    info = [9, 11, 12, 14, 15]
    
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
    
    
    
    for guy in utilPlayers:
        for stat in guy:
            print(stat)
    
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
    
    
def dlcsv(loc):
    chrome_options = webdriver.ChromeOptions()
    prefs = {'download.default_directory' : loc}
    chrome_options.add_experimental_option('prefs', prefs)
    
    driver = webdriver.Chrome(executable_path = '/opt/anaconda3/bin/chromedriver', options=chrome_options)
    driver.get("https://www.draftkings.com/account/sitelogin/false?returnurl=%2Flobby")

    driver.implicitly_wait(2)


    #USERNAME AND PASSWORD
    driver.find_element_by_name("username").send_keys('patdan10')
    driver.find_element_by_name("password").send_keys('Bluedog1')

    #LOG IN
    log = driver.find_element_by_xpath("/html/body/section[1]/section/section[2]/div[3]/button")
    log.click()

    #WAIT FOR LOG IN
    WebDriverWait(driver, 400).until(
        EC.presence_of_element_located((By.XPATH, "/html/body/header/div/div[1]/div/header/div/div[2]/div[2]/nav/a[2]"))
    )


    #LINEUP
    driver.get("https://www.draftkings.com/lineup/upload")

    #DROPDOWN
    WebDriverWait(driver, 400).until(
        EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div[2]/div[1]/div/div[1]/a"))
    )

    menu = driver.find_element_by_xpath("/html/body/div[1]/div[2]/div[1]/div/div[1]/a")
    menu.click()

    #SOC
    WebDriverWait(driver, 400).until(
        EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div[2]/div[1]/div/div[1]/ul"))
    )

    spos = driver.find_element_by_xpath("/html/body/div[1]/div[2]/div[1]/div/div[1]/ul")
    sports = spos.find_elements_by_tag_name("li")
    
    for s in sports:
        anc = s.find_elements_by_tag_name("a")
        if anc[0].text == "NFL":
            anc[0].click()
            break


    #SHOWDOWN DROPDOWN
    show = driver.find_element_by_xpath("/html/body/div[1]/div[2]/div[1]/div/div[2]/a")
    show.click()
    
    WebDriverWait(driver, 400).until(
        EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div[2]/div[1]/div/div[2]/ul"))
    )

    #CLICK SHOWDOWN
    down = driver.find_element_by_xpath("/html/body/div[1]/div[2]/div[1]/div/div[2]/ul")
    options = down.find_elements_by_tag_name("li")
    
    for opt in options:
        anc2 = opt.find_elements_by_tag_name("a")
        if anc2[0].text == "SHOWDOWN CAPTAIN MODE":
            anc2[0].click()
            break


    #GAMES
    listGames = driver.find_element_by_xpath("/html/body/div[1]/div[2]/div[1]/div/ul")
    games = listGames.find_elements_by_tag_name("li")
    dl = driver.find_element_by_xpath("/html/body/div[1]/div[2]/div[1]/div/a")

    for g in games:
        g.click()
        dl.click()
    
    return len(games)


makeLineup()
