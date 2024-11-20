-- UTF-8 without BOM
-- скрипт выполняется с правами суперпользователя postgres
-- скрипт создаёт табличные пространства, базу данных, пользователя для работы с новой БД и выдаёт права

DROP DATABASE qz_db;
DROP USER qz_user;

CREATE DATABASE qz_db
    WITH 
    --по умолчанию:OWNER = postgres
    ENCODING = 'UTF8'
    --порядок сортировки:LC_COLLATE = 'Russian_Russia.1251'
    --порядок сортировки:LC_CTYPE = 'Russian_Russia.1251'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1;

--по умолчанию:GRANT ALL ON DATABASE qz_db TO postgres;
--по умолчанию:GRANT TEMPORARY, CONNECT ON DATABASE qz_db TO PUBLIC;

CREATE USER qz_user
    WITH
    LOGIN PASSWORD 'qz_LAZ7dBLmSJb9' -- this is the value you probably need to edit
    NOSUPERUSER
    INHERIT
    NOCREATEDB
    NOCREATEROLE
    NOREPLICATION;

GRANT ALL ON DATABASE qz_db TO qz_user;
