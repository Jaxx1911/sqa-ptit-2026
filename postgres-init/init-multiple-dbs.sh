#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "postgres" <<-EOSQL
    CREATE DATABASE customer_db;
    CREATE DATABASE order_db;
    CREATE DATABASE pay_db;
    CREATE DATABASE ship_db;
    CREATE DATABASE staff_db;
    CREATE DATABASE manager_db;
EOSQL
