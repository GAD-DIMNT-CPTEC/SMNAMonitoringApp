#! /bin/bash -x

# Script to clean up ancient files. For all purpouses, only the last 7 day are kept on disk.
#
# @cfbastarz (March, 2024)

inctime=/home/carlos.bastarz/bin/inctime

lpath=/share/das/dist/carlos.bastarz/SMNAMonitoringApp

Prods=(logs anls obsm)
Logs=(gsi pre model pos)

now=$(date '+%Y%m%d')00

nowm7d=$(${inctime} $now -7d %y4%m2%d2%h2)
nowm14d=$(${inctime} $now -14d %y4%m2%d2%h2)

datai=${nowm14d}
dataf=${nowm7d}

data=${datai}

while [ ${data} -le ${dataf} ]
do

  echo ${now} ${now7d} ${nowm14d} ${data}

  for prod in ${Prods[@]}
  do

    if [ ${prod} == "logs" ]
    then
      for log in ${Logs[@]}
      do
        rm -rf ${lpath}/${prod}/${log}/*${log}_${data}*
      done
    elif [ ${prod} == "anls" ]
    then
      rm -rf ${lpath}/${prod}/${data}
      #rm -rf ${lpath}/${prod}/grib_tmp/${data}
      rm -rf ${lpath}/${prod}/spec_tmp/${data}
    elif [ ${prod} == "obsm" ]
    then
      rm -rf ${lpath}/${prod}/txt/obs_${data}*.txt
      rm -rf ${lpath}/${prod}/txt/gsilog_${data}.txt
      rm -rf ${lpath}/${prod}/csv/obs_${data}*.csv
      rm -rf ${lpath}/${prod}/csv/gsilog_${data}.csv
    fi
  done

  echo

  data=$(${inctime} ${data} +1d %y4%m2%d2%h2)

done

exit 0
