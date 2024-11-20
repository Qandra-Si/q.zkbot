-- UTF-8 without BOM
-- скрипт выполняется от имени пользователя qz_user
-- скрипт создаёт в базе данных таблицы, секвенторы, индексы

CREATE SCHEMA IF NOT EXISTS qz AUTHORIZATION qz_user;

DROP INDEX IF EXISTS idx_zkm_location;
DROP INDEX IF EXISTS qz.idx_zkm_hash;
DROP INDEX IF EXISTS qz.idx_pk_zkm;
DROP TABLE IF EXISTS qz.zkillmails;


--------------------------------------------------------------------------------
-- zkillmails
-- справочник со списоком killmails с zkillboard
--------------------------------------------------------------------------------
CREATE TABLE qz.zkillmails
(
    zkm_id INTEGER NOT NULL,
    zkm_hash CHARACTER VARYING(40) NOT NULL,
    zkm_location BIGINT NOT NULL,
    zkm_fitted_value DOUBLE PRECISION,
    zkm_dropped_value DOUBLE PRECISION,
    zkm_destroyed_value DOUBLE PRECISION,
    zkm_total_value DOUBLE PRECISION,
    zkm_points INTEGER,
    zkm_npc BOOLEAN,
    zkm_solo BOOLEAN,
    zkm_awox BOOLEAN,
    zkm_labels TEXT[],
    CONSTRAINT pk_zkm PRIMARY KEY (zkm_id)
)
TABLESPACE pg_default;

ALTER TABLE qz.zkillmails OWNER TO qz_user;

CREATE UNIQUE INDEX idx_pk_zkm
    ON qz.zkillmails USING btree
    (zkm_id ASC NULLS LAST)
TABLESPACE pg_default;

CREATE INDEX idx_zkm_hash
    ON qz.zkillmails USING btree
    (zkm_hash ASC NULLS LAST)
TABLESPACE pg_default;

CREATE INDEX idx_zkm_location
    ON qz.zkillmails USING btree
    (zkm_location ASC NULLS LAST)
TABLESPACE pg_default;
--------------------------------------------------------------------------------

-- получаем справку в конце выполнения всех запросов
\d+ qz.