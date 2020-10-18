#!/bin/bash
echo -n "DB URI > "
read dburi
echo -n "Create file with name > "
read filename
pg_dump $dburi --no-password --file=$filename --verbose --clean --no-owner --no-privileges --if-exists
echo "done"
exit 0
