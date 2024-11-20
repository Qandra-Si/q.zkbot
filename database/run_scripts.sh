#!/bin/bash

#sudo -u postgres psql --port=5432 --file=001.create_db.sql           --echo-errors --log-file=/tmp/001.create_db.log           postgres postgres
sudo -u postgres psql --port=5432 --file=002.create_schema.sql       --echo-errors --log-file=/tmp/002.create_schema.log       qz_db qz_user
