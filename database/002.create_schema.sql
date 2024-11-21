-- UTF-8 without BOM
-- скрипт выполняется от имени пользователя qz_user
-- скрипт создаёт в базе данных таблицы, секвенторы, индексы

CREATE SCHEMA IF NOT EXISTS qz AUTHORIZATION qz_user;

DROP INDEX IF EXISTS idx_a_ship_type_id;
DROP INDEX IF EXISTS idx_a_corporation_id;
DROP INDEX IF EXISTS idx_a_character_id;
DROP INDEX IF EXISTS idx_a_alliance_id;
DROP INDEX IF EXISTS idx_a_killmail_id;
DROP TABLE IF EXISTS qz.attackers;

DROP INDEX IF EXISTS idx_v_ship_type_id;
DROP INDEX IF EXISTS idx_v_character_id;
DROP INDEX IF EXISTS idx_pk_v;
DROP TABLE IF EXISTS qz.victims;

DROP INDEX IF EXISTS idx_km_solar_system_id;
DROP INDEX IF EXISTS idx_pk_km;
DROP TABLE IF EXISTS qz.killmails;

DROP INDEX IF EXISTS idx_zkm_location;
DROP INDEX IF EXISTS qz.idx_zkm_id;
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
    zkm_location BIGINT,
    zkm_fitted_value DOUBLE PRECISION,
    zkm_dropped_value DOUBLE PRECISION,
    zkm_destroyed_value DOUBLE PRECISION,
    zkm_total_value DOUBLE PRECISION,
    zkm_points INTEGER,
    zkm_npc BOOLEAN,
    zkm_solo BOOLEAN,
    zkm_awox BOOLEAN,
    zkm_labels TEXT[],
    zkm_created_at TIMESTAMP,
    zkm_updated_at TIMESTAMP,
    CONSTRAINT pk_zkm PRIMARY KEY (zkm_id)
)
TABLESPACE pg_default;

ALTER TABLE qz.zkillmails OWNER TO qz_user;

CREATE UNIQUE INDEX idx_pk_zkm
    ON qz.zkillmails USING btree
    (zkm_id ASC NULLS LAST)
TABLESPACE pg_default;

CREATE INDEX idx_zkm_id
    ON qz.zkillmails USING btree
    (zkm_id ASC NULLS LAST)
TABLESPACE pg_default;

CREATE INDEX idx_zkm_location
    ON qz.zkillmails USING btree
    (zkm_location ASC NULLS LAST)
    WHERE (zkm_location IS NOT NULL);
--------------------------------------------------------------------------------

--------------------------------------------------------------------------------
-- killmails
-- справочник со списоком killmails от esi
--------------------------------------------------------------------------------
CREATE TABLE qz.killmails
(
    km_id INTEGER NOT NULL,
    km_time TIMESTAMP NOT NULL,
    km_moon_id INTEGER,
    km_solar_system_id BIGINT NOT NULL,
    km_war_id INTEGER,
    CONSTRAINT pk_km PRIMARY KEY (km_id),
    CONSTRAINT fk_km_id FOREIGN KEY (km_id)
        REFERENCES qz.zkillmails(zkm_id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE CASCADE
)
TABLESPACE pg_default;

ALTER TABLE qz.killmails OWNER TO qz_user;

CREATE UNIQUE INDEX idx_pk_km
    ON qz.killmails USING btree
    (km_id ASC NULLS LAST)
TABLESPACE pg_default;

CREATE INDEX idx_km_solar_system_id
    ON qz.killmails USING btree
    (km_solar_system_id ASC NULLS LAST)
TABLESPACE pg_default;
--------------------------------------------------------------------------------

--------------------------------------------------------------------------------
-- victims
-- справочник со списоком victims от esi
--------------------------------------------------------------------------------
CREATE TABLE qz.victims
(
    v_killmail_id INTEGER NOT NULL,
    v_alliance_id INTEGER,
    v_character_id INTEGER,
    v_corporation_id INTEGER,
    v_damage_taken INTEGER NOT NULL,
    v_faction_id INTEGER,
    -- TODO: items
    v_position DOUBLE PRECISION[3],
    v_ship_type_id INTEGER NOT NULL,
    CONSTRAINT pk_v PRIMARY KEY (v_killmail_id),
    CONSTRAINT fk_v_id FOREIGN KEY (v_killmail_id)
        REFERENCES qz.killmails(km_id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE CASCADE
)
TABLESPACE pg_default;

ALTER TABLE qz.victims OWNER TO qz_user;

CREATE UNIQUE INDEX idx_pk_v
    ON qz.victims USING btree
    (v_killmail_id ASC NULLS LAST)
TABLESPACE pg_default;

CREATE INDEX idx_v_character_id
    ON qz.victims USING btree
    (v_character_id ASC NULLS LAST)
    WHERE (v_character_id IS NOT NULL);

CREATE INDEX idx_v_ship_type_id
    ON qz.victims USING btree
    (v_ship_type_id ASC NULLS LAST)
TABLESPACE pg_default;
--------------------------------------------------------------------------------

--------------------------------------------------------------------------------
-- attackers
-- справочник со списоком attackers от esi
--------------------------------------------------------------------------------
CREATE TABLE qz.attackers
(
    a_killmail_id INTEGER NOT NULL,
    a_alliance_id INTEGER,
    a_character_id INTEGER,
    a_corporation_id INTEGER,
    a_damage_done INTEGER NOT NULL,
    a_faction_id INTEGER,
    a_final_blow BOOLEAN NOT NULL,
    a_security_status DOUBLE PRECISION NOT NULL,
    a_ship_type_id INTEGER,
    a_weapon_type_id INTEGER,
    CONSTRAINT fk_v_id FOREIGN KEY (a_killmail_id)
        REFERENCES qz.killmails(km_id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE CASCADE
)
TABLESPACE pg_default;

ALTER TABLE qz.attackers OWNER TO qz_user;

CREATE INDEX idx_a_killmail_id
    ON qz.attackers USING btree
    (a_killmail_id ASC NULLS LAST)
TABLESPACE pg_default;

CREATE INDEX idx_a_alliance_id
    ON qz.attackers USING btree
    (a_alliance_id ASC NULLS LAST)
    WHERE (a_alliance_id IS NOT NULL);

CREATE INDEX idx_a_character_id
    ON qz.attackers USING btree
    (a_character_id ASC NULLS LAST)
    WHERE (a_character_id IS NOT NULL);

CREATE INDEX idx_a_corporation_id
    ON qz.attackers USING btree
    (a_corporation_id ASC NULLS LAST)
    WHERE (a_corporation_id IS NOT NULL);

CREATE INDEX idx_a_ship_type_id
    ON qz.attackers USING btree
    (a_ship_type_id ASC NULLS LAST)
    WHERE (a_ship_type_id IS NOT NULL);
--------------------------------------------------------------------------------

-- получаем справку в конце выполнения всех запросов
\d+ qz.
