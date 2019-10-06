#!/bin/bash

set -e
set -u

echo Hello from db-create-script $(basename "$0")

psql -X -U postgres \
	-h localhost \
	--set ON_ERROR_STOP=on \
       	--set AUTOCOMMIT=on \
        -f /docker-entrypoint-initdb.d/init_db.sql.no-autorun \
	postgres
