#! /bin/bash -x

# Wrapper script to run jobs on a remote machine.
#
# @cfbastarz (August, 2026)

set -u

Hosts=(xc50 egeon)

for host in ${Hosts[@]}
do

  if [ $host == "xc50" ]
  then

    REMOTE="carlos_bastarz@login-xc50.cptec.inpe.br"
    SCRIPT="/lustre_xc50/carlos_bastarz/SMNAMonitoringApp/cron_scripts/anls_imgs/qsub_plot_map.sh"
    LOG="/share/das/dist/carlos.bastarz/sandbox/SMNAMonitoringApp/cron_scripts/anls_imgs/plot_map-$host.log"
    STARTCMD="/lustre_xc50/carlos_bastarz/SMNAMonitoringApp/cron_scripts/anls_imgs/startup.sh"
    RUNCMD="/opt/pbs/default/bin/qsub"

  elif [ $host == "egeon" ]
  then

    REMOTE="carlos.bastarz@egeon.cptec.inpe.br"
    SCRIPT="/mnt/beegfs/carlos.bastarz/SMNAMonitoringApp/cron_scripts/anls_imgs/qsub_plot_map.sh"
    LOG="/share/das/dist/carlos.bastarz/sandbox/SMNAMonitoringApp/cron_scripts/anls_imgs/plot_map-$host.log"
    STARTCMD="/mnt/beegfs/carlos.bastarz/SMNAMonitoringApp/cron_scripts/anls_imgs/startup.sh"
    RUNCMD="/usr/bin/sbatch"

  fi

  timestamp() {
      date '+%Y-%m-%d %H:%M:%S'
  }
  
  echo "[$(timestamp)] Iniciando submissão no host $host" >> "$LOG"
  
  if ssh \
      -o BatchMode=yes \
      -o ConnectTimeout=30 \
      -o ServerAliveInterval=30 \
      -o ServerAliveCountMax=3 \
      "$REMOTE" \
      "'$STARTCMD'" >> "$LOG" 2>&1
  then
      echo "[$(timestamp)] Start realizado com sucesso no host $host" >> "$LOG"
  else
      rc=$?
      echo "[$(timestamp)] ERRO: start remoto falhou (status $rc) no host $host" >> "$LOG"
      #exit "$rc"
  fi

  if ssh \
      -o BatchMode=yes \
      -o ConnectTimeout=30 \
      -o ServerAliveInterval=30 \
      -o ServerAliveCountMax=3 \
      "$REMOTE" \
      "'$SCRIPT'" >> "$LOG" 2>&1
  then
      echo "[$(timestamp)] Submissão realizada com sucesso no host $host" >> "$LOG"
  else
      rc=$?
      echo "[$(timestamp)] ERRO: qsub remoto falhou (status $rc) no host $host" >> "$LOG"
      #exit "$rc"
  fi

done

exit 0
