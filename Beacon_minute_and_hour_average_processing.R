#This script is used to further process minute-averaged Beacon files. The incoming timestamp is in UTC.
#The script brings in the minute-averaged and stpp-corrected csv from the python programs
#min_avg_m.py and stpp_correct.py, cleans up the data frame (see annotated code below), and then 
#makes an hour-averaged file from the minute-averaged file. In the final csvs, there are columns 
#for both UTC and local time. The local timestamp automatically adjusts for daylight savings' time.

##################################################################################
#************************ NEEDED FUNCTIONS & PACKAGES ***************************#
##################################################################################

print("Starting R processing")
suppressMessages(library(lubridate)) #package to process date data
suppressMessages(library(chron)) #package to process date data
suppressMessages(library(gridExtra)) #package to print data table
options(scipen=999) #avoiding scientific notation
std.err <- function(x) sd(x, na.rm=T)/(sqrt(length(x[is.finite(x)]))) #standard error function

##################################################################################
#**************************** TIME ZONE SELECTION *******************************#
##################################################################################

args_from_python = commandArgs(trailingOnly=TRUE) #Reading in arguments passed to R from Python program

if(args_from_python[1]=="Pacific") #Selecting time zone based on user input in Python program
{
  time_zone = "PST8PDT"
} else if(args_from_python[1]=="Mountain"){
  time_zone = "MST7MDT"
} else if(args_from_python[1]=="Central"){
  time_zone = "CST6CDT"
} else if(args_from_python[1]=="Eastern"){
  time_zone = "EST5EDT"
} else if(args_from_python[1]=="Taiwan"){
  time_zone = "Asia/Taipei"
}

##################################################################################
#***************************** MINUTE-AVERAGED DATA *****************************#
##################################################################################

############# READING IN AND MANAGING UNPROCESSED BEACON DATA #############
setwd(args_from_python[2]) #Setting working directory with path variable from Python
minute_averaged_data=read.csv("initial_output.csv", header=FALSE) #The minute-averaged, STPP-corrected Beacon data for this site
minute_averaged_data=minute_averaged_data[,-24] #delete empty last column if it exists
nam=c("NA_1","Pressure", "BME_temp", "Rh", "Dew_pt", "NA_2","NA_3", #column name vector
      "NA_4", "O3_wrk", "O3_aux", "CO_wrk", "CO_aux", "NO_wrk", "NO_aux",
      "NO2_wrk", "NO2_aux","PM_hi","PM_lo","PM_pct_fs","CO2_raw","Vaisala_temp",
      "Date_time_UTC", "CO2_STPP")
colnames(minute_averaged_data)=nam #set column names in minute-averaged file

############# Identify and create different date and day columns, make a local time column
minute_averaged_data$Date_time_UTC=ymd_hms(minute_averaged_data$Date_time_UTC) #formatting Date_time_UTC column as a POSIX (date/time) column
minute_averaged_data$Date_time_UTC_2=minute_averaged_data$Date_time_UTC #duplicate the UTC time column, required because the next two lines will reset the time in both columns
minute_averaged_data$Date_time_local=attr(minute_averaged_data$Date_time_UTC_2, "tzone") <- time_zone #make a local time column and set the time zone to local
minute_averaged_data$Date_time_local=as.POSIXct(minute_averaged_data$Date_time_UTC_2, format="%m/%d/%Y %H:%M:%S",tz=time_zone) #use the duplicated UTC time column to read in time in local
minute_averaged_data=minute_averaged_data[,-24] #delete the extra UTC time column
minute_averaged_data$Date_only_local=date(minute_averaged_data$Date_time_local) #making a column that has only the local date without the time
minute_averaged_data$Weekday_local=strftime(minute_averaged_data[,"Date_time_local"],'%A',tz=time_zone) #making a local weekday column
minute_averaged_data$Julian_local=yday(as.Date(minute_averaged_data$Date_time_local,tz=time_zone)) #making a local Julian day column

############# Remove first entry when there are duplicate timestamps
minute_averaged_data$Index=seq(1,nrow(minute_averaged_data),by=1) #make an index column with count of rows
remdup=minute_averaged_data[duplicated(minute_averaged_data[,"Date_time_UTC"])=="TRUE","Index"] #getting row numbers for first row of data with duplicate timestamps
if(length(remdup)==0) #conditional statement to remove duplicate timestamp rows if they exist
{
  minute_averaged_data=minute_averaged_data
} else {
  minute_averaged_data=minute_averaged_data[-remdup,]
}
minute_averaged_data$Index=seq(1,nrow(minute_averaged_data),by=1) #recalculate index (row number) with rows deleted

############# Making a local Julian date column with decimal for time
minute_averaged_data$Julian_decimal_local=minute_averaged_data$Julian_local+(as.numeric(times(strftime(minute_averaged_data$Date_time_local,"%H:%M:%S"))))

##################################################################################
#***************************** HOUR-AVERAGED DATA *******************************#
##################################################################################

hours=minute_averaged_data #create new data frame from a copy of the minute-averaged data frame
hours$datehour=cut(as.POSIXct(hours$Date_time_UTC, #round time to hour-only for averaging
  format="%Y/%m/%d %H:%M:%S"), breaks="hour")
hours$datehour=(as.character(hours$datehour)) #format the hours column as a character so that...
hours$datehour=as.POSIXct(hours$datehour,tz="UTC") #...we can format it as a date/time column here

hour_averaged_data=NA #calculate the hourly mean of each column
suppressWarnings(for(i in c(1:29)) { #NOTE that suppressed warnings are from inability to average non-numeric columns; will address below
  value=aggregate(hours[,i], list(hours$datehour), mean, na.rm=T)
  if(i==1){
    hour_averaged_data=cbind(hour_averaged_data,value)
  } else {
    hour_averaged_data=cbind(hour_averaged_data,value[,2])
  }
})

hour_averaged_data=hour_averaged_data[,-c(1,3,24,26,28)] #remove unnecessary columns
colnames(hour_averaged_data)=c("Date_time_UTC","Pressure","BME_temp","Rh","Dew_pt", "NA_1","NA_2","NA_3", #name columns
                    "O3_wrk","O3_aux","CO_wrk","CO_aux","NO_wrk","NO_aux","NO2_wrk","NO2_aux", #NOTE that "local" columns are not yet in local time
                    "PM_hi","PM_lo","PM_pct_fs","CO2_raw","Vaisala_temp","CO2_STPP","Date_only_local",
                    "Julian_local","Index","Julian_decimal_local")

############# Make a time column in UTC
hour_averaged_data$Date_time_UTC_2=hour_averaged_data$Date_time_UTC #duplicate the UTC time column, required because the next two lines will reset the time in both columns
hour_averaged_data$Date_time_local=attr(hour_averaged_data$Date_time_UTC_2, "tzone") <- time_zone #make a local time column and set the time zone for local time
hour_averaged_data$Date_time_local=as.POSIXct(hour_averaged_data$Date_time_UTC_2, format="%m/%d/%Y %H:%M:%S",tz=time_zone) #use the duplicated UTC time column to read in time in local
hour_averaged_data=hour_averaged_data[,-27] #delete the extra UTC time column

############# Identify and create different date and day columns
hour_averaged_data$Index=as.numeric(rownames(hour_averaged_data)) #recalculate the index column with count of rows
hour_averaged_data$Date_only_local=date(hour_averaged_data$Date_time_local) #recalculating the column that has only the local date without the time
hour_averaged_data$Julian_local=yday(as.Date(hour_averaged_data$Date_time_local,tz=time_zone)) #recalculating the local Julian day column
hour_averaged_data$Weekday_local=strftime(hour_averaged_data[,"Date_time_local"],'%A',tz=time_zone) #recalculating the local weekday column
hour_averaged_data$Julian_decimal_local=hour_averaged_data$Julian_local+(as.numeric(times(strftime(hour_averaged_data$Date_time_local,"%H:%M:%S")))) # Recalculating the local Julian date column with decimal for time
hour_averaged_data[is.na(hour_averaged_data)] <- NA #convert all NA values in data frame to NA

##################################################################################
#**************************** REARRANGE COLUMNS *********************************#
##################################################################################

minute_averaged_data=minute_averaged_data[,c(28,22,24,25,26,27,29,2,3,21,4,5,9:19,20,23)]
hour_averaged_data=hour_averaged_data[,c(25,1,27,23,28,24,26,2,3,21,4,5,9:19,20,22)]

##################################################################################
#*********************************** SAVE FILES *********************************#
##################################################################################

shell_cmd=(paste("mkdir ", paste(args_from_python[2],"/",args_from_python[3],args_from_python[4],"_to_",args_from_python[5],"_temporary_processing",sep=""),sep=""))
system(shell_cmd)
setwd(paste(args_from_python[2],"/",args_from_python[3],args_from_python[4],"_to_",args_from_python[5],"_temporary_processing",sep=""))
write.csv(minute_averaged_data, paste(args_from_python[3],"_",args_from_python[4],"_to_",args_from_python[5],"_","minute_averaged_STPP_corrected.csv",sep=""))
write.csv(hour_averaged_data, paste(args_from_python[3],"_",args_from_python[4],"_to_",args_from_python[5],"_","hour_averaged_STPP_corrected.csv",sep=""))

##################################################################################
#*************************** LOOKING AT DATA RECORD ******************************#
##################################################################################

#Creating data table of min and max values for selected measurements over period
out=NULL
for(j in c(8:12,24,25)){
  Value <- (colnames(hour_averaged_data[j]))
  Minimum_hour_avg_value <- round(min(hour_averaged_data[c(0:length(hour_averaged_data$Index)),j],na.rm=T),2)
  Maximum_hour_avg_value <- round(max(hour_averaged_data[c(0:length(hour_averaged_data$Index)),j],na.rm=T),2)
  d <- data.frame(Value,Minimum_hour_avg_value,Maximum_hour_avg_value)
  out=rbind(out,d)
}

#Making plots of all data over period
filename=paste(paste(args_from_python[3],"_",args_from_python[4],"_to_",args_from_python[5],"_","PLOTS.pdf",sep=""))
pdf(filename,width=7, height=5,onefile=T)
grid.table(out) #adding data table to plots
for(i in c(8:25)){ #printing plots in pdf
  plot(hour_averaged_data[,i], xaxt="n", ylab=paste(colnames(hour_averaged_data[i])), xlab="", xlim=c(0,length(hour_averaged_data$Index)),type='l')
  axis(1,at=seq(1,length(hour_averaged_data$Index),by=(length(hour_averaged_data$Index)/10)),labels=hour_averaged_data[seq(1,length(hour_averaged_data$Index),by=(length(hour_averaged_data$Index)/10)),"Date_only_local"], las=2, cex.axis=0.8)
}
graphics.off()