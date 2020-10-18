#!/bin/bash
dbname=postgres
username=postgres
port=5432
host=localhost

echo -n "Dump file path > "
read filename

echo -e "Restoring database from $filename \n\n"

psql --dbname=$dbname --file=$filename --echo-all --echo-errors --host=$host --port=$port --username=$username
echo "done"

exit 0
