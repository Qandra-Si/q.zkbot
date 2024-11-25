-- UTF-8 without BOM
-- скрипт выполняется от имени пользователя qz_user
-- скрипт создаёт в базе данных таблицы, секвенторы, индексы

CREATE SCHEMA IF NOT EXISTS qz AUTHORIZATION qz_user;

DROP INDEX IF EXISTS idx_ess_constellation_id;
DROP INDEX IF EXISTS idx_ess_pk;
DROP TABLE IF EXISTS qz.esi_systems;

DROP INDEX IF EXISTS idx_esc_region_id;
DROP INDEX IF EXISTS idx_esc_pk;
DROP TABLE IF EXISTS qz.esi_constellations;

DROP INDEX IF EXISTS idx_esr_pk;
DROP TABLE IF EXISTS qz.esi_regions;

DROP INDEX IF EXISTS idx_sdet_created_at;
DROP INDEX IF EXISTS idx_sdet_pk;
DROP TABLE IF EXISTS qz.eve_sde_type_ids;

DROP INDEX IF EXISTS idx_eal_pk;
DROP TABLE IF EXISTS qz.esi_alliances;

DROP INDEX IF EXISTS idx_eco_pk;
DROP TABLE IF EXISTS qz.esi_corporations;

DROP INDEX IF EXISTS idx_ech_pk;
DROP TABLE IF EXISTS qz.esi_characters;

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
    zkm_published BOOLEAN NOT NULL DEFAULT FALSE, -- признак того, что сообщение опубликовано в discord-е
    zkm_need_refresh BOOLEAN NOT NULL DEFAULT FALSE, -- признак того, что сообщение надо обновить в discord-е
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

CREATE INDEX idx_zkm_published
    ON qz.zkillmails USING btree
    (zkm_published ASC NULLS LAST)
TABLESPACE pg_default;

CREATE INDEX idx_zkm_need_refresh
    ON qz.zkillmails USING btree
    (zkm_need_refresh ASC NULLS LAST)
TABLESPACE pg_default;
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

--------------------------------------------------------------------------------
-- esi_characters
-- справочник со списком пилотов
--------------------------------------------------------------------------------
CREATE TABLE qz.esi_characters (
    ech_character_id BIGINT NOT NULL,
    ech_name CHARACTER VARYING(255) NOT NULL,
    -- ech_corporation_id BIGINT NOT NULL,
    -- ech_description TEXT,
    -- ech_birthday CHARACTER VARYING(255) NOT NULL,
    -- ech_gender CHARACTER VARYING(255) NOT NULL,
    -- ech_race_id INTEGER NOT NULL,
    -- ech_bloodline_id INTEGER NOT NULL,
    -- ech_ancestry_id INTEGER,
    -- ech_security_status DOUBLE PRECISION,
    ech_created_at TIMESTAMP,
    ech_updated_at TIMESTAMP,
    CONSTRAINT pk_ech PRIMARY KEY (ech_character_id)
)
TABLESPACE pg_default;

ALTER TABLE qz.esi_characters OWNER TO qz_user;

CREATE UNIQUE INDEX idx_ech_pk
    ON qz.esi_characters USING btree
    (ech_character_id ASC NULLS LAST)
TABLESPACE pg_default;
--------------------------------------------------------------------------------

--------------------------------------------------------------------------------
-- esi_corporations
-- справочник со списком корпораций
--------------------------------------------------------------------------------
CREATE TABLE qz.esi_corporations (
    eco_corporation_id BIGINT NOT NULL,
    eco_name CHARACTER VARYING(255) NOT NULL,
    -- eco_ticker CHARACTER VARYING(255) NOT NULL,
    -- eco_member_count INTEGER NOT NULL,
    -- eco_ceo_id BIGINT NOT NULL,
    -- eco_alliance_id INTEGER,
    -- eco_description TEXT,
    -- eco_tax_rate DOUBLE PRECISION NOT NULL,
    -- eco_date_founded TIMESTAMP,
    -- eco_creator_id BIGINT NOT NULL,
    -- eco_url CHARACTER VARYING(510),
    -- eco_faction_id INTEGER,
    -- eco_home_station_id INTEGER,
    -- eco_shares BIGINT,
    eco_created_at TIMESTAMP,
    eco_updated_at TIMESTAMP,
    CONSTRAINT pk_eco PRIMARY KEY (eco_corporation_id)
)
TABLESPACE pg_default;

ALTER TABLE qz.esi_corporations OWNER TO qz_user;

CREATE UNIQUE INDEX idx_eco_pk
    ON qz.esi_corporations USING btree
    (eco_corporation_id ASC NULLS LAST)
TABLESPACE pg_default;
--------------------------------------------------------------------------------

--------------------------------------------------------------------------------
-- esi_alliances
-- справочник со списком альянсов
--------------------------------------------------------------------------------
CREATE TABLE qz.esi_alliances (
    eal_alliance_id BIGINT NOT NULL,
    eal_name CHARACTER VARYING(255) NOT NULL,
    -- eal_ticker CHARACTER VARYING(255) NOT NULL,
    -- eal_faction_id INTEGER,
    -- eal_creator_corporation_id BIGINT NOT NULL,
    -- eal_creator_id BIGINT NOT NULL,
    -- eal_date_founded CHARACTER VARYING(255) NOT NULL,
    -- eal_executor_corporation_id BIGINT NOT NULL,
    eal_created_at TIMESTAMP,
    eal_updated_at TIMESTAMP,
    CONSTRAINT pk_eal PRIMARY KEY (eal_alliance_id)
)
TABLESPACE pg_default;

ALTER TABLE qz.esi_alliances OWNER TO qz_user;

CREATE UNIQUE INDEX idx_eal_pk
    ON qz.esi_alliances USING btree
    (eal_alliance_id ASC NULLS LAST)
TABLESPACE pg_default;
--------------------------------------------------------------------------------

--------------------------------------------------------------------------------
-- EVE Static Data Interface (typeIDs)
-- сведения о параметрах типах присутствующих в игре элементов, из typeIDs.yaml
--------------------------------------------------------------------------------
CREATE TABLE qz.eve_sde_type_ids
(
    sdet_type_id INTEGER NOT NULL,
    sdet_type_name CHARACTER VARYING(255),
    -- sdet_group_id INTEGER NOT NULL,
    -- sdet_volume DOUBLE PRECISION,
    -- sdet_capacity DOUBLE PRECISION,
    -- sdet_base_price BIGINT,
    sdet_published BOOLEAN,
    -- sdet_market_group_id INTEGER,
    -- sdet_meta_group_id SMALLINT,
    -- sdet_tech_level SMALLINT,
    sdet_icon_id INTEGER,
    -- sdet_portion_size INTEGER,
    -- sdet_packaged_volume DOUBLE PRECISION,
    sdet_created_at TIMESTAMP DEFAULT (current_timestamp at time zone 'GMT'),
    CONSTRAINT pk_sdet PRIMARY KEY (sdet_type_id)
	-- ,CONSTRAINT fk_sdet_market_group_id FOREIGN KEY (sdet_market_group_id)
    --     REFERENCES qz.eve_sde_market_groups(sdeg_group_id) MATCH SIMPLE
    --     ON UPDATE NO ACTION
    --     ON DELETE NO ACTION,
    -- CONSTRAINT fk_sdet_group_id FOREIGN KEY (sdet_group_id)
    --     REFERENCES qz.eve_sde_group_ids(sdecg_group_id) MATCH SIMPLE
    --     ON UPDATE NO ACTION
    --     ON DELETE NO ACTION
)
TABLESPACE pg_default;

-- COMMENT ON COLUMN qz.eve_sde_type_ids.sdet_meta_group_id IS 'meta-группа, получаем из sde';
-- COMMENT ON COLUMN qz.eve_sde_type_ids.sdet_tech_level IS 'технологический уровень 1..5, получаем из esi'; -- при tech=1 различная meta (abyssal,faction,tech1...)
-- COMMENT ON COLUMN qz.eve_sde_type_ids.sdet_packaged_volume IS 'm3 в упакованном виде, получаем из esi';

ALTER TABLE qz.eve_sde_type_ids OWNER TO qz_user;

CREATE UNIQUE INDEX idx_sdet_pk
    ON qz.eve_sde_type_ids USING btree
    (sdet_type_id ASC NULLS LAST)
TABLESPACE pg_default;

-- CREATE INDEX idx_sdet_group_id
--     ON qz.eve_sde_type_ids USING btree
--     (sdet_group_id ASC NULLS LAST)
-- TABLESPACE pg_default;
-- 
-- CREATE INDEX idx_sdet_market_group_id
--     ON qz.eve_sde_type_ids USING btree
--     (sdet_market_group_id ASC NULLS LAST)
-- TABLESPACE pg_default;

CREATE INDEX idx_sdet_created_at
    ON qz.eve_sde_type_ids USING btree
    (sdet_created_at ASC NULLS LAST)
TABLESPACE pg_default;
--------------------------------------------------------------------------------

--------------------------------------------------------------------------------
-- esi_regions
-- справочник со списком регионов
--------------------------------------------------------------------------------
CREATE TABLE qz.esi_regions (
    esr_region_id BIGINT NOT NULL,
    esr_name CHARACTER VARYING(255) NOT NULL,
    -- description
    esr_created_at TIMESTAMP,
    esr_updated_at TIMESTAMP,
    CONSTRAINT pk_esr PRIMARY KEY (esr_region_id)
)
TABLESPACE pg_default;

ALTER TABLE qz.esi_regions OWNER TO qz_user;

CREATE UNIQUE INDEX idx_esr_pk
    ON qz.esi_regions USING btree
    (esr_region_id ASC NULLS LAST)
TABLESPACE pg_default;
--------------------------------------------------------------------------------

--------------------------------------------------------------------------------
-- esi_constellations
-- справочник со списком созвездий
--------------------------------------------------------------------------------
CREATE TABLE qz.esi_constellations (
    esc_constellation_id BIGINT NOT NULL,
    esc_name CHARACTER VARYING(255) NOT NULL,
    esc_position DOUBLE PRECISION[3] NOT NULL,
    esc_region_id BIGINT NOT NULL,
    esc_created_at TIMESTAMP,
    esc_updated_at TIMESTAMP,
    CONSTRAINT pk_esc PRIMARY KEY (esc_constellation_id)
)
TABLESPACE pg_default;

ALTER TABLE qz.esi_constellations OWNER TO qz_user;

CREATE UNIQUE INDEX idx_esc_pk
    ON qz.esi_constellations USING btree
    (esc_constellation_id ASC NULLS LAST)
TABLESPACE pg_default;

CREATE INDEX idx_esc_region_id
    ON qz.esi_constellations USING btree
    (esc_region_id ASC NULLS LAST)
TABLESPACE pg_default;
--------------------------------------------------------------------------------

--------------------------------------------------------------------------------
-- esi_systems
-- справочник со списком солнечных систем
--------------------------------------------------------------------------------
CREATE TABLE qz.esi_systems (
    ess_system_id BIGINT NOT NULL,
    ess_name CHARACTER VARYING(255) NOT NULL,
    ess_position DOUBLE PRECISION[3] NOT NULL,
    ess_constellation_id BIGINT NOT NULL,
    -- star_id
    -- planets
    -- stations
    -- stargates
    -- security_status
    -- security_class
    ess_created_at TIMESTAMP,
    ess_updated_at TIMESTAMP,
    CONSTRAINT pk_ess PRIMARY KEY (ess_system_id)
)
TABLESPACE pg_default;

ALTER TABLE qz.esi_systems OWNER TO qz_user;

CREATE UNIQUE INDEX idx_ess_pk
    ON qz.esi_systems USING btree
    (ess_system_id ASC NULLS LAST)
TABLESPACE pg_default;

CREATE INDEX idx_ess_constellation_id
    ON qz.esi_systems USING btree
    (ess_constellation_id ASC NULLS LAST)
TABLESPACE pg_default;
--------------------------------------------------------------------------------

-- получаем справку в конце выполнения всех запросов
\d+ qz.
