#! /bin/bash -x

# Wrapper script to run convert_smna_diag_to_parquet_readDiag.py.
#
# @cfbastarz (April, 2024)

#eval "$(conda shell.bash hook)"
#conda activate pyBAM

#inctime=/home/carlos.bastarz/bin/inctime

lpath=/share/das/dist/carlos.bastarz/SMNAMonitoringApp/rdiag
rpath=/lustre_xc50/ioper/models/SMNA-Oper/SMG/datainout/gsi/dataout

datai=2025100900
dataf=2025101600

data=${datai}

Loops=(1 3)

while [ ${data} -le ${dataf} ]
do

  mkdir -p /share/das/dist/carlos.bastarz/SMNAMonitoringApp/rdiag/diag_tmp/${data}
  mkdir -p /share/das/dist/carlos.bastarz/SMNAMonitoringApp/rdiag/${data}

  cd /share/das/dist/carlos.bastarz/SMNAMonitoringApp/rdiag/diag_tmp/${data}

  for loop in ${Loops[@]}
  do
    rsync -arv carlos_bastarz@login-xc50.cptec.inpe.br:${rpath}/${data}/diag_conv_0${loop}.${data} .

    cat ${lpath}/convert_smna_diag_to_parquet_readDiag.py-template | sed "s,%DATA%,${data},g" > ${lpath}/convert_smna_diag_to_parquet_readDiag.py
    sed -i "s,%LOOP%,${loop},g" ${lpath}/convert_smna_diag_to_parquet_readDiag.py

    /share/das/miniconda3/envs/readDiag/bin/python3 ${lpath}/convert_smna_diag_to_parquet_readDiag.py
  done

  #data=$(${inctime} ${data} +6h %y4%m2%d2%h2)
  data=$(date -u +%Y%m%d%H -d "${data:0:8} ${data:8:2} +6 hours")

done

#conda deactivate pyBAM

chmod +x /share/das/dist/carlos.bastarz/SMNAMonitoringApp/rdiag/create_catalog.sh

chmod -R 755 /share/das/dist/carlos.bastarz/SMNAMonitoringApp/rdiag/20*

/share/das/dist/carlos.bastarz/SMNAMonitoringApp/rdiag/create_catalog.sh
