#!/bin/sh
day=$(date +%Y%m%d%H%M%S)
[ -d "caches" ] || mkdir caches
cd caches
[ -e "maps-$day.json" ] && exit 1
find -name \*.json -exec gzip -q {} \;
cd ..
python -c 'import crone_api, json; print(json.dumps(crone_api.get_maps()))' > "caches/maps-$day.json" || rm "caches/maps-$day.json"
