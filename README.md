# Readme for the repository beacon_data_proc
The program in this repository retrieves selected data for selected site and processes to minute- and hour-averaged .csv files
using the program beacon_processing_master.py

## Overview
This program was written to simplify the following steps:
1. Grabbing Beacon data from Sumac
2. Making minute-averaged and hour-averaged files from raw Beacon data with STPP-corrected CO2
3. Making plots over the selected time period to take a quick look for equipment health and/or wifi connectivity

The program requires the following scripts to work:
1. min_avg_m_sumac.py (makes the minute-averaged file)
2. stpp_correct_sumac.py (corrects CO2 for STPP - see Shusterman et al., 2016)
3. Beacon_minute_and_hour_average_processing.R (makes the hour-averaged file and cleans up the data - see R script for more details)

## Getting started and user inputs
In order to run this program, follow these steps:
1. Pull this repository from Git to your Sumac home directory using the command: git clone https://github.com/BEACO2N/beacon_data_proc.git
2. In the directory beacon_data_proc in your home directory, run: ./beacon_processing_master.py
3. Select the number of the site/SD card name for which you would like data
4. Select the time zone where your site is located. Note that for time zones in the United States, adjustments for daylight savings time (DST)
   will be automatically made. Take caution if your site is in a place that doesn't observe DST (e.g. non-Navajo Arizona)
5. Select the date range for which you would like data
6. Let 'er rip. Upon completion you will have a minute-averaged csv, and hour-averaged csv, and a pdf with a data table of maximum and minimum
   hour-averaged values over the time period and plots of the hour-averaged values over the time period.
7. Paste the command given in another terminal window in your selected local directory to copy these files from Sumac to local.

## Heading explanations in csv files
Column | Explanation
------------ | -------------
Index | Row number
Date_time_UTC | Date and time in UTC, taken directly from Beacon data
Date_time_local | Date and time in local time, calculated in R program
Date_only_local | Date without time in local time, calculated in R program
Weekday_local | Weekday in local time, calculated in R program
Julian_local | Ordinal day in local time, calculated in R program 
Julian_decimal_local | Ordinal day and time in local time, calculated in R program
Pressure | Atmospheric pressure in mbar
BME_temp | Temperature in degrees Celsius from the BME at the site
Vaisala_temp | Temperature in degrees Celsius from the Vaisala at the site
Rh | Relative humidity from the BME at the site
Dew_pt | Dew point temperature in degrees Celsius from the BME at the site
O3_wrk | Voltage at the ozone working electrode in millivolts
O3_aux | Voltage at the ozone auxiliary electrode in millivolts
CO_wrk | Voltage at the carbon monoxide working electrode in millivolts
CO_aux | Voltage at the carbon monoxide auxiliary electrode in millivolts
NO_wrk | Voltage at the nitric oxide working electrode in millivolts
NO_aux | Voltage at the nitric oxide auxiliary electrode in millivolts
NO2_wrk | Voltage at the ozone working electrode in millivolts
NO2_aux | Voltage at the nitrogen dioxide auxiliary electrode in millivolts
PM_hi | The "high" PM reading
PM_lo | The "low" PM reading
PM_pct_fs | PM percent full scale
CO2_raw | Raw CO2 value reported by the Vaisala
CO2_STPP | CO2 value corrected for STPP

Note that "Julian" designation reflects the common misuse of the term "Julian" to mean the term "ordinal"

## Wish List
This version of the program is in its first stage of development. Some items that would be great for future iterations:
1. Write files to .mat format for further processing in Matlab
2. Caculate ordinal day from year zero rather than the beginning of the year
3. Automate the running of this code to produce plots or tables every Monday which will flag malfunctioning equipment at sites
4. Add CO2 corrections for atemporal and temporal bias (see Shusterman et al., 2016)
5. Add trace gas processing to convert voltage to concentration (see Kim et al., 2018)
6. Add PM processing to convert percent full scale to concentration
7. When BME at a site is broken, use Vaisala temperature at that site and BME data from the closest site to calculate STPP-corrected CO2
