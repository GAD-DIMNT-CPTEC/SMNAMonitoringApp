#! /bin/bash -x

# Script to start up the processess related to the SMNAMonitoringApp (i.e., get the current date and update the dates within scripts).
#
# Note: make sure to run this script at times 01, 07, 13 and 19 UTC (otherwise it will choke at 00 UTC)
#
# @cfbastarz (March, 2024)

#inctime=${HOME}/bin/inctime

lpath=/share/das/dist/carlos.bastarz/sandbox/SMNAMonitoringApp/cron_scripts

Hosts=("XC50"  "Egeon")

#today=$(date '+%Y%m%d%H')
#today=2025022501
today=2026081201
#today=2024031407
#today=2024031413
#today=2024031419

if [ ${today:8:2} -le 10 ]
then
  todaym1H=${today:0:8}0$((${today:8:2}-1))
else
  todaym1H=${today:0:8}$((${today:8:2}-1))
fi

#yesterday=$(${inctime} ${todaym1H} -1d %y4%m2%d2%h2)
#aweekbefore=$(${inctime} ${todaym1H} -7d %y4%m2%d2%h2)

yesterday=$(date -u +%Y%m%d%H -d "${todaym1H:0:8} ${todaym1H:8:2} -24 hours")
aweekbefore=$(date -u +%Y%m%d%H -d "${todaym1H:0:8} ${todaym1H:8:2} -168 hours")

echo ${todaym1H} > ${lpath}/todaym1H.txt
echo ${aweekbefore} > ${lpath}/aweekbefore.txt

for hostn in ${Hosts[@]}
do

  if [ ${hostn} == "XC50" ]
  then
    smna_install=/lustre_xc50/ioper/models/SMNA-Oper/SMG
    smna_host=login-xc50.cptec.inpe.br
    host_login=carlos_bastarz
    host_name=xc50
    dados_obs=/lustre_xc50/ioper/data/external/\${data}/dataout/NCEP
  elif [ ${hostn} == "Egeon" ]
  then
    smna_install=/mnt/beegfs/ioper/SMNA_v3.0.0.t12717/SMG
    smna_host=egeon.cptec.inpe.br
    host_login=carlos.bastarz
    host_name=egeon
    dados_obs=/oper/dados/dboper/raw/arch/mod/ncep/gdas/\${data:0:4}/\${data:4:2}/\${data:6:2}
  fi

  echo "Updating script ${lpath}/logs/get_logs.sh"
  cat ${lpath}/logs/get_logs.sh-template | sed "s,#DATAI#,${aweekbefore},g" > ${lpath}/logs/get_logs-${hostn,,}.sh
  sed -i "s,#DATAF#,${todaym1H},g" ${lpath}/logs/get_logs-${hostn,,}.sh
  sed -i "s,#LPATH#,${lpath},g" ${lpath}/logs/get_logs-${hostn,,}.sh
  sed -i "s,#HOSTNAME#,${host_name},g" ${lpath}/logs/get_logs-${hostn,,}.sh
  sed -i "s,#SMNAINSTALL#,${smna_install},g" ${lpath}/logs/get_logs-${hostn,,}.sh
  sed -i "s,#HOSTLOGIN#,${host_login},g" ${lpath}/logs/get_logs-${hostn,,}.sh
  sed -i "s,#SMNAHOST#,${smna_host},g" ${lpath}/logs/get_logs-${hostn,,}.sh

  chmod +x ${lpath}/logs/get_logs-${hostn,,}.sh

  echo "Updating script ${lpath}/logs/create_log_csv.sh"
  cat ${lpath}/logs/create_log_csv.sh-template | sed "s,#DATAI#,${aweekbefore},g" > ${lpath}/logs/create_log_csv-${hostn,,}.sh
  sed -i "s,#LPATH#,${lpath},g" ${lpath}/logs/create_log_csv-${hostn,,}.sh
  sed -i "s,#DATAF#,${todaym1H},g" ${lpath}/logs/create_log_csv-${hostn,,}.sh
  sed -i "s,#HOSTNAME#,${host_name},g" ${lpath}/logs/create_log_csv-${hostn,,}.sh
  
  chmod +x ${lpath}/logs/create_log_csv-${hostn,,}.sh

  echo "Updating script ${lpath}/mass/run_create_database.sh"
  cat ${lpath}/mass/run_create_database.sh-template | sed "s,#DATAI#,${aweekbefore},g" > ${lpath}/mass/run_create_database-${hostn,,}.sh
  sed -i "s,#LPATH#,${lpath},g" ${lpath}/mass/run_create_database-${hostn,,}.sh
  sed -i "s,#HOSTNAME#,${host_name},g" ${lpath}/mass/run_create_database-${hostn,,}.sh
  sed -i "s,#DATAF#,${todaym1H},g" ${lpath}/mass/run_create_database-${hostn,,}.sh
  sed -i "s,#HOSTLOGIN#,${host_login},g" ${lpath}/mass/run_create_database-${hostn,,}.sh
  sed -i "s,#SMNAINSTALL#,${smna_install},g" ${lpath}/mass/run_create_database-${hostn,,}.sh
  sed -i "s,#SMNAHOST#,${smna_host},g" ${lpath}/mass/run_create_database-${hostn,,}.sh
  
  chmod +x ${lpath}/mass/run_create_database-${hostn,,}.sh

  echo "Updating script ${lpath}/jo/get_nobs.sh"
  cat ${lpath}/jo/get_nobs.sh-template | sed "s,#DATAI#,${aweekbefore},g" > ${lpath}/jo/get_nobs-${hostn,,}.sh
  sed -i "s,#LPATH#,${lpath},g" ${lpath}/jo/get_nobs-${hostn,,}.sh
  sed -i "s,#DATAF#,${todaym1H},g" ${lpath}/jo/get_nobs-${hostn,,}.sh
  sed -i "s,#SMNAINSTALL#,${smna_install},g" ${lpath}/jo/get_nobs-${hostn,,}.sh
  sed -i "s,#HOSTLOGIN#,${host_login},g" ${lpath}/jo/get_nobs-${hostn,,}.sh
  sed -i "s,#SMNAHOST#,${smna_host},g" ${lpath}/jo/get_nobs-${hostn,,}.sh
  sed -i "s,#HOSTNAME#,${host_name},g" ${lpath}/jo/get_nobs-${hostn,,}.sh
  
  chmod +x ${lpath}/jo/get_nobs-${hostn,,}.sh

  echo "Updating script ${lpath}/obsm/get_inventory.sh"
  cat ${lpath}/obsm/get_inventory.sh-template | sed "s,#DATAI#,${aweekbefore},g" > ${lpath}/obsm/get_inventory-${hostn,,}.sh
  sed -i "s,#LPATH#,${lpath},g" ${lpath}/obsm/get_inventory-${hostn,,}.sh
  sed -i "s,#DATAF#,${todaym1H},g" ${lpath}/obsm/get_inventory-${hostn,,}.sh
  sed -i "s,#SMNAINSTALL#,${smna_install},g" ${lpath}/obsm/get_inventory-${hostn,,}.sh
  sed -i "s,#DADOSOBS#,${dados_obs},g" ${lpath}/obsm/get_inventory-${hostn,,}.sh
  sed -i "s,#HOSTLOGIN#,${host_login},g" ${lpath}/obsm/get_inventory-${hostn,,}.sh
  sed -i "s,#SMNAHOST#,${smna_host},g" ${lpath}/obsm/get_inventory-${hostn,,}.sh
  sed -i "s,#HOSTNAME#,${host_name},g" ${lpath}/obsm/get_inventory-${hostn,,}.sh
  
  chmod +x ${lpath}/obsm/get_inventory-${hostn,,}.sh

  echo "Updating script ${lpath}/jo/SMNA-Dashboard_load_files_create_dataframe_save-new.py"
  cat ${lpath}/jo/SMNA-Dashboard_load_files_create_dataframe_save-new.py-template | sed "s,#DATAI#,${aweekbefore},g" > ${lpath}/jo/SMNA-Dashboard_load_files_create_dataframe_save-${hostn,,}.py
  sed -i "s,#DATAF#,${todaym1H},g" ${lpath}/jo/SMNA-Dashboard_load_files_create_dataframe_save-${hostn,,}.py
  sed -i "s,#BPATH#,${lpath},g" ${lpath}/jo/SMNA-Dashboard_load_files_create_dataframe_save-${hostn,,}.py
  sed -i "s,#HOSTNAME#,${host_name},g" ${lpath}/jo/SMNA-Dashboard_load_files_create_dataframe_save-${hostn,,}.py
  
  echo "Updating script ${lpath}/anls/run_convert_smna_icn_fct_to_zarr_pyBAM.sh"
  cat ${lpath}/anls/run_convert_smna_icn_fct_to_zarr_pyBAM.sh-template | sed "s,#DATAI#,${aweekbefore},g" > ${lpath}/anls/run_convert_smna_icn_fct_to_zarr_pyBAM-${hostn,,}.sh
  sed -i "s,#DATAF#,${todaym1H},g" ${lpath}/anls/run_convert_smna_icn_fct_to_zarr_pyBAM-${hostn,,}.sh
  sed -i "s,#LPATH#,${lpath},g" ${lpath}/anls/run_convert_smna_icn_fct_to_zarr_pyBAM-${hostn,,}.sh
  sed -i "s,#SMNAINSTALL#,${smna_install},g" ${lpath}/anls/run_convert_smna_icn_fct_to_zarr_pyBAM-${hostn,,}.sh
  sed -i "s,#HOSTLOGIN#,${host_login},g" ${lpath}/anls/run_convert_smna_icn_fct_to_zarr_pyBAM-${hostn,,}.sh
  sed -i "s,#SMNAHOST#,${smna_host},g" ${lpath}/anls/run_convert_smna_icn_fct_to_zarr_pyBAM-${hostn,,}.sh
  sed -i "s,#HOSTNAME#,${host_name},g" ${lpath}/anls/run_convert_smna_icn_fct_to_zarr_pyBAM-${hostn,,}.sh

  chmod +x ${lpath}/anls/run_convert_smna_icn_fct_to_zarr_pyBAM-${hostn,,}.sh

  mkdir -p ${lpath}/anls/${hostn,,}

  echo "Updating script ${lpath}/anls/create_catalog.sh"
  cat ${lpath}/anls/create_catalog.sh-template | sed "s,#DATAI#,${aweekbefore},g" > ${lpath}/anls/${hostn,,}/create_catalog.sh
  sed -i "s,#LPATH#,${lpath},g" ${lpath}/anls/${hostn,,}/create_catalog.sh
  sed -i "s,#DATAF#,${todaym1H},g" ${lpath}/anls/${hostn,,}/create_catalog.sh
  sed -i "s,#HOSTNAME#,${host_name},g" ${lpath}/anls/${hostn,,}/create_catalog.sh
  
  chmod +x ${lpath}/anls/create_catalog-${hostn,,}.sh

  echo "Updating script ${lpath}/anls/convert_smna_dataset_to_zarr.py"
  cat ${lpath}/anls/convert_smna_dataset_to_zarr.py-template | sed "s,#DATAI#,${aweekbefore},g" > ${lpath}/anls/${hostn,,}/convert_smna_dataset_to_zarr.py
  sed -i "s,#DATAF#,${todaym1H},g" ${lpath}/anls/${hostn,,}/convert_smna_dataset_to_zarr.py
  sed -i "s,#LPATH#,${lpath},g" ${lpath}/anls/${hostn,,}/convert_smna_dataset_to_zarr.py
  sed -i "s,#HOSTNAME#,${host_name},g" ${lpath}/anls/${hostn,,}/convert_smna_dataset_to_zarr.py

  echo "Updating script ${lpath}/rdiag/run_convert_smna_diag_to_parquet_readDiag.sh"
  cat ${lpath}/rdiag/run_convert_smna_diag_to_parquet_readDiag.sh-template | sed "s,#DATAI#,${aweekbefore},g" > ${lpath}/rdiag/run_convert_smna_diag_to_parquet_readDiag-${hostn,,}.sh
  sed -i "s,#LPATH#,${lpath},g" ${lpath}/rdiag/run_convert_smna_diag_to_parquet_readDiag-${hostn,,}.sh
  sed -i "s,#DATAF#,${todaym1H},g" ${lpath}/rdiag/run_convert_smna_diag_to_parquet_readDiag-${hostn,,}.sh
  sed -i "s,#SMNAINSTALL#,${smna_install},g" ${lpath}/rdiag/run_convert_smna_diag_to_parquet_readDiag-${hostn,,}.sh
  sed -i "s,#HOSTNAME#,${host_name},g" ${lpath}/rdiag/run_convert_smna_diag_to_parquet_readDiag-${hostn,,}.sh
  sed -i "s,#HOSTLOGIN#,${host_login},g" ${lpath}/rdiag/run_convert_smna_diag_to_parquet_readDiag-${hostn,,}.sh
  sed -i "s,#SMNAHOST#,${smna_host},g" ${lpath}/rdiag/run_convert_smna_diag_to_parquet_readDiag-${hostn,,}.sh

  chmod +x ${lpath}/rdiag/run_convert_smna_diag_to_parquet_readDiag-${hostn,,}.sh

  echo "Updating script ${lpath}/rdiag/create_catalog.sh"
  cat ${lpath}/rdiag/create_catalog.sh-template | sed "s,#DATAI#,${aweekbefore},g" > ${lpath}/rdiag/create_catalog-${hostn,,}.sh
  sed -i "s,#LPATH#,${lpath},g" ${lpath}/rdiag/create_catalog-${hostn,,}.sh
  sed -i "s,#DATAF#,${todaym1H},g" ${lpath}/rdiag/create_catalog-${hostn,,}.sh
  sed -i "s,#HOSTNAME#,${host_name},g" ${lpath}/rdiag/create_catalog-${hostn,,}.sh

  chmod +x ${lpath}/rdiag/create_catalog-${hostn,,}.sh

done

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
