from bs4 import BeautifulSoup
import requests
import csv
import unidecode
from datetime import datetime

def playerScraper(pid, day, pos):
    year = 20
        
    avg = 0
    count = 0.0
    weights = [0.5, 0.75, 1]
    
    while True:
        season = "20"+str(year)+"-"+"20"+str(year+1)
        if year == 17:
            break
        
        stats = {"goals": 10, "assists": 6, "shots_total": 1, "shots_on_target": 1, "cards_yellow": -1.5, "cards_red": -3, "interceptions": 0.5, "passes_completed": 0.02}
        
        summary = "https://fbref.com/en/players/" + pid + "/matchlogs/" + season + "/summary/"
        ref = requests.get(summary)
        soupRef = BeautifulSoup(ref.content, features="html.parser")
        
        table = soupRef.find("div", {"id": "content"}).find("table", {"id": "matchlogs_all"})
        
        if table==None:
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
            date = date[0]+" "+months[date[1]]+" "+date[2]
            date = datetime.strptime(date, "%Y %b %d")
            
            if date > day:
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
                
                                
                #print(s, datapoint)
                
                games[index] += int(datapoint.get_text()) * stats[s]
                #print("WORK")
            
            index += 1
        
        
        
        # SCAPES PASSING
        misc = "https://fbref.com/en/players/" + pid + "/matchlogs/" + season + "/passing/"
        ref = requests.get(misc)
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
            misc = "https://fbref.com/en/players/" + pid + "/matchlogs/" + season + "/keeper/"
            ref = requests.get(misc)
            soupRef = BeautifulSoup(ref.content, features="html.parser")
            
            table = soupRef.find("div", {"id": "content"}).find("table", {"id": "matchlogs_all"}).find("tbody")
            rows = table.find_all("tr")
            
            for r in rows:
                if games[index] == "N":
                    index += 1
                    continue
                
                for s in stats.keys():
                    datapoint = r.find("td", {"data-stat": s})
                    games[index] += int(datapoint.get_text()) * stats[s]
                
                games[index] += cleans[index] * 5
                
                index += 1
        elif pos == "D":
            while index < len(games):
                games[index] += cleans[index] * 3
                index += 1
        
        for g in games:
            if g.__class__.__name__ != "str":
                avg += (g * weights[year-18])
                count += (1.0 * weights[year-18])
        
        year -= 1
    
    return round(avg/count, 2)


months = {"01": "Jan", "02": "Feb", "03": "Mar", "04": "Apr", "05": "May", "06": "Jun", "07": "Jul", "08": "Aug", "09": "Sep", "10": "Oct", "11": "Nov", "12": "Dec"}

print(playerScraper("f0f7f62f", datetime.strptime("2020 Jul 28", "%Y %b %d"), "F"))