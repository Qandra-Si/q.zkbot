-- UTF-8 without BOM
-- скрипт выполняется от имени пользователя qz_user

ALTER TABLE qz.zkillmails ADD zkm_published BOOLEAN DEFAULT FALSE NOT NULL;
ALTER TABLE qz.zkillmails ADD zkm_need_refresh BOOLEAN DEFAULT FALSE NOT NULL;

UPDATE qz.zkillmails
SET zkm_published = TRUE
WHERE zkm_id IN (SELECT p_killmail_id FROM qz.published);

DROP INDEX IF EXISTS idx_pk_p;
DROP TABLE IF EXISTS qz.published;
