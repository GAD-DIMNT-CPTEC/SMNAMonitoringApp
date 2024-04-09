#! /bin/bash -x

# Script to start up the processess related to the GSIMonitor (i.e., get the current date and update the dates within scripts).
#
# Note: make sure to run this script at time 01, 07, 13 and 19 UTC (otherwise it will choke at 00 UTC)
#
# @cfbastarz (March, 2024)

inctime=${HOME}/bin/inctime

lpath=/share/das/dist/carlos.bastarz/GSIMonitor

today=$(date '+%Y%m%d%H')
#today=2024031401
#today=2024031407
#today=2024031413
#today=2024031419
if [ ${today:8:2} -le 10 ]
then
  todaym1H=${today:0:8}0$((${today:8:2}-1))
else
  todaym1H=${today:0:8}$((${today:8:2}-1))
fi
yesterday=$(${inctime} ${todaym1H} -1d %y4%m2%d2%h2)
aweekbefore=$(${inctime} ${todaym1H} -7d %y4%m2%d2%h2)

echo ${todaym1H} > ${lpath}/todaym1H.txt
echo ${aweekbefore} > ${lpath}/aweekbefore.txt

echo "Updating script ${lpath}/logs/get_logs.sh"
cat ${lpath}/logs/get_logs.sh-template | sed "s,#DATAI#,${aweekbefore},g" > ${lpath}/logs/get_logs.sh
sed -i "s,#DATAF#,${todaym1H},g" ${lpath}/logs/get_logs.sh

echo "Updating script ${lpath}/logs/create_log_csv.sh"
cat ${lpath}/logs/create_log_csv.sh-template | sed "s,#DATAI#,${aweekbefore},g" > ${lpath}/logs/create_log_csv.sh
sed -i "s,#DATAF#,${todaym1H},g" ${lpath}/logs/create_log_csv.sh

echo "Updating script ${lpath}/obsm/get_inventory.sh"
cat ${lpath}/obsm/get_inventory.sh-template | sed "s,#DATAI#,${aweekbefore},g" > ${lpath}/obsm/get_inventory.sh
sed -i "s,#DATAF#,${todaym1H},g" ${lpath}/obsm/get_inventory.sh

echo "Updating script ${lpath}/jo/get_nobs.sh"
cat ${lpath}/jo/get_nobs.sh-template | sed "s,#DATAI#,${aweekbefore},g" > ${lpath}/jo/get_nobs.sh
sed -i "s,#DATAF#,${todaym1H},g" ${lpath}/jo/get_nobs.sh

echo "Updating script ${lpath}/jo/SMNA-Dashboard_load_files_create_dataframe_save.py"
cat ${lpath}/jo/SMNA-Dashboard_load_files_create_dataframe_save.py-template | sed "s,#DATAI#,${aweekbefore},g" > ${lpath}/jo/SMNA-Dashboard_load_files_create_dataframe_save.py
sed -i "s,#DATAF#,${todaym1H},g" ${lpath}/jo/SMNA-Dashboard_load_files_create_dataframe_save.py

echo "Updating script ${lpath}/anls/run_convert_smna_icn_fct_to_zarr_pyBAM.sh"
cat ${lpath}/anls/run_convert_smna_icn_fct_to_zarr_pyBAM.sh-template | sed "s,#DATAI#,${aweekbefore},g" > ${lpath}/anls/run_convert_smna_icn_fct_to_zarr_pyBAM.sh
sed -i "s,#DATAF#,${todaym1H},g" ${lpath}/anls/run_convert_smna_icn_fct_to_zarr_pyBAM.sh

echo "Updating script ${lpath}/anls/create_catalog.sh"
cat ${lpath}/anls/create_catalog.sh-template | sed "s,#DATAI#,${aweekbefore},g" > ${lpath}/anls/create_catalog.sh
sed -i "s,#DATAF#,${todaym1H},g" ${lpath}/anls/create_catalog.sh

#if [ ${todaym1H:8:2} == "00" ]
#then
#
#  echo "Updating script ${lpath}/anls/convert_smna_dataset_to_zarr.py"
#  cat ${lpath}/anls/convert_smna_dataset_to_zarr.py-template | sed "s,#DATAI#,${aweekbefore},g" > ${lpath}/anls/convert_smna_dataset_to_zarr.py
#  sed -i "s,#DATAF#,${todaym1H},g" ${lpath}/anls/convert_smna_dataset_to_zarr.py
#  
#  echo "Updating script ${lpath}/anls/run_convert_smna_dataset_to_zarr.sh"
#  cat ${lpath}/anls/run_convert_smna_dataset_to_zarr.sh-template | sed "s,#DATAI#,${aweekbefore},g" > ${lpath}/anls/run_convert_smna_dataset_to_zarr.sh
#  sed -i "s,#DATAF#,${todaym1H},g" ${lpath}/anls/run_convert_smna_dataset_to_zarr.sh
#  
#  echo "Updating script ${lpath}/anls/create_catalog.sh"
#  cat ${lpath}/anls/create_catalog.sh-template | sed "s,#DATAI#,${aweekbefore},g" > ${lpath}/anls/create_catalog.sh
#  sed -i "s,#DATAF#,${todaym1H},g" ${lpath}/anls/create_catalog.sh
#
#fi

exit 0
