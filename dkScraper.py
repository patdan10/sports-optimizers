import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# loc - directory to be saved to
# contestType - classic or showdown
def dlcsv(loc, contestType):
    chrome_options = webdriver.ChromeOptions()
    prefs = {'download.default_directory' : loc + '\\'}
    chrome_options.add_experimental_option('prefs', prefs)
    driver = webdriver.Chrome(chrome_options=chrome_options)
    
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

    #URL FOR DOWNLOADS
    driver.get("https://www.draftkings.com/lineup/upload")

    #SPORT DROPDOWN
    WebDriverWait(driver, 400).until(
        EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div[2]/div[1]/div/div[1]/a"))
    )

    menu = driver.find_element_by_xpath("/html/body/div[1]/div[2]/div[1]/div/div[1]/a")
    menu.click()

    #FIND SOC
    WebDriverWait(driver, 400).until(
        EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div[2]/div[1]/div/div[1]/ul"))
    )

    spos = driver.find_element_by_xpath("/html/body/div[1]/div[2]/div[1]/div/div[1]/ul")
    sports = spos.find_elements_by_tag_name("li")
    
    for s in sports:
        anc = s.find_elements_by_tag_name("a")
        if anc[0].text == "SOC":
            anc[0].click()
            break

    #GAME TYPE DROPDOWN
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
        if anc2[0].text == contestType:
            anc2[0].click()
            break

    #CLICK GAMES
    listGames = driver.find_element_by_xpath("/html/body/div[1]/div[2]/div[1]/div/ul")
    games = listGames.find_elements_by_tag_name("li")
    dl = driver.find_element_by_xpath("/html/body/div[1]/div[2]/div[1]/div/a")

    allTeams = []
    
    for g in games:
        teams = g.find_elements_by_tag_name("em")[0].text.split(" ")
        date = g.text.split(" ")
        game = []
        game.append(teams[0])
        game.append(teams[2])
        date[0] = date[0].split("/")
        date[0] = date[0][0]+date[0][1]
        game.append(date[0:3])
        allTeams.append(game)
        
        g.click()
        time.sleep(0.2)
        dl.click()
    
    return allTeams


def csvSubmit(loc, optims, driver):
    subLoc = "/Users/patrick/Desktop/code"
    headings = ['CPT', 'FLEX', 'FLEX', 'FLEX', 'FLEX', 'FLEX']
    
    for lineup in optims:
        ids = []
        for i in lineup:
            if i[1] == 1:
                ids.append(i[0])
        for i in lineup:
            if i[1] == 0:
                ids.append(i[0])
                
        # CREATE SUBMISSION FILE
        with open('submission.csv', 'w') as csvfile:
            filewriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            filewriter.writerow(headings)
            filewriter.writerow(ids)
            
        
        # upload page
        driver.get("https://www.draftkings.com/lineup/upload")
            
        WebDriverWait(driver, 400).until(
            EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div[2]/div[2]/form/input[1]"))
        )
        
        
        upload = driver.find_element_by_xpath("/html/body/div[1]/div[2]/div[2]/form/input[1]")
        upload.send_keys(subLoc + "/submission.csv")
        upload.submit()
        
        os.remove(subLoc + "/submission.csv")