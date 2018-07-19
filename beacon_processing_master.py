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
import csv
import subprocess
from textui import uielements

import min_avg_m_sumac
import stpp_correct_sumac

_my_dir = os.path.abspath(os.path.realpath(os.path.dirname(__file__)))

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
sitesdir = os.path.join(_my_dir, 'Test')
def select_site():
    files = glob.glob(os.path.join(sitesdir,'*'))
    directories = [os.path.basename(f) for f in files if os.path.isdir(f)]
    return uielements.user_input_list('What is your site/SD card name?',directories,emptycancel=False)
site = select_site() #selecting site using function above

#Functions to get time zone in order to make the correct local time correction in R
tzone=['Pacific','Mountain','Central','Eastern','Taiwan']
def time_zone_finder(tzone):
    return uielements.user_input_list('What is your time zone?',tzone,emptycancel=False)
time_zone = time_zone_finder(tzone)

#Copy only files from selected date range into temporary folder
parent = os.path.join(sitesdir, site, 'data') #Folder in parent directory with months
start_idx = start_date(os.listdir(parent)) #picking the first month in the range for which to grab data
end_idx = end_date(os.listdir(parent)) #picking the last month in the range for which to grab data
temporary_directory = os.path.join(_my_dir, 'Temporary_directory', site, 'data') #Path to temporary data directory

for i in range(start_idx,end_idx+1): #copy files
    shutil.copytree(os.path.join(parent,os.listdir(parent)[i]), os.path.join(temporary_directory,os.listdir(parent)[i]))

#Define last day of the month for min_avg_m_sumac.py script
if os.listdir(parent)[end_idx][5:7] in ("01","03","05","07","08","11","12"):
    lastdayofmonth = 31
elif os.listdir(parent)[end_idx][5:7] in ("04","06","09","10"):
    lastdayofmonth = 30
elif os.listdir(parent)[end_idx][5:7] in ("02") and os.listdir(parent)[end_idx][0:4] in ("2012","2016","2020","2024","2028","2032"):
    lastdayofmonth = 29
else:
    lastdayofmonth = 28

#Run minute-averaging script and STPP correct script
list_of_min_averages = min_avg_m_sumac.main(lastdayofmonth,temporary_directory)
list_of_min_averages_STPP_corrected = stpp_correct_sumac.main(list_of_min_averages)

#Change all None, nan, and Nan to "NA" because R doesn't understand Nan, nan, and None as NA
for row in list_of_min_averages_STPP_corrected:
    for (i, item) in enumerate(row):
        if item == 'None' or item == 'nan' or item == 'Nan':
            row[i]='NA'

#Write to csv for processing in R
with open("initial_output.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerows(list_of_min_averages_STPP_corrected)

#R processing
subprocess.check_call(['Rscript', '--vanilla', os.path.join(_my_dir, 'Processing_script_ideal2.r'),time_zone, _my_dir, site, os.listdir(parent)[start_idx], os.listdir(parent)[end_idx]])

#Rename file
#os.rename('R_processed_minute_averaged_STPP_corrected.csv',(site + '_' + os.listdir(parent)[start_idx] + '_to_' + os.listdir(parent)[end_idx-1] + '_' + 'minute_averaged_STPP_corrected.csv'))
#os.rename('R_processed_hour_averaged_STPP_corrected.csv',(site + '_' + os.listdir(parent)[start_idx] + '_to_' + os.listdir(parent)[end_idx-1] + '_' + 'hour_averaged_STPP_corrected.csv'))
#os.rename('checking_data_record.pdf',(site + '_' + os.listdir(parent)[start_idx] + '_to_' + os.listdir(parent)[end_idx-1] + '_' + 'hour_averaged_data_record_plots.pdf'))

###AT END
#Remove temporary directory and its contents
#shutil.rmtree('./Temporary_directory/')
#os.remove('./initial_output.csv')
