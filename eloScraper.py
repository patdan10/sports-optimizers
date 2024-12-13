from bs4 import BeautifulSoup
import requests
import csv
import unidecode
from datetime import datetime
import time

def eloScraper(tid, day):
    
    seasonSwitch = datetime.strptime("2020 Aug 25", "%Y %b %d")
    
    if day > seasonSwitch:
        season = "2020-2021"
    else:
        season = "2019-2020"
    
    #print(season)
    
    url = "http://elofootball.com/club.php?clubid="+str(tid)+"&season="+season
    #print(url)
    time.sleep(.3)
    
    ref = requests.get(url)
    # loop until sucess or die after 4 attempts
    #   (if initial request was sucessful, then does nothing.)

    #attempt = 0 # - counts the number of attempts made

    if ref.status_code != 200:  
        # pause for a full second before attempting again
        time.sleep(1.0)

        # attempt HTTP request (again)
        ref = requests.get(url)
    
    soupRef = BeautifulSoup(ref.content, features="html.parser")
    dates = soupRef.find_all("table", {"class": "sortable fixed primary"})[-1]
    dates = dates.find_all("tr")[1:]
    for game in dates:
        rows = game.find_all("td")
        gdate = rows[1].get_text().split("/")
        gdate = gdate[0]+" "+months[gdate[1]]+" "+gdate[2]
        gdate = datetime.strptime(gdate, "%Y %b %d")
        #print(gdate)
        if gdate <= day:
            elo = rows[-3].get_text()
            return elo



months = {"01": "Jan", "02": "Feb", "03": "Mar", "04": "Apr", "05": "May", "06": "Jun", "07": "Jul", "08": "Aug", "09": "Sep", "10": "Oct", "11": "Nov", "12": "Dec"}

#print(eloScraper("225", datetime.strptime("2020 Nov 8", "%Y %b %d")))