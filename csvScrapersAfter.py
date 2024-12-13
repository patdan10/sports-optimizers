import csv
import math
import unidecode

'''
Scrapes the showdown after file to find the true FPTS
Returns points scored by the lineup
'''
def showdownCsvAfterScrape(loc, lineup):

    # total points
    points = 0.0
    
    with open(loc, encoding='utf8') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        # used to skip the unneeded lines
        counter = 0
        
        for row in reader:
            #ignore top rows
            if counter == 0:
                counter += 1
                continue
            
            # rewrite without accents
            row[7] = unidecode.unidecode(row[7])
            
            # go through the lineup
            for i in lineup:
                # skip if not player (7 is player name)
                if not i[0] in row[7]:
                    if not row[7][1:] == i[0]:
                        continue
                # if marked as captain in csv (8 is CPT/FLEX, 10 is FPTS)
                if row[8] == "CPT":
                    row[10] = round(float(row[10])*(2.0/3.0),2)
                # if captain in lineup
                if i[1] == 1:
                    row[10] = round(float(row[10])*(1.5),2)
                # sum to total points
                points += float(row[10])
                
    return points

'''
Scrapes the classic after file to find the true FPTS
Returns points scored by the lineup
'''
def classicCsvAfterScrape(loc, lineup):

    # total points
    points = 0.0
    
    with open(loc, encoding='utf8') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        # used to skip the unneeded lines
        counter = 0
        
        for row in reader:
            #ignore top rows
            if counter == 0:
                counter += 1
                continue
            
            # rewrite without accents
            row[7] = unidecode.unidecode(row[7])
            
            # go through the lineup
            for i in lineup:
                # skip if not player (7 is player name)
                if not row[7] == i[0]:
                    if not row[7][1:] == i[0]:
                        continue
                # sum to total points
                print(row[7])
                points += float(row[10])
                
    return points
            
'''
Scrapes the after csv file to find how well the optimal lineup would have performed
Returns percentile
'''
def findPercentile(loc, points):
    
    with open(loc, encoding='utf8') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        # counts all entries
        counter = -1
        # tracks rank
        rank = 0.0
        
        for row in reader:
            #skip first line
            if counter == -1:
                counter += 1
                continue
            
            # increment the counter to track # of entries
            counter += 1
            
            # find rank where our entry was/would have been
            if round(float(row[4]),2) <= points and rank == 0:
                rank = float(row[0])

    # return the average percentile
    return round(1.0 - (rank/counter),6)