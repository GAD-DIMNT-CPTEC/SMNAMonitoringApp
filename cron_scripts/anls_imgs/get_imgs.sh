#! /bin/bash -x

# Wrapper script to get images on a remote machine.
#
# @cfbastarz (August, 2026)

set -u

Hosts=(xc50 egeon)

for host in ${Hosts[@]}
do

  LOCAL_PATH="/share/das/dist/carlos.bastarz/sandbox/SMNAMonitoringApp/cron_scripts/anls_imgs"

  if [ $host == "xc50" ]
  then

    REMOTE="carlos_bastarz@login-xc50.cptec.inpe.br"
    REMOTE_PATH="/lustre_xc50/carlos_bastarz/SMNAMonitoringApp/cron_scripts/anls_imgs/imgs"
    SCRIPT="/lustre_xc50/carlos_bastarz/SMNAMonitoringApp/cron_scripts/anls_imgs/qsub_plot_map.sh"
    LOG="/share/das/dist/carlos.bastarz/sandbox/SMNAMonitoringApp/cron_scripts/anls_imgs/get_imgs-$host.log"
    RUNCMD="/opt/pbs/default/bin/qsub"

  elif [ $host == "egeon" ]
  then

    REMOTE="carlos.bastarz@egeon.cptec.inpe.br"
    REMOTE_PATH="/mnt/beegfs/carlos.bastarz/SMNAMonitoringApp/cron_scripts/anls_imgs/imgs"
    SCRIPT="/mnt/beegfs/carlos.bastarz/SMNAMonitoringApp/cron_scripts/anls_imgs/qsub_plot_map.sh"
    LOG="/share/das/dist/carlos.bastarz/sandbox/SMNAMonitoringApp/cron_scripts/anls_imgs/get_imgs-$host.log"
    RUNCMD="/usr/bin/sbatch"

  fi

  timestamp() {
      date '+%Y-%m-%d %H:%M:%S'
  }
  
  echo "[$(timestamp)] Iniciando download de imagens no host $host" >> "$LOG"

  mkdir -p $LOCAL_PATH/$host

  cd $LOCAL_PATH/$host

  if rsync -arv $REMOTE:${REMOTE_PATH}/* . >> "$LOG" 2>&1
  then
      echo "[$(timestamp)] Download de imagens finalizado com sucesso no host $host" >> "$LOG"
  else
      rc=$?
      echo "[$(timestamp)] ERRO: Acesso às imagens falhou (status $rc) no host $host" >> "$LOG"
      #exit "$rc"
  fi

done

exit 0
