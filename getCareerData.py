# -*- encoding: utf-8 -*-
# @ModuleName: Get data
# @Function: 
# @Author: Liu Gengjin
# @Time: 11/18/2021 9:19 AM

import sys
import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup
from googlesearch import search
import os


# to save the console information in log.log file
class Logger(object):
    def __init__(self, filename='default.log', stream=sys.stdout):
        self.terminal = stream
        self.log = open(filename, 'a')

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)
        self.terminal.flush()
        self.log.flush()

    def flush(self):
        pass


# keep these two at the front of the whole script
sys.stdout = Logger('./log.log', sys.stdout)
sys.stderr = Logger('./log.log', sys.stderr)

# create the driverCareer folder
if not os.path.exists('driverCareer'):
    os.makedirs('driverCareer')
summary = pd.read_csv('firstSeasonSummary.csv')


# search the diver's name on Google and return the first driverDB's url
def googleSearch(name):
    query = name + " driverDB"
    for j in search(query, tld="co.in", num=1, stop=1, pause=2):
        return j


# collect the driver's career data and processing data
def careerData(name, year):
    # get the response in the form of html
    driverDB = googleSearch(name)
    response = requests.get(driverDB)
    # using BeautifulSoup library to crawl data from driverDB
    soup = BeautifulSoup(response.text, 'html.parser')
    # examine the website's HTML codes to determine the table class that we need
    table = soup.find('table', {'class': "table table-striped table-bordered table-condensed"})
    df = pd.read_html(str(table))
    df = pd.DataFrame(df[0])
    # add columns names
    df.columns = ['year', 'raceType', 'numRace', 'numWin', 'numPodium', 'numPole', 'numFastest']
    df = df.drop(df[((df.raceType == "Karting") | (df.raceType == "Esports"))].index)
    # only collect three years data before each driver entering the F1
    df = df.drop(df[((df.year < (year - 3)) | (df.year >= year))].index)
    df = df.drop('raceType', axis=1)
    df = df.reset_index(drop=True)
    # using regex to replace unnecessary data
    # there are some '?' data, I used Nan to replace those.
    df = df.replace(r'\?', 999, regex=True). \
        replace([' races', ' wins', ' podiums', ' pole positions',
                 ' fastest race laps', ' fastest race lap'], '', regex=True)
    df = df.replace([' race', ' win', ' podium', ' pole position',
                     ' fastest race lap'], '', regex=True).astype(int)
    df = df.replace(999, np.nan)
    df.to_csv('driverCareer/' + name + ".csv")
    print('Driver ' + str(i) + ' saved successfully!')


# main program
for i in range(len(summary)):
    fullName = summary.fullName[i]
    raceYear = summary.year[i]
    # to avoid some driver data table break the loop, that don't appear in driverDB
    try:
        careerData(fullName, raceYear)
    except ValueError:
        print(str(i) + ': ' + summary.fullName[i] + ' has no career data.')

# save Guanyu Zhou data
i = 'GuanYu Zhou'
careerData("Guanyu Zhou", 2022)


