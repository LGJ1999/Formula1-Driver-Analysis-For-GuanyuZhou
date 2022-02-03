# -*- encoding: utf-8 -*-
# @ModuleName: F1_first_season_analysis
# @Function: 
# @Author: Liu Gengjin
# @Time: 11/21/2021 4:29 PM

import numpy as np
import pandas as pd
from datetime import datetime

# input the necessary files and change the necessary column name
races = pd.read_csv('races.csv')
races = races.rename(columns={'name': 'competitionName',
                              'date': 'competitionDate'})

results = pd.read_csv('results.csv')
results = results.rename(columns={'points': 'driverPoints'})

drivers = pd.read_csv('drivers.csv')
drivers = drivers.rename(columns={'nationality': 'driverNationality',
                                  'url': 'driverLink'})

driver_standings = pd.read_csv('driver_standings.csv')
driver_standings = driver_standings.rename(
    columns={'points': 'driverAccumulativePoints',
             'position': 'driverAccumulativePosition'})

qualifying = pd.read_csv('qualifying.csv')
qualifying = qualifying.rename(columns={'position': 'qualifyingPosition'})

constructors = pd.read_csv('constructors.csv')
constructors = constructors.rename(columns={'name': 'constructorName',
                                            'nationality': 'constructorNationality'})

constructor_standings = pd.read_csv('constructor_standings.csv')
constructor_standings = constructor_standings.rename(
    columns={'points': 'constructorAccumulativePoints',
             'position': 'constructorAccumulativePosition'})


# left merge to join between different tables
def left_merge(df_right, Id):
    global seasonYear
    seasonYear = pd.merge(seasonYear, df_right, how='left', on=Id)
    return


seasonYear = races
left_merge(results, 'raceId')
left_merge(drivers, 'driverId')
left_merge(driver_standings, ['driverId', 'raceId'])
left_merge(qualifying, ['driverId', 'raceId'])
# be careful of the column name need to be renamed
seasonYear = seasonYear.rename(columns={'constructorId_x': 'constructorId'})
left_merge(constructors, 'constructorId')
left_merge(constructor_standings, ['constructorId', 'raceId'])
seasonYear = seasonYear.sort_values(by=['driverId', 'year'])


# determine the first season competitions for each driver, and drop other seasons competitions
def drop(df, driverID):
    for j in range(len(driverID)):
        competitionYear = df[df['driverId'] == driverID[j]]
        # find the first season of each driver
        firstYear = competitionYear['year'].min()
        df = df.drop(df[(df.year > firstYear) & (df.driverId == driverID[j])].index)
    return df


# this part is for processing the dataframe to suit the next operation
# make sure each driver appear only one time
driverId = seasonYear['driverId'].drop_duplicates()
# to list that will make the operation easier and the above function need a list type as an input
driverId = driverId.tolist()
firstSeason = drop(seasonYear, driverId)
# reset the index of dataframe to make sure next step's loop easier
firstSeason = firstSeason.reset_index(drop=True)

# create the new column to contain divers fullname
firstSeason['fullName'] = firstSeason.forename + " " + firstSeason.surname

# save some useful column
firstSeasonUseful = firstSeason[['fullName',
                                 'qualifyingPosition',
                                 'driverPoints', 'positionOrder',
                                 'driverAccumulativePoints', 'driverAccumulativePosition',
                                 'constructorAccumulativePoints', 'constructorAccumulativePosition',
                                 'raceId', 'driverId']].copy()

# create a new dataframe to contain the drivers' first season and statistical data
firstSeasonSummary = firstSeason[['driverId','fullName', 'dob', 'driverNationality',
                                  'constructorId', 'constructorName', 'constructorNationality',
                                  'year', 'competitionDate']].copy()

# data processing for getting the first season data for each driver
firstSeasonSummary = firstSeasonSummary.drop_duplicates(subset=['fullName'])
firstSeasonSummary = firstSeasonSummary[(firstSeasonSummary.year < 2022)]
firstSeasonSummary = firstSeasonSummary.reset_index(drop='true')

# create the new column and calculate the age when participating the first season and the birth year
firstSeasonSummary['ageForFirstSeason'] = ''
firstSeasonSummary['birthYear'] = ''
for i in range(len(firstSeasonSummary)):
    Birthday = datetime.strptime(firstSeasonSummary.dob[i], '%Y-%m-%d')
    date = datetime.strptime(firstSeasonSummary.competitionDate[i], '%Y-%m-%d')
    firstSeasonSummary.loc[i, 'ageForFirstSeason'] = round((date - Birthday).days / 365, 2)
    firstSeasonSummary.loc[i, 'birthYear'] = Birthday.year


# to count each drivers' first season's the num of competition
def num(name):
    global firstSeasonSummary
    nick = 'num' + name
    firstSeasonSummary[nick] = ''
    for k in range(len(firstSeasonSummary)):
        fullName = firstSeasonSummary.fullName[k]
        result = firstSeasonUseful.fullName[firstSeasonUseful['fullName'] == fullName].count()
        firstSeasonSummary.loc[k, nick] = result


# to get each driver participate in how many competitions for his first season
num('competition')


# to define a name function for the dataframe
def named(name,func):
    global firstSeasonSummary
    nick = name + func
    firstSeasonSummary[nick] = ''


# to define a saving data into dataframe function
def add(name, func, k, result):
    global firstSeasonSummary
    nick = name + func
    firstSeasonSummary.loc[k, nick] = result


# to calculate mean, sum, std, median of points and positions
def statistics(name):
    global firstSeasonSummary
    named(name, 'std')
    named(name, 'mean')
    named(name, 'median')
    named(name, 'maximum')
    named(name, 'minimum')
    for k in range(len(firstSeasonSummary)):
        fullName = firstSeasonSummary.fullName[k]
        nameDf = firstSeasonUseful[firstSeasonUseful['fullName'] == fullName]
        std = round(nameDf.std()[name], 2)
        add(name, 'std', k, std)
        mean = round(nameDf.mean()[name], 2)
        add(name, 'mean', k, mean)
        median = nameDf.median()[name]
        add(name, 'median', k, median)
        maximum = nameDf.max()[name]
        add(name, 'maximum', k, maximum)
        minimum = nameDf.min()[name]
        add(name, 'minimum', k, minimum)
    return


# get these two statistic data
statistics('positionOrder')
statistics('qualifyingPosition')


# to get the whole season data for each driver and constructor
def seasonData(name):
    global firstSeasonSummary
    firstSeasonSummary[name] = ''
    for j in range(len(firstSeasonSummary)):
        fullName = firstSeasonSummary.fullName[j]
        driver = firstSeasonUseful[(firstSeasonUseful.fullName == fullName)]
        raceId = driver.raceId.max()
        firstSeasonSummary.loc[j, name] = driver[driver.raceId == raceId][name].values[0]
    return


seasonData('driverAccumulativePoints')
seasonData('driverAccumulativePosition')
seasonData('constructorAccumulativePoints')
seasonData('constructorAccumulativePosition')


# to get the constructor's last three years' data, once the driver joined the team.
def constructorFormalResult(name):
    global firstSeasonSummary
    for k in range(1, 4):
        nick = str(k) + 'LastSeason' + name
        firstSeasonSummary[nick] = ''
        for j in range(len(firstSeasonSummary)):
            year = firstSeasonSummary.year[j]
            yearBack = year - k
            constructorId = firstSeasonSummary.constructorId[j]
            raceDf = seasonYear[(seasonYear.year == yearBack)]
            constructorDf = raceDf[(raceDf.constructorId == constructorId)]
            raceId = constructorDf.raceId.max()
            result = constructorDf[(constructorDf.raceId == raceId)][name].tolist()
            if result:
                firstSeasonSummary.loc[j, nick] = result[0]
            else:
                firstSeasonSummary.loc[j, nick] = np.nan
    return


constructorFormalResult('constructorAccumulativePoints')
constructorFormalResult('constructorAccumulativePosition')
firstSeasonSummary = firstSeasonSummary.drop(['driverId', 'dob', 'constructorId',
                                              'competitionDate'], axis=1)
firstSeasonSummary = firstSeasonSummary.sort_values(by="year")
firstSeasonSummary = firstSeasonSummary.reset_index(drop='true')
firstSeasonSummary.to_csv('firstSeasonSummary.csv')
