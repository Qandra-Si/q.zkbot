-- UTF-8 without BOM
-- скрипт выполняется от имени пользователя qz_user

ALTER TABLE qz.zkillmails ADD zkm_published BOOLEAN DEFAULT FALSE NOT NULL;
ALTER TABLE qz.zkillmails ADD zkm_need_refresh BOOLEAN DEFAULT FALSE NOT NULL;

UPDATE qz.zkillmails
SET zkm_published = TRUE
WHERE zkm_id IN (SELECT p_killmail_id FROM qz.published);

CREATE INDEX idx_zkm_published
    ON qz.zkillmails USING btree
    (zkm_published ASC NULLS LAST)
TABLESPACE pg_default;

CREATE INDEX idx_zkm_need_refresh
    ON qz.zkillmails USING btree
    (zkm_need_refresh ASC NULLS LAST)
TABLESPACE pg_default;

DROP INDEX IF EXISTS idx_pk_p;
DROP TABLE IF EXISTS qz.published;
