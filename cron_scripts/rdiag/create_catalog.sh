#! /bin/bash -x

#inctime=${HOME}/bin/inctime

lpath=/share/das/dist/carlos.bastarz/SMNAMonitoringApp/rdiag

Loops=(diag_conv_01 diag_conv_03)
Vars=(ps t q uv)

for loop  in ${Loops[@]}
do

  datai=2025100900
  dataf=2025101600
  
  data=${datai}

  echo "sources:" > ${lpath}/catalog_${loop}.yml
  
  while [ ${data} -le ${dataf} ]
  do
  
    for var in ${Vars[@]}
    do

      echo ${data} ${var}
  
cat << EOF >> ${lpath}/catalog_${loop}.yml

  '${var}_${loop}_${data}':
    driver: geoparquet
    args:
      urlpath: https://s0.cptec.inpe.br/pesquisa/das/dist/carlos.bastarz/SMNAMonitoringApp/rdiag/${data}/${var}-${loop}.${data}.parquet
    description: SMNA ${var^^} Conventional Diagnostics (${loop:10:2}) for ${data}
    metadata: 
      catalog_dir: https://s0.cptec.inpe.br/pesquisa/das/dist/carlos.bastarz/SMNAMonitoringApp/rdiag/${data}
      tags:
        - atmosphere
        - data_assimilation
        - smna
        - observational diagnostic data
      url: https://s0.cptec.inpe.br/pesquisa/das/dist/carlos.bastarz/SMNAMonitoringApp/rdiag/${data}

EOF

      chmod 755 ${lpath}/catalog_${loop}.yml
  
    done

    #data=$(${inctime} ${data} +6h %y4%m2%d2%h2)
    data=$(date -u +%Y%m%d%H -d "${data:0:8} ${data:8:2} +6 hours")
  
  done

done


exit 0
