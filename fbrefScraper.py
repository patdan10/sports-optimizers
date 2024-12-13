from bs4 import BeautifulSoup
import requests
import csv
import unidecode
from datetime import datetime
import time

import teamDictionary
months = teamDictionary.months

def playerScraper(pid, pos, retroDate):
    year = 20
        
    avg = 0
    count = 0.0
    while True:
        season = "20"+str(year)+"-20"+str(year+1)
        if year == 17:
            break
        year -= 1
        
        stats = {"goals": 10, "assists": 6, "shots_total": 1, "shots_on_target": 1, "cards_yellow": -1.5, "cards_red": -3, "interceptions": 0.5, "passes_completed": 0.02}
        
        summary = "https://fbref.com/en/players/" + pid + "/matchlogs/" + season + "/summary/"
        
        time.sleep(.3)
        ref = requests.get(summary)
        if ref.status_code != 200:  
            # pause for a full second before attempting again
            time.sleep(1.0)

            # attempt HTTP request (again)
            ref = requests.get(summary)
        
        soupRef = BeautifulSoup(ref.content, features="html.parser")
        
        table = soupRef.find("div", {"id": "content"}).find("table", {"id": "matchlogs_all"})
        
        
        if table == None:
            break
        
        table = table.find("tbody")
        
        rows = table.find_all("tr")
        
        index = 0
        games = [0]*len(rows)
        cleans = [0]*len(rows)
        
        
        # SCRAPE SUMMARY
        for r in rows:
            
            cleans[index] = r.find("td", {"data-stat": "opponent"}).get_text()
            #print(cleans[index])
            if ("N" in r.find("td", {"data-stat": "game_started"}).get_text()) or (r.has_attr('class')):
                games[index] = "N"
                index += 1
                continue
            
            date = r.find("th", {"data-stat": "date"}).get_text().split("-")
            #print(date)
            date = date[0]+" "+months[date[1]]+" "+date[2]
            date = datetime.strptime(date, "%Y %b %d")
            
            if date > retroDate:
                games[index] = "N"
                index += 1
                continue
            
            for s in stats.keys():
                datapoint = r.find("td", {"data-stat": s})
                if datapoint is None or len(datapoint.get_text()) == 0:
                    games[index] = "N"
                    break
                
                games[index] += int(datapoint.get_text()) * stats[s]
            
            index += 1
        
        # SCRAPE MISC
        stats = {"fouls": 1, "fouled": -0.5, "crosses": 0.7, "tackles_won": 1}
        misc = "https://fbref.com/en/players/" + pid + "/matchlogs/" + season + "/misc/"
        time.sleep(.3)
        ref = requests.get(misc)
        if ref.status_code != 200:  
            # pause for a full second before attempting again
            time.sleep(1.0)

            # attempt HTTP request (again)
            ref = requests.get(misc)
        soupRef = BeautifulSoup(ref.content, features="html.parser")
        
        table = soupRef.find("div", {"id": "content"}).find("table", {"id": "matchlogs_all"}).find("tbody")
        rows = table.find_all("tr")
        index = 0
        
        for r in rows:
            if games[index] == "N":
                index += 1
                continue
            
            for s in stats.keys():
                datapoint = r.find("td", {"data-stat": s})
                
                if datapoint is None or len(datapoint.get_text()) == 0:
                    games[index] = "N"
                    break
                
                games[index] += int(datapoint.get_text()) * stats[s]
            
            index += 1
        
        #print(games)
        
        # SCAPES PASSING
        passing = "https://fbref.com/en/players/" + pid + "/matchlogs/" + season + "/passing/"
        time.sleep(.3)
        ref = requests.get(passing)
        if ref.status_code != 200:  
            # pause for a full second before attempting again
            time.sleep(1.0)

            # attempt HTTP request (again)
            ref = requests.get(passing)
        soupRef = BeautifulSoup(ref.content, features="html.parser")
        
        table = soupRef.find("div", {"id": "content"}).find("table", {"id": "matchlogs_all"}).find("tbody")
        rows = table.find_all("tr")
        index = 0
        
        for r in rows:
            if games[index] == "N":
                cleans[index] = "N"
                index += 1
                continue
            
            
            datapoint = r.find("td", {"data-stat": "assisted_shots"})
            
            if datapoint is None or len(datapoint.get_text()) == 0:
                    games[index] = "N"
                    break
            
            games[index] += int(datapoint.get_text()) * 1
            
            
            datapoint = r.find("td", {"data-stat": "result"}).get_text().split("–")
            ga = datapoint[1]
            win = datapoint[0].split(" ")[0]
            
            if ga == "0":
                cleans[index] = 1
            else:
                cleans[index] = 0
            
            if pos == "GK":
                if win == "W":
                    games[index] += 5
            
            
            index += 1
        
        # SCRAPES ONLY KEEPERS
        index = 0
        
        if pos == "GK":
            stats = {"saves": 2, "goals_against_gk": -2}
            keeper = "https://fbref.com/en/players/" + pid + "/matchlogs/" + season + "/keeper/"
            time.sleep(.3)
            ref = requests.get(keeper)
            if ref.status_code != 200:  
                # pause for a full second before attempting again
                time.sleep(1.0)

                # attempt HTTP request (again)
                ref = requests.get(keeper)
                
            soupRef = BeautifulSoup(ref.content, features="html.parser")
            
            table = soupRef.find("div", {"id": "content"}).find("table", {"id": "matchlogs_all"}).find("tbody")
            rows = table.find_all("tr")
            
            for r in rows:
                if games[index] == "N":
                    index += 1
                    continue
                
                for s in stats.keys():
                    datapoint = r.find("td", {"data-stat": s})
                    
                    if datapoint is None or len(datapoint.get_text()) == 0:
                        games[index] = "N"
                        break
                    
                    games[index] += int(datapoint.get_text()) * stats[s]
                
                games[index] += cleans[index] * 5
                
                index += 1
        elif pos == "D":
            while index < len(games):
                games[index] += cleans[index] * 3
                index += 1
        
        for g in games:
            if g.__class__.__name__ != "str":
                avg += g
                count += 1.0
    if count == 0:
        return 0
    return round(avg/count, 2)
