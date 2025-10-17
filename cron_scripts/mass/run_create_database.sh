#! /bin/bash -x

# Wrapper script to run parseF220.py.
#
# @cfbastarz (March, 2025)

#inctime=/home/carlos.bastarz/bin/inctime

lpath=/share/das/dist/carlos.bastarz/SMNAMonitoringApp/mass
rpath=/lustre_xc50/ioper/models/SMNA-Oper/SMG/datainout/gsi/dataout
fout=costFile_Oper.db 

datai=2025100900
dataf=2025101600

data=${datai}

rm ${lpath}/costFile_Oper.db

while [ ${data} -le ${dataf} ]
do

  # First, get the GSI for.220 files
  mkdir -p ${lpath}/mass_tmp/${data}

  cd ${lpath}/mass_tmp/${data}

  rsync -arv carlos_bastarz@login-xc50.cptec.inpe.br:${rpath}/${data}/fort.220 .

#  data=$(${inctime} ${data} +6h %y4%m2%d2%h2)
  data=$(date -u +%Y%m%d%H -d "${data:0:8} ${data:8:2} +6 hours")

done

cd ${lpath}

/scripts/das/conda/envs/sqlite/bin/python3 ${lpath}/parseF220.py -i ${datai} -f ${dataf} --path ${lpath}/mass_tmp --fout ${lpath}/${fout}

chmod 755 ${lpath}/${fout} 
