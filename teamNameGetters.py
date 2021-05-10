import csv

'''
scrapes the showdown csv to find team names
returns list of all team names in the csv
'''
def showdownTeamNameGetter(loc):
    # scrape the csv
    with open(loc, encoding='mac_roman') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        counter = 0
        # instantiate teams list
        teams = []
        for row in reader:
            # ignore beginning of csv file
            if counter < 8:
                counter += 1
                continue
            # find new teams
            if row[14] not in teams:
                teams.append(row[14])
                continue
    
    return teams

'''
scrapes the classic csv to find team names
returns list of all team names in the csv
'''
def classicTeamNameGetter(loc):
    # scrape the csv
    with open(loc, encoding='mac_roman') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        counter = 0
        # instantiate teams list
        teams = []
        for row in reader:
            # ignore beginning of csv file
            if counter < 8:
                counter += 1
                continue
            # find new teams
            if row[16] not in teams:
                teams.append(row[16])
                continue
    
    return teams