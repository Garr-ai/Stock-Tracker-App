from cProfile import label
from doctest import master
import sqlite3
from textwrap import fill
from turtle import bgcolor, width
from WebscrapeandDB import *
from tkinter import *
from tkinter import ttk
import tkinter as tk
import pandas as pd
import time
import os
import pathlib


### --- VARIABLES --- ###
DBNAME = 'STOCKS.db'
FIRSTRUN = True

if (pathlib.Path.cwd() / DBNAME).exists():
    FIRSTRUN = False

### --- FUNCTIONS --- ###

### Input
def inputWindow():
    """Window to input wanted info into entry.
    """
    global TICKER, DAYS, RESULTS
    TICKERLABEL = Label(NEWWINDOW, text='Ticker:').pack()
    TICKER = Entry(NEWWINDOW)
    TICKER.pack()
    DAYLABEL = Label(NEWWINDOW, text='Days Ago:').pack()
    DAYS = Entry(NEWWINDOW)
    DAYS.pack()
    RESULTS = Label(NEWWINDOW, text='# of Results:').pack()
    RESULTS = Entry(NEWWINDOW)
    RESULTS.pack()
    # Empty space as a separator.
    SPACE = Label(NEWWINDOW, text=' ').pack()
    
    # Button to get values from the entry widget.
    INPUTBUTTON = Button(NEWWINDOW, text='Enter Information', command=getInputs)
    INPUTBUTTON.pack()


def selectInput():
    """Buttons to select what operation to undergo.
    """
    BT1 = Button(text='Refresh latest trades', command=lambda: btSelect(1)).grid(row=1, column=0, padx=5, pady=15)
    BT2 = Button(text='Add specified ticker', command=lambda: btSelect(2)).grid(row=1, column=1, padx=5, pady=15)
    BT3 = Button(text='Export general data as CSV', command=lambda: btSelect(3)).grid(row=1, column=2, padx=5, pady=15)
    BT4 = Button(text='Export specific data as CSV', command=lambda: btSelect(4)).grid(row=1, column=3, padx=5, pady=15)
    BT5 = Button(text='Show recent trades', command=lambda: btSelect(5)).grid(row=1, column=4, padx=5, pady=15)
    BT6 = Button(text='Show specific trades', command=lambda: btSelect(6)).grid(row=1, column=5, padx=5, pady=15)


def getSearchNum():
    """Used for the refreshing button; gets number of results.
    """
    global ENTERNUM
    TEXT = Label(NEWWINDOW, text='Number of Results:').pack()
    ENTERNUM = Entry(NEWWINDOW)
    NEWWINDOW.geometry('250x100')
    ENTERNUM.pack()
    NUMWARNING = Label(NEWWINDOW, text='Entering a number above 100 may cause lag.').pack(pady=5)
    NUMBUTTON = Button(NEWWINDOW, text='Enter', command=getNumEntry).pack(pady=5)
     
### Processing
def menuVisuals():
    """Creates the main menu
    """
    ROOT.title('Insider Stocks Viewer')
    ROOT.geometry('825x50')
    ROOT.config(bg='#1277FC')
    ROOT.resizable(False,False)

def btSelect(NUM):
    """Based on button clicked, undergoes operation.

    Args:
        NUM (INT): 
    """
    if NUM == 1:
        URL = f"http://openinsider.com/screener?s=&o=&pl=&ph=&ll=&lh=&fd=730&fdr=&td=0&tdr=&fdlyl=&fdlyh=&daysago=&xp=1&xs=1&vl=&vh=&ocl=&och=&sic1=-1&sicl=100&sich=9999&grp=0&nfl=&nfh=&nil=&nih=&nol=&noh=&v2l=&v2h=&oc2l=&oc2h=&sortcol=0&cnt={NUM}&page=1"
        NEWWINDOW = makeWindow()
        RESULTS = getSearchNum()

    elif NUM == 2:
        NEWWINDOW = makeWindow()
        NEWWINDOW.geometry('250x200')
        inputWindow()

    elif NUM == 3:
        FILENAME = 'Data.csv'
        if (pathlib.Path.cwd() / FILENAME).exists():
            os.remove(FILENAME)
        else:
            pass
        CONNECTION = connectDB()
        makeGeneralCSV(CONNECTION)
        NEWWINDOW = makeWindow()
        NEWWINDOW.geometry('150x75')
        SUCCESS = Label(NEWWINDOW, text='SUCCESS').pack()
    
    elif NUM == 4:
        FILENAME = 'Specdata.csv'
        if (pathlib.Path.cwd() / FILENAME).exists():
            os.remove(FILENAME)
        else:
            pass
        CONNECTION = connectDB()
        makeSpecCSV(CONNECTION)
        NEWWINDOW = makeWindow()
        NEWWINDOW.geometry('150x75')
        SUCCESS = Label(NEWWINDOW, text='SUCCESS').pack()

    elif NUM == 5:
        NEWWINDOW = makeWindow()
        viewGeneral()
    
    elif NUM == 6:
        NEWWINDOW = makeWindow()
        viewSpecific()

def connectDB():
    """Connects to the db

    Returns:
        db: 
    """
    CONNECTION = sqlite3.connect(DBNAME)
    return CONNECTION

def makeGeneralCSV(CONNECTION):
    """Creates csv

    Args:
        CONNECTION (db): 
    """
    CURSOR = CONNECTION.cursor()
    DATA=pd.read_sql('SELECT * from DATA', CONNECTION)
    DATA.to_csv('Data.csv')

def makeSpecCSV(CONNECTION):
    """Creates spec csv

    Args:
        CONNECTION (db): 
    """
    CURSOR = CONNECTION.cursor()
    SPECDATA=pd.read_sql('SELECT * from SPECDATA', CONNECTION)
    SPECDATA.to_csv('Specdata.csv')
# ---------------------------------------------------------------------------- #

def getNumEntry():
    """Get the entered value and continues operation.
    """
    RESULTS=ENTERNUM.get()
    URL = f"http://openinsider.com/screener?s=&o=&pl=&ph=&ll=&lh=&fd=730&fdr=&td=0&tdr=&fdlyl=&fdlyh=&daysago=&xp=1&xs=1&vl=&vh=&ocl=&och=&sic1=-1&sicl=100&sich=9999&grp=0&nfl=&nfh=&nil=&nih=&nol=&noh=&v2l=&v2h=&oc2l=&oc2h=&sortcol=0&cnt={RESULTS}&page=1"
    ARRAYINFO = getGeneralTrade(URL)
    NUM = 1
    addToDB(ARRAYINFO, NUM)
    NEWWINDOW.destroy()


def getInputs():
    """Gets all entered values and continues operation.
    """
    TICKTEXT=TICKER.get()
    DAYVAL=DAYS.get()
    RESULTVAL=RESULTS.get()
    confWindow(TICKTEXT, DAYVAL, RESULTVAL)

def makeWindow():
    """Makes a new window
    """
    global NEWWINDOW
    NEWWINDOW = Toplevel(master)
    NEWWINDOW.title('New')
    NEWWINDOW.geometry('600x600')
    return NEWWINDOW


                        
# --------------------------------------------------------------- #

# Confirmation window
def confWindow(TICKER, DAYVAL, RESULTS):
    """Displays entered values and asks for confirmation of correctly entered values.

    Args:
        TICKER (STR): 
        DAYVAL (INT): 
        RESULTS (ITN): 
    """
    global CONF
    CONF = Toplevel(master)
    CONF.title("Confirmation")
    CONF.geometry('300x200')
    CONF.resizable('False', 'False')
    CONFLABEL = Label(CONF, text='Is this correct?').pack()
    TICKERLAB = Label(CONF, text=f'Ticker: {TICKER}').pack()    
    DAYLAB = Label(CONF, text=f'Days Ago: {DAYVAL}').pack()
    RESULTNUM = Label(CONF, text=f'Result #: {RESULTS}').pack()
    try:
        if int(RESULTS) > 25:
            WARNING = Label(CONF, text='''Warning! Choosing a result higher than 25 
            may cause 
            a significant delay in getting results.''').pack()
        else:
            pass
    except ValueError:
        pass
    YESBUTTON = Button(CONF, text='Yes', command=lambda: yesClicked(TICKER, DAYVAL, RESULTS)).pack()
    NOBUTTON = Button(CONF, text='No', command=CONF.destroy).pack()
    
def yesClicked(TICKER, DAYVAL, RESULTS):
    """Destroys old windows after yes is clicked, and finishes operations.

    Args:
        TICKER (STR):
        DAYVAL (int): 
        RESULTS (int):
    """
    URL = f"http://openinsider.com/screener?s={TICKER}&o=&pl=&ph=&ll=&lh=&fd=730&fdr=&td=0&tdr=&fdlyl=&fdlyh=&daysago={DAYVAL}&xp=1&xs=1&vl=&vh=&ocl=&och=&sic1=-1&sicl=100&sich=9999&grp=0&nfl=&nfh=&nil=&nih=&nol=&noh=&v2l=&v2h=&oc2l=&oc2h=&sortcol=0&cnt={RESULTS}&page=1"
    ARRAYINFO = getSpecificTrade(URL)
    NUM = 2
    addToDB(ARRAYINFO, NUM)
    CONF.destroy()
    NEWWINDOW.destroy()

# -------------------------------------------------------------- #

### OUTPUTS
def viewGeneral():
    """Displays table of whole database.
    """
    CONNECTION = sqlite3.connect(DBNAME)
    CURSOR = CONNECTION.cursor()
    DATA = CURSOR.execute('''
        SELECT
            *,
            oid
        FROM
            DATA
    ;''').fetchall()

    # Main table
    TABLE = ttk.Treeview(NEWWINDOW)
    VSCROLL = ttk.Scrollbar(NEWWINDOW, orient='vertical', command=TABLE.yview)
    VSCROLL.pack(side='right', fill='y')
    XSCROLL = ttk.Scrollbar(NEWWINDOW, orient='horizontal', command=TABLE.xview)
    XSCROLL.pack(side='bottom', fill='x')
    TABLE.configure(yscrollcommand=VSCROLL.set, xscrollcommand=XSCROLL.set)
    TABLE['columns'] = ("Date Submitted", "Date of Trade", "Ticker", "Company Name", "Trader Name", "Trader Title", "Trade Type", "Price", "Qty Sold", "Qty Owned", "Own Change", "Value +-")
    TABLE.column("#0", width=0, stretch=NO)
    TABLE.column("Date Submitted", width=90)
    TABLE.column("Date of Trade", width=80)
    TABLE.column("Ticker", width=50)
    TABLE.column("Company Name", width=80)
    TABLE.column("Trader Name", width=80)
    TABLE.column("Trader Title",width=80)
    TABLE.column("Trade Type", width=80)
    TABLE.column("Price", width=50)
    TABLE.column("Qty Sold", width=80)
    TABLE.column("Qty Owned", width=80)
    TABLE.column("Own Change", width=80)
    TABLE.column("Value +-", width=80)
    TABLE.heading("#0", text='')
    TABLE.heading("Date Submitted", text="Date Submitted")
    TABLE.heading("Date of Trade", text="Date of Trade")
    TABLE.heading("Ticker", text="Ticker")
    TABLE.heading("Company Name", text="Company Name")
    TABLE.heading("Trader Name", text="Trader Name")
    TABLE.heading("Trader Title", text="Trader Title")
    TABLE.heading("Trade Type", text="Trade Type")
    TABLE.heading("Price", text="Price")
    TABLE.heading("Qty Sold", text="Qty Sold")
    TABLE.heading("Qty Owned", text="Qty Owned")
    TABLE.heading("Own Change", text="Own Change")
    TABLE.heading("Value +-", text="Value +-")
    TABLE.pack(fill='both', expand=True)

    COUNT = 1
    TABLE.tag_configure('odd', background='white')
    TABLE.tag_configure('even', background='#DCE0DD')
    for info in DATA:
        if COUNT % 2 == 0:
            TABLE.insert("", tk.END, values=info, tags=('even',))
        else:
            TABLE.insert("", tk.END, values=info, tags=('odd',))

        COUNT+=1

def viewSpecific():
    """Displays table of whole specific database.
    """
    global TABLE
    CONNECTION = sqlite3.connect(DBNAME)
    CURSOR = CONNECTION.cursor()
    SPECDATA = CURSOR.execute('''
        SELECT
            *,
            oid
        FROM
            SPECDATA
    ;''').fetchall()
    CONNECTION.close()
    TABLE = ttk.Treeview(NEWWINDOW)
    VSCROLL = ttk.Scrollbar(NEWWINDOW, orient='vertical', command=TABLE.yview)
    VSCROLL.pack(side='right', fill='y')
    XSCROLL = ttk.Scrollbar(NEWWINDOW, orient='horizontal', command=TABLE.xview)
    XSCROLL.pack(side='bottom', fill='x')
    TABLE.configure(yscrollcommand=VSCROLL.set, xscrollcommand=XSCROLL.set)
    TABLE['columns'] = ("Date Submitted", "Date of Trade", "Ticker", "Trader Name", "Trader Title", "Trade Type", "Price", "Qty Sold", "Qty Owned", "Own Change", "Value +-")
    TABLE.column("#0", width=0, stretch=NO)
    TABLE.column("Date Submitted", width=90)
    TABLE.column("Date of Trade", width=80)
    TABLE.column("Ticker", width=50)
    TABLE.column("Trader Name", width=80)
    TABLE.column("Trader Title",width=80)
    TABLE.column("Trade Type", width=80)
    TABLE.column("Price", width=50)
    TABLE.column("Qty Sold", width=80)
    TABLE.column("Qty Owned", width=80)
    TABLE.column("Own Change", width=80)
    TABLE.column("Value +-", width=80)
    TABLE.heading("#0", text='')
    TABLE.heading("Date Submitted", text="Date Submitted")
    TABLE.heading("Date of Trade", text="Date of Trade")
    TABLE.heading("Ticker", text="Ticker")
    TABLE.heading("Trader Name", text="Trader Name")
    TABLE.heading("Trader Title", text="Trader Title")
    TABLE.heading("Trade Type", text="Trade Type")
    TABLE.heading("Price", text="Price")
    TABLE.heading("Qty Sold", text="Qty Sold")
    TABLE.heading("Qty Owned", text="Qty Owned")
    TABLE.heading("Own Change", text="Own Change")
    TABLE.heading("Value +-", text="Value +-")
    TABLE.pack(fill='both', expand=True)

    # Create striped row tags
    COUNT = 0
    TABLE.tag_configure('odd', background='white')
    TABLE.tag_configure('even', background='#DCE0DD')
    for info in SPECDATA:
        if COUNT % 2 == 0:
            TABLE.insert("", tk.END, values=info, tags=('even',))
        else:
            TABLE.insert("", tk.END, values=info, tags=('odd',))

        COUNT+=1

        
if __name__ == "__main__":
    ROOT = Tk()
    if FIRSTRUN == True:
        URL = 'http://openinsider.com/screener?s=&o=&pl=&ph=&ll=&lh=&fd=730&fdr=&td=0&tdr=&fdlyl=&fdlyh=&daysago=&xp=1&xs=1&vl=&vh=&ocl=&och=&sic1=-1&sicl=100&sich=9999&grp=0&nfl=&nfh=&nil=&nih=&nol=&noh=&v2l=&v2h=&oc2l=&oc2h=&sortcol=0&cnt=50&page=1'
        STOCKARRAY = getGeneralTrade(URL)
        NUM = 1
        makeDB()
        addToDB(STOCKARRAY, NUM)
    else:
        pass
    ### Program runs as normal
    menuVisuals()
    selectInput()
    ROOT.mainloop()

    
