chcp 1251

@rem psql --file=001.create_db.sql           --echo-errors --log-file=001.create_db.log           postgres postgres
psql --file=002.create_schema.sql       --echo-errors --log-file=002.create_schema.log       qz_db qz_user

pause