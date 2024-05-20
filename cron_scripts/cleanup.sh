#! /bin/bash -x

# Script to clean up ancient files. For all purpouses, only the last 7 day are kept on disk.
#
# @cfbastarz (March, 2024)

inctime=/home/carlos.bastarz/bin/inctime

lpath=/share/das/dist/carlos.bastarz/SMNAMonitoringApp

Prods=(logs anls obsm rdiag jo)
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
        rm -rf ${lpath}/${prod}/${log}/*${log}_${data:0:8}*
      done
    elif [ ${prod} == "anls" ]
    then
      rm -rf ${lpath}/${prod}/${data:0:8}*
      #rm -rf ${lpath}/${prod}/grib_tmp/${data:0:8}*
      rm -rf ${lpath}/${prod}/spec_tmp/${data:0:8}*
    elif [ ${prod} == "obsm" ]
    then
      rm -rf ${lpath}/${prod}/txt/obs_${data:0:8}*.txt
      rm -rf ${lpath}/${prod}/txt/gsilog_${data:0:8}*.txt
      rm -rf ${lpath}/${prod}/csv/obs_${data:0:8}*.csv
      rm -rf ${lpath}/${prod}/csv/gsilog_${data:0:8}*.csv
    elif [ ${prod} == "rdiag" ]
    then
      rm -rf ${lpath}/${prod}/${data:0:8}*
      rm -rf ${lpath}/${prod}/diag_tmp/${data:0:8}*
    elif [ ${prod} == "jo" ]
    then
      rm -rf ${lpath}/${prod}/preOper/${data:0:8}*
      rm -rf ${lpath}/${prod}/JGerd/${data:0:8}*
    fi

  done

  echo

  data=$(${inctime} ${data} +1d %y4%m2%d2%h2)

done

exit 0
