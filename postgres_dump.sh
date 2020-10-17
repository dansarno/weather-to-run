#!/bin/bash
echo -n "dbname > "
read dbname
echo -n "host > "
read host
echo -n "port > "
read port
echo -n "username > "
read username
echo -n "password > "
read password
echo -n "create file with name > "
read filename
pg_dump postgres://$username:$password@$host:$port/$dbname --no-password --file=$filename --verbose --clean --no-owner --schema-only --no-privileges --if-exists
echo "done"
exit 0
