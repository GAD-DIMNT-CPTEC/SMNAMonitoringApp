#! /bin/bash -x

# Wrapper script to run convert_smna_dataset_to_zarr.py.
#
# @cfbastarz (March, 2024)

source /scripts/das/intel_fortran/intel/oneapi/setvars.sh

export SIGIOBAM=/scripts/das/carlos.bastarz/libsigiobam-1.1-ifort/local
export LD_LIBRARY_PATH=/${SIGIOBAM}/lib:${LD_LIBRARY_PATH}

eval "$(conda shell.bash hook)"
conda activate pyBAM

#inctime=/home/carlos.bastarz/bin/inctime

#lpath=/share/das/dist/carlos.bastarz/SMNAMonitoringApp/anls
lpath=/share/das/dist/carlos.bastarz/sandbox/SMNAMonitoringApp/cron_scripts/anls/xc50
rpath=/lustre_xc50/ioper/models/SMNA-Oper/SMG/datainout/bam/model/dataout/TQ0299L064/DAS

host_name=xc50

datai=2026080500
dataf=2026081200

data=${datai}

while [ ${data} -le ${dataf} ]
do

  #datafct=$(${inctime} ${data} +6h %y4%m2%d2%h2)
  datafct=$(date -u +%Y%m%d%H -d "${data:0:8} ${data:8:2} +6 hours")
  
  # First, get the SMNA analysis from the BAM post-processing in XC50
  mkdir -p ${lpath}/spec_tmp/${data}
  mkdir -p ${lpath}/${data}

  cd ${lpath}/spec_tmp/${data}

  rsync -arv carlos_bastarz@login-xc50.cptec.inpe.br:${rpath}/${data}/GFCTCPT${data}${data}F.icn.TQ0299L064 .
  rsync -arv carlos_bastarz@login-xc50.cptec.inpe.br:${rpath}/${data}/GFCTCPT${data}${data}F.dic.TQ0299L064 .
  rsync -arv carlos_bastarz@login-xc50.cptec.inpe.br:${rpath}/${data}/GFCTCPT${data}${datafct}F.dir.TQ0299L064 .
  rsync -arv carlos_bastarz@login-xc50.cptec.inpe.br:${rpath}/${data}/GFCTCPT${data}${datafct}F.fct.TQ0299L064 .

  cat ${lpath}/../convert_smna_icn_fct_to_zarr_pyBAM.py-template | sed "s,%DATAI%,${data},g" > ${lpath}/convert_smna_icn_fct_to_zarr_pyBAM.py
  sed -i "s,%DATAF%,${datafct},g" ${lpath}/convert_smna_icn_fct_to_zarr_pyBAM.py
  sed -i "s,%LPATH%,${lpath},g" ${lpath}/convert_smna_icn_fct_to_zarr_pyBAM.py
  sed -i "s,%HOSTNAME%,${host_name},g" ${lpath}/convert_smna_icn_fct_to_zarr_pyBAM.py

  /share/das/miniconda3/envs/pyBAM/bin/python3 ${lpath}/convert_smna_icn_fct_to_zarr_pyBAM.py

  #data=$(${inctime} ${data} +6h %y4%m2%d2%h2)
  data=$(date -u +%Y%m%d%H -d "${data:0:8} ${data:8:2} +6 hours")

done

conda deactivate pyBAM

chmod +x ${lpath}/create_catalog.sh

chmod -R 755 ${lpath}/20*

${lpath}/create_catalog.sh
