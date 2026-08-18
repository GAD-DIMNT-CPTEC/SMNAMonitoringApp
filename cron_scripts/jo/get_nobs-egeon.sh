#! /bin/bash -x

# Script para obter e organizar as informações dos logs do GSI
# para dois experimentos.

# Na máquina local, montar os discos da seguinte forma:
# $ cd /extra2
# $ sshfs carlos_bastarz@login-xc50.cptec.inpe.br:/lustre_xc50/ioper/models/SMNA-Oper/SMG/datainout/gsi/dataout XC50_SMNA_GSI_dataout_preOper
# $ sshfs carlos_bastarz@login-xc50.cptec.inpe.br:/lustre_xc50/joao_gerd/SMNA-Oper/SMG/datainout/gsi/dataout XC50_SMNA_GSI_dataout_JGerd
# $ sshfs carlos.bastarz@egeon.cptec.inpe.br:/mnt/beegfs/jose.aravequia/SMG/datainout/gsi/dataout EGEON_SMNA_GSI_dataout_JAraveq

# @cfbastarz (31/08/2023)

datai=2026080500
dataf=2026081200

data=${datai}

while [ ${data} -le ${dataf} ]
do

  #lpath=/share/das/dist/carlos.bastarz/SMNAMonitoringApp/jo/${exp}
  lpath=/share/das/dist/carlos.bastarz/sandbox/SMNAMonitoringApp/cron_scripts/jo/egeon/${exp}
  rpath=/mnt/beegfs/ioper/SMNA_v3.0.0.t12717/SMG/datainout/gsi/dataout

  mkdir -p ${lpath}/${data}

  logf=$(ssh carlos.bastarz@egeon.cptec.inpe.br ls -t1 ${rpath}/${data}/gsiStdout_${data}.runTime-*.log | head -1)
  
  mkdir -p ${lpath}/${data}
  
  scp -v carlos.bastarz@egeon.cptec.inpe.br:${logf} ${lpath}/${data}/gsiStdout_${data}.log

  data=$(date -u +%Y%m%d%H -d "${data:0:8} ${data:8:2} +6 hours")

done

exit 0
