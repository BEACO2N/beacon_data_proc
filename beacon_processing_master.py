#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 12 09:55:23 2018

@author: stephendecina
"""

#Necessary modules
import os
import shutil
import sys
import glob
from textui import uielements

import min_avg_m_sumac

#Dealing with compatability issue
if sys.version_info.major == 3:
    get_input = input
elif sys.version_info.major == 2:
    get_input = raw_input
else:
    raise NotImplementedError('No input method defined for Python version {}'.format(sys.version_info.major))

#Functions to get date range in order to copy only files of interest to temporary directory
def start_date(dates):
    return uielements.user_input_list('What is your start date?',dates,emptycancel=False, returntype='index')

def end_date(dates):
    return uielements.user_input_list('What is your end date?',dates,emptycancel=False, returntype='index')

#Asking for user input: which site should we process?
sitesdir = os.path.join('.', 'Test')
def select_site():
    files = glob.glob(os.path.join(sitesdir,'*'))
    directories = [os.path.basename(f) for f in files if os.path.isdir(f)]
    return uielements.user_input_list('What is your site/SD card name?',directories,emptycancel=False)
site = select_site() #selecting site using function above

#Copy only files from selected date range into temporary folder
parent = os.path.join('.', 'Test', site, 'data') #Folder in parent directory with months
start_idx = start_date(os.listdir(parent)) #picking the first month in the range for which to grab data
end_idx = end_date(os.listdir(parent)) #picking the last month in the range for which to grab data

tempdir = os.path.join('.', 'Temporary_directory', site, 'data') #Path to temporary data directory
for i in range(start_idx,end_idx+1): #copy files
    shutil.copytree(os.path.join(parent,os.listdir(parent)[i]), os.path.join(tempdir,os.listdir(parent)[i]))

#Define last day of the month for min_avg_m_sumac.py script
#Give example of what "monthfolders" is - explanation
if os.listdir(parent)[end_idx][5:7] in ("01","03","05","07","08","11","12"):
    lastdayofmonth = 31
elif os.listdir(parent)[end_idx][5:7] in ("04","06","09","10"):
    lastdayofmonth = 30
elif os.listdir(parent)[end_idx][5:7] in ("02") and os.listdir(parent)[end_idx][0:4] in ("2012","2016","2020","2024","2028","2032"):
    lastdayofmonth = 29
else:
    lastdayofmonth = 28

#Run minute-averaging script
min_avg_m_sumac.main(lastdayofmonth,tempdir)

import stpp.correct.py

#Run python scripts to get minute-averaged file
#python2.7 min_avg_M.py ../A5 | python2.7 stpp_correct.py >../A5/HA5_2018_Dec_Mar.csv

#Change all NA's to "NA"
#sed -i '' -e ’s/None/NA/g' ../B4/HB4_2018_Dec_Jan.csv
#sed -i '' -e ’s/NaN/NA/g' ../B4/HB4_2018_Dec_Jan.csv
#sed -i '' -e ’s/nan/NA/g' ../B4/HB4_2018_Dec_Jan.csv

#R processing


###AT END
#Remove temporary directory and its contents
shutil.rmtree('./Temporary_directory/')


















#make Temporary Directory - likely unnecessary
def createFolder(directory):
    if not os.path.isdir(directory):
        os.makedirs(directory)
    elif os.path.isfile(directory):
        raise OSError ('"{}" is a file, cannot create a directory with that name'.format(directory))
        
site = input('What is your site/SD card name as written in Sumac?')
startdate = input('What is your start date in yyyy_mm?')
shellcmd = os.path.join('.', 'Temporary_directory', site, 'data',startdate)
createFolder(shellcmd)



def start_date(dates):
    print("What is your start date?")
    for idx, element in enumerate(dates):
        print("{}) {}".format(idx+1,element))
    i = get_input("Enter number: ")
    try:
        if 0 < int(i) <= len(dates):
            return int(i)
    except:
        pass
    return None

def end_date(dates):
    print("What is your end date?")
    for idx, element in enumerate(dates):
        print("{}) {}".format(idx+1,element))
    i = get_input("Enter number: ")
    try:
        if 0 < int(i) <= len(dates):
            return int(i)
    except:
        pass
    return None