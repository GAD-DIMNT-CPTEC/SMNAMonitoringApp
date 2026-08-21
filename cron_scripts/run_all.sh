#! /bin/bash -x

datai=2026081400
#dataf=2026082100
dataf=${datai}

lpath=/share/das/dist/carlos.bastarz/sandbox/SMNAMonitoringApp/cron_scripts

data=${datai}

while [ ${data} -le ${dataf} ]
do

    UTC=${data:8:2}

    if [ ${UTC} = 00 ]
    then

      # For 00Z 
      #${lpath}/startup.sh
      ${lpath}/anls_imgs/run_jobs.sh
      ${lpath}/logs/get_logs-egeon.sh
      ${lpath}/logs/get_logs-xc50.sh
      ${lpath}/jo/get_nobs-egeon.sh
      ${lpath}/jo/get_nobs-xc50.sh
      ${lpath}/jo/run_SMNA-Dashboard_load_files_create_dataframe_save-egeon.py
      ${lpath}/jo/run_SMNA-Dashboard_load_files_create_dataframe_save-xc50.py
      ${lpath}/logs/create_log_csv-egeon.sh
      ${lpath}/logs/create_log_csv-xc50.sh
      ${lpath}/obsm/get_inventory-egeon.sh
      ${lpath}/obsm/get_inventory-xc50.sh
      ${lpath}/anls/run_convert_smna_icn_fct_to_zarr_pyBAM-egeon.sh
      ${lpath}/anls/run_convert_smna_icn_fct_to_zarr_pyBAM-xc50.sh
      ${lpath}/rdiag/run_convert_smna_diag_to_parquet_readDiag-egeon.sh
      ${lpath}/rdiag/run_convert_smna_diag_to_parquet_readDiag-xc50.sh
      ${lpath}/anls_imgs/get_imgs-egeon.sh
      ${lpath}/anls_imgs/get_imgs-xc50.sh
      #${lpath}/cleanup.sh

      wait

    elif [ ${UTC} = 06 ]
    then

      # For 06Z
      #${lpath}/startup.sh
      ${lpath}/logs/get_logs-egeon.sh
      ${lpath}/logs/get_logs-xc50.sh
      ${lpath}/jo/get_nobs-egeon.sh
      ${lpath}/jo/get_nobs-xc50.sh
      ${lpath}/jo/run_SMNA-Dashboard_load_files_create_dataframe_save-egeon.py
      ${lpath}/jo/run_SMNA-Dashboard_load_files_create_dataframe_save-xc50.py
      ${lpath}/logs/create_log_csv-egeon.sh
      ${lpath}/logs/create_log_csv-xc50.sh
      ${lpath}/obsm/get_inventory-egeon.sh
      ${lpath}/obsm/get_inventory-xc50.sh
      ${lpath}/anls/run_convert_smna_icn_fct_to_zarr_pyBAM-egeon.sh
      ${lpath}/anls/run_convert_smna_icn_fct_to_zarr_pyBAM-xc50.sh
      ${lpath}/rdiag/run_convert_smna_diag_to_parquet_readDiag-egeon.sh
      ${lpath}/rdiag/run_convert_smna_diag_to_parquet_readDiag-xc50.sh
      #${lpath}/cleanup.sh 

      wait

    elif [ ${UTC} = 12 ]
    then

      # For 12Z
      #${lpath}/startup.sh
      ${lpath}/logs/get_logs-egeon.sh
      ${lpath}/logs/get_logs-xc50.sh
      ${lpath}/jo/get_nobs-egeon.sh
      ${lpath}/jo/get_nobs-xc50.sh
      ${lpath}/jo/run_SMNA-Dashboard_load_files_create_dataframe_save-egeon.py
      ${lpath}/jo/run_SMNA-Dashboard_load_files_create_dataframe_save-xc50.py
      ${lpath}/logs/create_log_csv-egeon.sh
      ${lpath}/logs/create_log_csv-xc50.sh
      ${lpath}/obsm/get_inventory-egeon.sh
      ${lpath}/obsm/get_inventory-xc50.sh
      ${lpath}/anls/run_convert_smna_icn_fct_to_zarr_pyBAM-egeon.sh
      ${lpath}/anls/run_convert_smna_icn_fct_to_zarr_pyBAM-xc50.sh
      ${lpath}/rdiag/run_convert_smna_diag_to_parquet_readDiag-egeon.sh
      ${lpath}/rdiag/run_convert_smna_diag_to_parquet_readDiag-xc50.sh
      #${lpath}p/cleanup.sh
      
      wait
    
    elif [ ${UTC} = 18 ]
    then

      # For 18Z
      #${lpath}/startup.sh
      ${lpath}/logs/get_logs-egeon.sh
      ${lpath}/logs/get_logs-xc50.sh
      ${lpath}/jo/get_nobs-egeon.sh
      ${lpath}/jo/get_nobs-xc50.sh
      ${lpath}/jo/run_SMNA-Dashboard_load_files_create_dataframe_save-egeon.py
      ${lpath}/jo/run_SMNA-Dashboard_load_files_create_dataframe_save-xc50.py
      ${lpath}/logs/create_log_csv-egeon.sh
      ${lpath}/logs/create_log_csv-xc50.sh
      ${lpath}/obsm/get_inventory-egeon.sh
      ${lpath}/obsm/get_inventory-xc50.sh
      ${lpath}/anls/run_convert_smna_icn_fct_to_zarr_pyBAM-egeon.sh
      ${lpath}/anls/run_convert_smna_icn_fct_to_zarr_pyBAM-xc50.sh
      ${lpath}/rdiag/run_convert_smna_diag_to_parquet_readDiag-egeon.sh
      ${lpath}/rdiag/run_convert_smna_diag_to_parquet_readDiag-xc50.sh
      #${lpath}/cleanup.sh

      wait

    fi

  data=$(date -u +%Y%m%d%H -d "${data:0:8} ${data:8:2} +6 hours")

done

chmod -R 755 ${lpath}/logs ${lpath}/mass ${lpath}/jo ${lpath}/obsm ${lpath}/anls ${lpath}/anls_imgs ${lpath}/rdiag

exit 0
