# -*- encoding: utf-8 -*-
import datetime
import typing

from .db_interface import QZKBotDatabase
from .error import ZKBotDatabaseError


class QZKBotMethods:
    def __init__(self, db: QZKBotDatabase):
        """ constructor

        :param db: instance of QZKBotDatabase
        """
        if not isinstance(db, QZKBotDatabase):
            raise ZKBotDatabaseError("You should use QZKBotDatabase to configure methods")
        self.db: QZKBotDatabase = db

    def __del__(self):
        """ destructor
        """

    def insert_into_zkillmails_hash_only(self, km_data: typing.Dict[str, typing.Any], updated_at: datetime.datetime):
        self.db.execute(
            "INSERT INTO zkillmails("
            " zkm_id,"
            " zkm_hash,"
            " zkm_created_at,"
            " zkm_updated_at)"
            "VALUES("
            " %(id)s,"
            " %(h)s,"
            " CURRENT_TIMESTAMP AT TIME ZONE 'GMT',"
            " TIMESTAMP WITHOUT TIME ZONE %(at)s)"
            "ON CONFLICT ON CONSTRAINT pk_zkm DO NOTHING;",
            {'id': km_data['killmail_id'],
             'h': km_data['killmail_hash'],
             'at': updated_at,
             }
        )

    def insert_into_zkillmails(self, zkm_data: typing.Dict[str, typing.Any], updated_at: datetime.datetime):
        zkb: typing.Dict[str, typing.Any] = zkm_data['zkb']
        self.db.execute(
            "INSERT INTO zkillmails("
            " zkm_id,"
            " zkm_hash,"
            " zkm_location,"
            " zkm_fitted_value,"
            " zkm_dropped_value,"
            " zkm_destroyed_value,"
            " zkm_total_value,"
            " zkm_points,"
            " zkm_npc,"
            " zkm_solo,"
            " zkm_awox,"
            " zkm_labels,"
            " zkm_created_at,"
            " zkm_updated_at) "
            "VALUES("
            " %(id)s,"
            " %(h)s,"
            " %(l)s,"
            " %(fv)s,"
            " %(drv)s,"
            " %(dev)s,"
            " %(tv)s,"
            " %(p)s,"
            " %(n)s,"
            " %(s)s,"
            " %(a)s,"
            " %(lbs)s,"
            " CURRENT_TIMESTAMP AT TIME ZONE 'GMT',"
            " TIMESTAMP WITHOUT TIME ZONE %(at)s)"
            "ON CONFLICT ON CONSTRAINT pk_zkm DO UPDATE SET"
            " zkm_location=%(l)s,"
            " zkm_fitted_value=%(fv)s,"
            " zkm_dropped_value=%(drv)s,"
            " zkm_destroyed_value=%(dev)s,"
            " zkm_total_value=%(tv)s,"
            " zkm_points=%(p)s,"
            " zkm_npc=%(n)s,"
            " zkm_solo=%(s)s,"
            " zkm_awox=%(a)s,"
            " zkm_labels=%(lbs)s,"
            " zkm_updated_at=TIMESTAMP WITHOUT TIME ZONE %(at)s "
            "WHERE zkillmails.zkm_location IS NULL;",
            {'id': zkm_data['killmail_id'],
             'h': zkb['hash'],
             'l': zkb['locationID'],
             'fv': zkb.get('fittedValue', None),
             'drv': zkb.get('droppedValue', None),
             'dev': zkb.get('destroyedValue', None),
             'tv': zkb.get('totalValue', None),
             'p': zkb.get('points', None),
             'n': zkb.get('npc', None),
             's': zkb.get('solo', None),
             'a': zkb.get('awox', None),
             'lbs': zkb.get('labels', []),
             'at': updated_at,
             }
        )

    def get_unrelated_killmails(self) -> typing.List[typing.Tuple[int, str]]:
        rows = self.db.select_all_rows(
            "SELECT"
            " zkm_id,"
            " zkm_hash "
            "FROM zkillmails "
            "WHERE zkm_id NOT IN (SELECT km_id FROM killmails);"
        )
        if rows is None:
            return []
        return [(int(_[0]), _[1]) for _ in rows]

    def insert_into_killmails(self, killmail_id, data) -> None:
        row = self.db.select_one_row(
            "INSERT INTO killmails("
            " km_id,"
            " km_time,"
            " km_moon_id,"
            " km_solar_system_id,"
            " km_war_id) "
            "VALUES("
            " %(id)s,"
            " %(t)s,"
            " %(m)s,"
            " %(ss)s,"
            " %(w)s)"
            "ON CONFLICT ON CONSTRAINT pk_km DO NOTHING "
            "RETURNING km_id;",
            {'id': killmail_id,
             't': data['killmail_time'],
             'm': data.get('moon_id'),
             'ss': data['solar_system_id'],
             'w': data.get('war_id'),
             }
        )
        if row is not None:
            v = data['victim']
            self.db.execute(
                "INSERT INTO victims("
                " v_killmail_id,"
                " v_alliance_id,"
                " v_character_id,"
                " v_corporation_id,"
                " v_damage_taken,"
                " v_faction_id,"
                " v_position,"
                " v_ship_type_id)"
                "VALUES("
                " %(id)s,"
                " %(a)s,"
                " %(ch)s,"
                " %(co)s,"
                " %(d)s,"
                " %(f)s,"
                " %(p)s,"
                " %(t)s)"
                "ON CONFLICT ON CONSTRAINT pk_v DO NOTHING;",
                {'id': killmail_id,
                 'a': v.get('alliance_id'),
                 'ch': v.get('character_id'),
                 'co': v.get('corporation_id'),
                 'd': v['damage_taken'],
                 'f': v.get('faction_id'),
                 'p': None if 'position' not in v else [v['position']['x'], v['position']['y'], v['position']['z']],
                 't': v['ship_type_id'],
                 }
            )
            attackers = data['attackers']
            for a in attackers:
                self.db.execute(
                    "INSERT INTO attackers("
                    " a_killmail_id,"
                    " a_alliance_id,"
                    " a_character_id,"
                    " a_corporation_id,"
                    " a_damage_done,"
                    " a_faction_id,"
                    " a_final_blow,"
                    " a_security_status,"
                    " a_ship_type_id,"
                    " a_weapon_type_id)"
                    "VALUES("
                    " %(id)s,"
                    " %(a)s,"
                    " %(ch)s,"
                    " %(co)s,"
                    " %(d)s,"
                    " %(f)s,"
                    " %(fb)s,"
                    " %(cc)s,"
                    " %(t)s,"
                    " %(w)s);",
                    {'id': killmail_id,
                     'a': a.get('alliance_id'),
                     'ch': a.get('character_id'),
                     'co': a.get('corporation_id'),
                     'd': a['damage_done'],
                     'f': a.get('faction_id'),
                     'fb': a['final_blow'],
                     'cc': a['security_status'],
                     't': a.get('ship_type_id'),
                     'w': a.get('weapon_type_id'),
                     }
                )

    def mark_all_killmails_as_published_if_none(self) -> None:
        self.db.execute(
            "insert into published"
            " select km_id"
            " from killmails"
            " where 0 = (select count(1) from published);"
        )

    def get_all_non_published_killmails(self) -> typing.List[typing.Tuple[int, str]]:
        rows = self.db.select_all_rows(
            "SELECT km_id, zkm_hash "
            "FROM killmails, zkillmails "
            "WHERE"
            " km_id NOT IN (SELECT p_killmail_id FROM published) AND"
            " km_id=zkm_id"
            "ORDER BY km_time;"
        )
        if rows is None:
            return []
        return [(int(_[0]), _[1]) for _ in rows]

    def mark_killmail_as_published(self, killmail_id: int) -> None:
        self.db.execute(
            "INSERT INTO published(p_killmail_id)"
            "VALUES(%(id)s);",
            {'id': killmail_id}
        )
