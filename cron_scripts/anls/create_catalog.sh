#! /bin/bash -x

#inctime=${HOME}/bin/inctime

lpath=/share/das/dist/carlos.bastarz/SMNAMonitoringApp/anls

Names=(anl bkg)

for name in ${Names[@]}
do

  datai=2025100900
  dataf=2025101600
  
  data=${datai}

  echo "sources:" > ${lpath}/catalog_${name}.yml
  
  while [ ${data} -le ${dataf} ]
  do
  
    echo ${data}
  
  if [ ${name} == "anl" ]
  then

cat << EOF >> ${lpath}/catalog_${name}.yml

  '${data}':
    args:
      consolidated: true
      urlpath: https://dataserver.cptec.inpe.br/dataserver_dimnt/das/carlos.bastarz/SMNAMonitoringApp/anls/${data}/GFCTCPT${data}${data}F.icn.TQ0299L064.zarr
    description: SMNA Analysis for ${data}
    driver: intake_xarray.xzarr.ZarrSource
    metadata: 
      catalog_dir: https://dataserver.cptec.inpe.br/dataserver_dimnt/das/carlos.bastarz/SMNAMonitoringApp/anls/${data}
      tags:
        - atmosphere
        - analysis
        - data_assimilation
        - smna
        - field
      url: https://dataserver.cptec.inpe.br/dataserver_dimnt/das/carlos.bastarz/SMNAMonitoringApp/anls/${data}

EOF
  
    chmod 755 ${lpath}/catalog_${name}.yml

  else

    #datafct=$(${inctime} ${data} +6h %y4%m2%d2%h2)
    datafct=$(date -u +%Y%m%d%H -d "${data:0:8} ${data:8:2} +6 hours")

cat << EOF >> ${lpath}/catalog_${name}.yml

  '${data}':
    args:
      consolidated: true
      urlpath: https://dataserver.cptec.inpe.br/dataserver_dimnt/das/carlos.bastarz/SMNAMonitoringApp/anls/${data}/GFCTCPT${data}${datafct}F.fct.TQ0299L064.zarr
    description: SMNA Analysis for ${data}
    driver: intake_xarray.xzarr.ZarrSource
    metadata: 
      catalog_dir: https://dataserver.cptec.inpe.br/dataserver_dimnt/das/carlos.bastarz/SMNAMonitoringApp/anls/${data}
      tags:
        - atmosphere
        - background
        - data_assimilation
        - smna
        - field
      url: https://dataserver.cptec.inpe.br/dataserver_dimnt/das/carlos.bastarz/SMNAMonitoringApp/anls/${data}

EOF

    chmod 755 ${lpath}/catalog_${name}.yml
  
  fi
  
    #data=$(${inctime} ${data} +6h %y4%m2%d2%h2)
    data=$(date -u +%Y%m%d%H -d "${data:0:8} ${data:8:2} +6 hours")
  
  done

done

exit 0
