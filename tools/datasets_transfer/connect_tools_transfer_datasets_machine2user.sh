#!/bin/bash

time_script_now='2022-05-02 00:00'

src_location_raw='/home/cfmi.arpal.org/continuum/ModelloContinuum/archive/%DOMAIN_NAME/weather_stations_realtime/%YYYY/%mm/%dd/gridded/*'
dst_location_raw='/home/cfmi.arpal.org/fabio.delogu/ModelloContinuum/archive/%DOMAIN_NAME/weather_stations_realtime/%YYYY/%mm/%dd/gridded/'

group_datasets_name=(
    "AvetoTrebbiaDomain" 
    "BormidaMDomain"
    "BormidaSDomain"
    "CentaDomain"
    "CentroPonenteDomain"
    "EntellaDomain"
	"ErroDomain"
	"FinaleseDomain"
	"ImperieseDomain"
	"LevanteGenoveseDomain"
	"MagraDomain"
	"OrbaSturaDomain"
	"PonenteDomain"
	"PonenteDomain"
	"PonenteGenoveseDomain"
	"RoiaDomain"
	"SavoneseDomain"
	"ScriviaDomain"
	"TanaroDomain"
)

group_datasets_period_step=(
    3
    3
    3
    3
    3
    3
	3
	3
	3
	3
	3
	3
	3
	3
	3
	3
	3
	3
	3
)

group_datasets_period_type=(
    "day ago"
    "day ago"
   	"day ago"
    "day ago"
    "day ago"
    "day ago"
	"day ago"
	"day ago"
	"day ago"
	"day ago"
	"day ago"
	"day ago"
	"day ago"
	"day ago"
	"day ago"
	"day ago"
	"day ago"
	"day ago"
	"day ago"
)


time_step=$(date -d "$time_script" +'%Y-%m-%d')
year_step=$(date -u -d "$time_step" +"%Y")
month_step=$(date -u -d "$time_step" +"%m")
day_step=$(date -u -d "$time_step" +"%d")

# Iterate over tags
for datasets_id in "${!group_datasets_name[@]}"; do
     
	datasets_name=${group_datasets_name[datasets_id]}
	datasets_period_step=${group_datasets_period_step[datasets_id]}
	datasets_period_type=${group_datasets_period_type[datasets_id]}
	
	echo " ---> Domain ${datasets_name} ... "

	# Iterate over datasets period
	for period_step in $(seq 0 $datasets_period_step); do
	
		time_step=$(date -d "$time_script_now ${period_step} ${datasets_period_type}" +'%Y-%m-%d %H:00')
		
		echo " ----> Time ${time_step} ... "
		
	    year_step=$(date -u -d "$time_step" +"%Y")
    	month_step=$(date -u -d "$time_step" +"%m")
    	day_step=$(date -u -d "$time_step" +"%d")
    	hour_step=$(date -u -d "$time_step" +"%H")
    	minute_step=$(date -u -d "$time_step" +"%M")
		
		src_location_step=${src_location_raw/'%YYYY'/$year_step}
		src_location_step=${src_location_step/'%mm'/$month_step}
		src_location_step=${src_location_step/'%dd'/$day_step}
		src_location_step=${src_location_step/'%DOMAIN_NAME'/$datasets_name}
		
		dst_location_step=${dst_location_raw/'%YYYY'/$year_step}
		dst_location_step=${dst_location_step/'%mm'/$month_step}
		dst_location_step=${dst_location_step/'%dd'/$day_step}
		dst_location_step=${dst_location_step/'%DOMAIN_NAME'/$datasets_name}
		
		echo " ----> Copy file from ${src_location_step} to ${dst_location_step} ... "
		
		mkdir -p ${dst_location_step}
		
		cp -r ${src_location_step} ${dst_location_step}
		
		echo " ----> Copy file from ${src_location_step} to ${dst_location_step} ... DONE"
		
		echo " ----> Time ${time_step} ... DONE"
	
	done
	
	echo " ---> Domain ${datasets_name} ... DONE"
	
done	



