#!/bin/sh
cd ../datas
[ -z "$1" ] && exit 1
python3 -c "import crone_api; print(crone_api.get_count('$1'))"
