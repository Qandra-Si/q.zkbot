-- UTF-8 without BOM
-- скрипт выполняется от имени пользователя qz_user
-- скрипт создаёт в базе данных таблицы, секвенторы, индексы

DROP INDEX IF EXISTS idx_sdet_created_at;
DROP INDEX IF EXISTS idx_sdet_pk;
DROP TABLE IF EXISTS qz.eve_sde_type_ids;

DROP INDEX IF EXISTS idx_eal_pk;
DROP TABLE IF EXISTS qz.esi_alliances;

DROP INDEX IF EXISTS idx_eco_pk;
DROP TABLE IF EXISTS qz.esi_corporations;

DROP INDEX IF EXISTS idx_ech_pk;
DROP TABLE IF EXISTS qz.esi_characters;

DROP INDEX IF EXISTS idx_pk_p;
DROP TABLE IF EXISTS qz.published;

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
