#! /bin/bash -x

# Script para obter e organizar as informações dos logs do GSI
# para dois experimentos.

# Na máquina local, montar os discos da seguinte forma:
# $ cd /extra2
# $ sshfs carlos_bastarz@login-xc50.cptec.inpe.br:/lustre_xc50/ioper/models/SMNA-Oper/SMG/datainout/gsi/dataout XC50_SMNA_GSI_dataout_preOper
# $ sshfs carlos_bastarz@login-xc50.cptec.inpe.br:/lustre_xc50/joao_gerd/SMNA-Oper/SMG/datainout/gsi/dataout XC50_SMNA_GSI_dataout_JGerd
# $ sshfs carlos.bastarz@egeon.cptec.inpe.br:/mnt/beegfs/jose.aravequia/SMG/datainout/gsi/dataout EGEON_SMNA_GSI_dataout_JAraveq

# @cfbastarz (31/08/2023)

#inctime=${HOME}/bin/inctime

#Exps=(JGerd preOper preOper.new)
Exps=(JGerd preOper)

datai=2025100900
dataf=2025101600

data=${datai}

while [ ${data} -le ${dataf} ]
do

  for exp in ${Exps[@]}
  do

    echo ${data} ${exp}

    lpath=/share/das/dist/carlos.bastarz/SMNAMonitoringApp/jo/${exp}
    #if [ ${data} -ge 2024021300 -a ${exp} == "preOper" ]
    if [ ${exp} == "preOper" ]
    then
      if [ ${data} -ge 2024021300 -a ${data} -le 2024022018 ]
      then
        rpath=/lustre_xc50/ioper/models/SMNA-Oper/SMG/datainout/gsi/dataout/ERR_BKP
      else
        rpath=/lustre_xc50/ioper/models/SMNA-Oper/SMG/datainout/gsi/dataout
      fi
    elif [ ${exp} == "preOper.new" ]
    then
      rpath=/lustre_xc50/ioper/models/SMNA-Oper/SMG/datainout/gsi/dataout
    elif [ ${exp} == "JGerd" ]
    then
      rpath=/lustre_xc50/joao_gerd/SMNA-Oper/SMG/datainout/gsi/dataout
    fi

    mkdir -p ${lpath}/${data}

    #logf=$(ls -t1 ${rpath}/${data}/gsiStdout_${data}.runTime-*.log | head -1)
    logf=$(ssh carlos_bastarz@login-xc50.cptec.inpe.br ls -t1 ${rpath}/${data}/gsiStdout_${data}.runTime-*.log | head -1)
  
    mkdir -p ${lpath}/${data}
  
    #cp -v ${logf} ${lpath}/${data}/gsiStdout_${data}.log
    scp -v carlos_bastarz@login-xc50.cptec.inpe.br:${logf} ${lpath}/${data}/gsiStdout_${data}.log

  done

  #data=$(${inctime} ${data} +6hr %y4%m2%d2%h2)
  data=$(date -u +%Y%m%d%H -d "${data:0:8} ${data:8:2} +6 hours")

done

exit 0
