#! /bin/bash

#datai=2025021800
#dataf=2025022500
datai=2025100300
dataf=2025101000

lpath=/share/das/dist/carlos.bastarz/SMNAMonitoringApp

data=${datai}

while [ ${data} -le ${dataf} ]
do

    UTC=${data:8:2}

    if [ ${UTC} = 00 ]
    then

      # For 00Z 
      ${lpath}/startup.sh
      ${lpath}/logs/get_logs.sh
      ${lpath}/mass/run_create_database.sh
      ${lpath}/jo/get_nobs.sh
      ${lpath}/jo/run_SMNA-Dashboard_load_files_create_dataframe_save.sh
      ${lpath}/logs/create_log_csv.sh
      ${lpath}/obsm/get_inventory.sh
      ${lpath}/anls/run_convert_smna_icn_fct_to_zarr_pyBAM.sh
      ${lpath}/rdiag/run_convert_smna_diag_to_parquet_readDiag.sh
      #${lpath}/cleanup.sh
    
      wait

    elif [ ${UTC} = 06 ]
    then

      # For 06Z
      ${lpath}/startup.sh
      ${lpath}/logs/get_logs.sh
      ${lpath}/mass/run_create_database.sh
      ${lpath}/jo/get_nobs.sh
      ${lpath}/jo/run_SMNA-Dashboard_load_files_create_dataframe_save.sh
      ${lpath}/logs/create_log_csv.sh
      ${lpath}/obsm/get_inventory.sh
      ${lpath}/anls/run_convert_smna_icn_fct_to_zarr_pyBAM.sh
      ${lpath}/rdiag/run_convert_smna_diag_to_parquet_readDiag.sh
      #${lpath}/cleanup.sh
    
      wait

    elif [ ${UTC} = 12 ]
    then

      # For 12Z
      ${lpath}/startup.sh
      ${lpath}/logs/get_logs.sh
      ${lpath}/mass/run_create_database.sh
      ${lpath}/jo/get_nobs.sh
      ${lpath}/jo/run_SMNA-Dashboard_load_files_create_dataframe_save.sh
      ${lpath}/logs/create_log_csv.sh
      ${lpath}/obsm/get_inventory.sh
      ${lpath}/anls/run_convert_smna_icn_fct_to_zarr_pyBAM.sh
      ${lpath}/rdiag/run_convert_smna_diag_to_parquet_readDiag.sh
      #${lpath}/cleanup.sh

      wait
    
    elif [ ${UTC} = 18 ]
    then

      # For 18Z
      ${lpath}/startup.sh
      ${lpath}/logs/get_logs.sh
      ${lpath}/mass/run_create_database.sh
      ${lpath}/jo/get_nobs.sh
      ${lpath}/jo/run_SMNA-Dashboard_load_files_create_dataframe_save.sh
      ${lpath}/logs/create_log_csv.sh
      ${lpath}/obsm/get_inventory.sh
      ${lpath}/anls/run_convert_smna_icn_fct_to_zarr_pyBAM.sh
      ${lpath}/rdiag/run_convert_smna_diag_to_parquet_readDiag.sh
      #${lpath}/cleanup.sh

      wait

    fi

  data=$(date -u +%Y%m%d%H -d "${data:0:8} ${data:8:2} +6 hours")

done

chmod -R 755 ${lpath}/logs ${lpath}/mass ${lpath}/jo ${lpath}/obsm ${lpath}/anls ${lpath}/rdiag

exit 0
