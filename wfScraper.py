from bs4 import BeautifulSoup
import requests
import datetime
import unidecode
import time

import teamDictionary
allTeams = teamDictionary.allTeams
months = teamDictionary.months



def runner(team1, team2, day):    
    day[0] = day[0].split("/")
    
    day[1] = int(day[1].split(":")[0])
    if day[2] == 'pm' and day[1] != 12:
        day[1] = day[1] + 12
    
    date_time_str = day[0][1]+ "/" + day[0][0] + "/20 " + str(day[1]) + ":00:00"
    print(date_time_str)
    date_time_obj = datetime.datetime.strptime(date_time_str, '%d/%m/%y %H:%M:%S')
    
    hours = 5
    hours_added = datetime.timedelta(hours = hours)
    
    real_time = str(date_time_obj + hours_added)
    
    real_time = real_time.split(" ")[0]
    real_time = real_time.split("-")
    real_time[1] = months[real_time[1]]
    today = real_time[0]+"/"+real_time[1]+"/"+real_time[2]+"/"

    #if input("Custom day? y/n ") == "y":
    #    today = input("Day: ")
    
    url = wf(team1, team2, today)
    if (url == False):
        return False
    if (url == None):
        return None
    return lineupGenerator(url)

def lineupGenerator(url):
    time.sleep(.3)
    ref = requests.get(url)
    if ref.status_code != 200:  
        # pause for a full second before attempting again
        time.sleep(1.0)

        # attempt HTTP request (again)
        ref = requests.get(url)

    soupRef = BeautifulSoup(ref.content, features="html.parser")

    tabelle = soupRef.find_all('table', {'class': 'standard_tabelle'})
    tabelle2 = []
    players = []

    for thing in tabelle:
        temp = thing.find_all('a', href=True)
        
        for item in temp:
            tabelle2.append(item)
        
        tabelle2.append("BREAK")
        
    tem = []

    for poten in tabelle2:
        if poten == "BREAK":
            players.append(tem)
            tem = []
            continue
        
        link = poten['href']
        
        if "player_summary" in link:
            tem.append(poten)

    team1 = None
    team2 = None
    
    for i in players[::-1]:
        if (len(i) >= 11) and (team2 == None):
            team2 = i
        elif (len(i) >= 11) and (team2 != None):
            team1 = i
            break
    
    starters = []
    count = 0
    
    if (team1 == None or team2 == None):
        return starters
    
    for play in team1:
        if count < 11:
            guy = play['title']
            if guy[0] == " ":
                guy = guy[1:]
            guy = unidecode.unidecode(guy)
            starters.append(guy)
        count += 1

    count = 0
    
    for play in team2:
        if count < 11:
            guy = play['title']
            if guy[0] == " ":
                guy = guy[1:]
            guy = unidecode.unidecode(guy)
            starters.append(guy)
        count += 1
    
    return starters



def wf(teamList, date):
    # modify list to include team urls
    for i in range(len(teamList)):
        if not teamList[i] in allTeams:
            return "Fix dictionary", []
        teamList[i] = allTeams[teamList[i]]
    
    # create url for the day of the game
    urlStart = "https://www.worldfootball.net/matches_today/" + date[2] + "20" + "/" + months[date[0]] + "/" + str(int(date[1])) + "/"
    
    # soup soup soup
    time.sleep(.3)
    ref = requests.get(urlStart)
    if ref.status_code != 200:  
        # pause for a full second before attempting again
        time.sleep(1.0)

        # attempt HTTP request (again)
        ref = requests.get(urlStart)
        
    soup = BeautifulSoup(ref.content, features="html.parser")
    dat = soup.find_all('div', {'class': 'data'})[2].find_all('tr')

    newTeamList = []
    urlList = []
    
    gameFound = False
    
    # search through all tr's (basically games)
    for item in dat:
        # a's are the team links plus the game report (if exists)
        info = item.find_all('a')
        # thing's are the links
        for thing in info:
            url = "https://www.worldfootball.net"
            # information of the link
            thing = thing['href']
            if thing != None:
                
                listo = thing.split("/")
                #print(listo)
                # look for team name
                if listo[1] == "teams" and (listo[2] in teamList):
                    # remove from teamList
                    teamList.remove(listo[2])
                    # append to new one to keep order
                    newTeamList.append(listo[2])
                    gameFound = True
                    
                # find the team report
                if listo[1] == "report" and gameFound == True:
                    # removes liveticket if game is live
                    if listo[3] == "liveticker":
                        thing = thing[:-11]
                    # appends to url list, resets to find next game if necessary
                    url += thing
                    urlList.append(url)
                    gameFound = False
                    break
        
        # end condition
        if len(teamList) == 0:
            break
        
    # Didnt find team(s)
    if len(teamList) != 0:
        #print(teamList)
        return "bad", teamList
    
    starters = []
    # loop through urls found to find lineups
    for i in range(len(urlList)):
        temp = lineupGenerator(urlList[i])
        starters += temp

    return starters, newTeamList