from doctest import master
import requests
from bs4 import BeautifulSoup
import sqlite3
import pathlib
from tkinter import *
import time
from main import makeWindow


### --- VARIABLES --- ###
DBNAME = "STOCKS.db" 
FIRSTRUN = True 

if (pathlib.Path.cwd() / DBNAME).exists():
    FIRSTRUN = False

### --- FUNCTIONS --- ###

## PROCESSING
# CHECKS
def checkInfo(STRING):
    if STRING.isalpha():
        return str(STRING)
    else:
        print("Please input only letters.")

def checkInt(NUM):
    """Checks if value is an integer

    Args:
        NUM (int): 

    Returns:
        int: 
    """
    if NUM.isnumeric():
        return int(NUM)
    else:
        print("Please enter a number: ")
        NEWNUM = input("> ")
        return checkInt(NEWNUM)

# Gets all the information from the website (general latest insider trades.)
def getGeneralTrade(URL):
    """Webscrapes data from latest trades

    Args:
        URL (str): 

    Returns:
        list: 
    """
    INFO = []
    ARRAYINFO = []
    SEPSIZE = 12 # Each list is separated into chunks with 12 objects each.
    R = requests.get(URL)
    SPECSOUP = BeautifulSoup(R.text, features="lxml")
    TABLE = SPECSOUP.find('table', class_='tinytable')
    CONTENT = TABLE.find_all('td')
    for i in range(len(CONTENT)):
        INFO.append(TABLE.select('td')[i].text)
    for i in range(len(INFO)-1, -1, -1):
        if INFO[i] == '' or INFO[i] == "D" or INFO[i] == "M" or INFO[i] == "DM" or INFO[i] == "AD" or INFO[i] == "A" or INFO[i] == "E" or INFO[i] == "ADM":
            INFO.pop(i)
    for i in range(0, len(INFO), SEPSIZE):
        ARRAYINFO.append(INFO[i:i+SEPSIZE])
    return ARRAYINFO

def getSpecificTrade(SPECURL):
    """Webscrapes data from a specific url, changeable through tkinter.

    Args:
        SPECURL (STR):

    Returns:
        [list]:
    """
    INFO = []
    ARRAYINFO = []
    SEPSIZE = 11 # Each list is separated into chunks with 11 objects each.
    SPECR = requests.get(SPECURL)
    SPECSOUP = BeautifulSoup(SPECR.text, features="lxml")
    TABLE = SPECSOUP.find('table', class_='tinytable')
    try:
        CONTENT = TABLE.find_all('td')
    except AttributeError:
        global ERRORVAR
        ERRORWINDOW = Toplevel(master)
        ERRORLABEL = Label(ERRORWINDOW, text='Operation failed; either there are no trades of this type or an input was wrong.').pack()
        ERRORVAR = False
        return
    for i in range(len(CONTENT)):
            INFO.append(TABLE.select('td')[i].text)

    for i in range(len(INFO)-1, -1, -1):
        if INFO[i] == '' or INFO[i] == "D" or INFO[i] == "M" or INFO[i] == "DM" or INFO[i] == "AD" or INFO[i] == "A" or INFO[i] == "E" or INFO[i] == "ADM":
            INFO.pop(i)

    for i in range(0, len(INFO), SEPSIZE):
        ARRAYINFO.append(INFO[i:i+SEPSIZE])
    return ARRAYINFO

def makeDB():
    """Creates databases.
    """
    CONNECTION = sqlite3.connect(DBNAME)
    CURSOR = CONNECTION.cursor()
    CURSOR.execute('''
    CREATE TABLE IF NOT EXISTS
        SPECDATA (
            DATESUBMIT PRIMARY KEY,
            DATETRADE,
            TICKER,
            TRADERNAME,
            TRADERTITLE,
            TRADETYPE,
            PRICE,
            QTYSOLD,
            QTYOWNED,
            OWNCHANGE,
            VALUE
        )
    ;''')

    CURSOR.execute('''
    CREATE TABLE IF NOT EXISTS
        DATA (
            DATESUBMIT PRIMARY KEY,
            DATETRADE,
            TICKER,
            COMPANYNAME,
            TRADERNAME,
            TRADERTITLE,
            TRADETYPE,
            PRICE,
            QTYSOLD,
            QTYOWNED,
            OWNCHANGE,
            VALUE
        )
    ;''')


def addToDB(ARRAYINFO, SELECT):
    """Adds arrayinfo to database. Takes the arrayinfo information to commit it to the database.
    The select value is used to select between inserting data into the general DATA vs SPECDATA.

    Args:
        ARRAYINFO (list): 
        SELECT (int):
    """
    if SELECT == 1:
        try:
            CONNECTION = sqlite3.connect(DBNAME)
            CURSOR = CONNECTION.cursor()
            for i in range(len(ARRAYINFO)):
                CURSOR.execute('''
                INSERT or REPLACE INTO
                    DATA (
                        DATESUBMIT,
                        DATETRADE,
                        TICKER,
                        COMPANYNAME,
                        TRADERNAME,
                        TRADERTITLE,
                        TRADETYPE,
                        PRICE,
                        QTYSOLD,
                        QTYOWNED,
                        OWNCHANGE,
                        VALUE
                    )
                    VALUES (
                        ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                    )
                ;''', (ARRAYINFO[i]))
            CONNECTION.commit()
        except sqlite3.ProgrammingError:
            NEWWINDOW = makeWindow()
            NEWWINDOW.geometry('200x50')
            ERROR = Label(NEWWINDOW, text='Failed to add to database. Database is locked, so exiting program').pack()
            time.sleep(3)
            exit()
            
    elif SELECT == 2:
        CONNECTION = sqlite3.connect(DBNAME)
        CURSOR = CONNECTION.cursor()
        try:
            for i in range(len(ARRAYINFO)):
                CURSOR.execute('''
                    INSERT or REPLACE INTO
                        SPECDATA (
                            DATESUBMIT,
                            DATETRADE,
                            TICKER,
                            TRADERNAME,
                            TRADERTITLE,
                            TRADETYPE,
                            PRICE,
                            QTYSOLD,
                            QTYOWNED,
                            OWNCHANGE,
                            VALUE
                        )
                    VALUES (
                        ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                    )
                ;''', (ARRAYINFO[i]))
            CONNECTION.commit()
            print("Successfully saved.")
        except TypeError:
            if ERRORVAR == False:
                pass
            else:
                ERRORWINDOW = Toplevel(master)
                ERRORLABEL = Label(ERRORWINDOW, text='Operation failed; either there are no trades of this type or an input was wrong. Database is locked, so exiting program.').pack()
                time.sleep(3)
                exit()


