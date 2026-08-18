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
lpath=#LPATH#/anls
rpath=#SMNAINSTALL#/SMG/datainout/bam/model/dataout/TQ0299L064/DAS

datai=2026080500
dataf=2026081200

data=${datai}

while [ ${data} -le ${dataf} ]
do

  #datafct=$(${inctime} ${data} +6h %y4%m2%d2%h2)
  datafct=$(date -u +%Y%m%d%H -d "${data:0:8} ${data:8:2} +6 hours")
  
  # First, get the SMNA analysis from the BAM post-processing in XC50
  mkdir -p /share/das/dist/carlos.bastarz/SMNAMonitoringApp/anls/spec_tmp/${data}
  mkdir -p /share/das/dist/carlos.bastarz/SMNAMonitoringApp/anls/${data}

  cd /share/das/dist/carlos.bastarz/SMNAMonitoringApp/anls/spec_tmp/${data}

  rsync -arv #SMNALOGIN#@#SMNAHOST#:${rpath}/${data}/GFCTCPT${data}${data}F.icn.TQ0299L064 .
  rsync -arv #SMNALOGIN#@#SMNAHOST#:${rpath}/${data}/GFCTCPT${data}${data}F.dic.TQ0299L064 .
  rsync -arv #SMNALOGIN#@#SMNAHOST#:${rpath}/${data}/GFCTCPT${data}${datafct}F.dir.TQ0299L064 .
  rsync -arv #SMNALOGIN#@#SMNAHOST#:${rpath}/${data}/GFCTCPT${data}${datafct}F.fct.TQ0299L064 .

  cat ${lpath}/convert_smna_icn_fct_to_zarr_pyBAM.py-template | sed "s,%DATAI%,${data},g" > ${lpath}/convert_smna_icn_fct_to_zarr_pyBAM.py
  sed -i "s,%DATAF%,${datafct},g" ${lpath}/convert_smna_icn_fct_to_zarr_pyBAM.py

  /share/das/miniconda3/envs/pyBAM/bin/python3 ${lpath}/convert_smna_icn_fct_to_zarr_pyBAM.py

  #data=$(${inctime} ${data} +6h %y4%m2%d2%h2)
  data=$(date -u +%Y%m%d%H -d "${data:0:8} ${data:8:2} +6 hours")

done

conda deactivate pyBAM

chmod +x /share/das/dist/carlos.bastarz/SMNAMonitoringApp/anls/create_catalog.sh

chmod -R 755 /share/das/dist/carlos.bastarz/SMNAMonitoringApp/anls/20*

/share/das/dist/carlos.bastarz/SMNAMonitoringApp/anls/create_catalog.sh
