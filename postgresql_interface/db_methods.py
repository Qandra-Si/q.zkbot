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

    def get_all_non_published_killmails(self) -> typing.List[typing.Dict[str, typing.Any]]:
        rows = self.db.select_all_rows(
            "SELECT"
            " km_id,"
            " zkm_hash,"
            " zkm_total_value,"
            " zkm_points,"
            " zkm_npc,"
            " zkm_solo,"
            " zkm_awox "
            "FROM killmails, zkillmails "
            "WHERE"
            " km_id NOT IN (SELECT p_killmail_id FROM published) AND"
            " km_id=zkm_id "
            "ORDER BY km_time;"
        )
        if rows is None:
            return []
        return [{
            'id': int(_[0]),  # not null
            'hash': _[1],  # not null
            'worth': _[2],
            'points': _[3],
            'npc': _[4],
            'solo': _[5],
            'awox': _[6]
        } for _ in rows]

    def mark_killmail_as_published(self, killmail_id: int) -> None:
        self.db.execute(
            "INSERT INTO published(p_killmail_id)"
            "VALUES(%(id)s);",
            {'id': killmail_id}
        )

    # -------------------------------------------------------------------------
    # [common]
    # -------------------------------------------------------------------------

    def get_absent_ids(self, ids: typing.Set[int], table: str, field: str) -> typing.List[int]:
        """
        :param ids: list of unique identities to compare with ids, stored in the database
        :param table: table name
        :param field: field name
        :return: list of ids which are not in the database
        """
        aids = self.db.select_all_rows(
            "SELECT id FROM UNNEST(%s) AS a(id) "
            "WHERE id NOT IN (SELECT {f} FROM {t});".format(t=table, f=field),
            list(ids)
        )
        return [int(_[0]) for _ in aids] if aids is not None else []

    # -------------------------------------------------------------------------
    # characters/{character_id}/
    # /universe/names/
    # -------------------------------------------------------------------------

    def get_absent_character_ids(self, ids: typing.Set[int]) -> typing.List[int]:
        absent: typing.List[int] = self.get_absent_ids(ids, "esi_characters", "ech_character_id")
        return absent

    def insert_or_update_character(self, id: int, data, updated_at):
        """ inserts character data into database

        :param id: unique character id
        :param data: character data
        :param updated_at: :class:`datetime.datetime`
        """
        # { "alliance_id": 99010134,
        #   "ancestry_id": 4,
        #   "birthday": "2009-08-19T19:23:00Z",
        #   "bloodline_id": 6,
        #   "corporation_id": 98553333,
        #   "description": "...",
        #   "gender": "male",
        #   "name": "olegez",
        #   "race_id": 4,
        #   "security_status": 3.960657443
        #  }
        #  { "category": "character",
        #    "id": 2116746261,
        #    "name": "Kekuit Void"
        #  }
        self.db.execute(
            "INSERT INTO esi_characters("
            " ech_character_id,"
            " ech_name,"
            " ech_created_at,"
            " ech_updated_at) "
            "VALUES("
            " %(id)s,"
            " %(nm)s,"
            " CURRENT_TIMESTAMP AT TIME ZONE 'GMT',"
            " TIMESTAMP WITHOUT TIME ZONE %(at)s) "
            "ON CONFLICT ON CONSTRAINT pk_ech DO UPDATE SET"
            " ech_name=%(nm)s,"
            " ech_updated_at=TIMESTAMP WITHOUT TIME ZONE %(at)s;",
            {'id': id,
             'nm': data['name'],
             'at': updated_at,
             }
        )

    # -------------------------------------------------------------------------
    # corporations/{corporation_id}/
    # /universe/names/
    # -------------------------------------------------------------------------

    def get_absent_corporation_ids(self, ids: typing.Set[int]) -> typing.List[int]:
        absent: typing.List[int] = self.get_absent_ids(ids, "esi_corporations", "eco_corporation_id")
        return absent

    def insert_or_update_corporation(self, id: int, data, updated_at):
        """ inserts corporation data into database

        :param id: unique corporation id
        :param data: corporation data
        :param updated_at: :class:`datetime.datetime`
        """
        # { "alliance_id": 99007203,
        #   "ceo_id": 93531267,
        #   "creator_id": 93362315,
        #   "date_founded": "2019-09-27T20:27:54Z",
        #   "description": "...",
        #   "home_station_id": 60003064,
        #   "member_count": 215,
        #   "name": "R Initiative 4",
        #   "shares": 1000,
        #   "tax_rate": 0.1,
        #   "ticker": "RI4",
        #   "url": "",
        #   "war_eligible": true
        #  }
        #  { "category": "corporation",
        #    "id": 787611831,
        #    "name": "Warriors tribe"
        #  }
        self.db.execute(
            "INSERT INTO esi_corporations("
            " eco_corporation_id,"
            " eco_name,"
            " eco_created_at,"
            " eco_updated_at) "
            "VALUES ("
            " %(id)s,"
            " %(nm)s,"
            " CURRENT_TIMESTAMP AT TIME ZONE 'GMT',"
            " TIMESTAMP WITHOUT TIME ZONE %(at)s) "
            "ON CONFLICT ON CONSTRAINT pk_eco DO UPDATE SET"
            " eco_name=%(nm)s,"
            " eco_updated_at=TIMESTAMP WITHOUT TIME ZONE %(at)s;",
            {'id': id,
             'nm': data['name'],
             'at': updated_at,
             }
        )

    # -------------------------------------------------------------------------
    # /alliances/{alliance_id}/
    # /universe/names/
    # -------------------------------------------------------------------------

    def get_absent_alliance_ids(self, ids: typing.Set[int]) -> typing.List[int]:
        absent: typing.List[int] = self.get_absent_ids(ids, "esi_alliances", "eal_alliance_id")
        return absent

    def insert_or_update_alliance(self, id: int, data, updated_at):
        """ inserts alliance data into database

        :param id: unique alliance id
        :param data: alliance data
        :param updated_at: :class:`datetime.datetime`
        """
        # { "creator_corporation_id": 98487467,
        #   "creator_id": 91251672,
        #   "date_founded": "2023-12-30T21:23:18Z",
        #   "executor_corporation_id": 98549274,
        #   "name": "Ragequit Cancel Sub",
        #   "ticker": "DEBUG"
        #  }
        #  { "category": "alliance",
        #    "id": 99012896,
        #    "name": "Ragequit Cancel Sub"
        #  }
        self.db.execute(
            "INSERT INTO esi_alliances("
            " eal_alliance_id,"
            " eal_name,"
            " eal_created_at,"
            " eal_updated_at) "
            "VALUES ("
            " %(id)s,"
            " %(nm)s,"
            " CURRENT_TIMESTAMP AT TIME ZONE 'GMT',"
            " TIMESTAMP WITHOUT TIME ZONE %(at)s) "
            "ON CONFLICT ON CONSTRAINT pk_eal DO UPDATE SET"
            " eal_name=%(nm)s,"
            " eal_updated_at=TIMESTAMP WITHOUT TIME ZONE %(at)s;",
            {'id': id,
             'nm': data['name'],
             'at': updated_at,
             }
        )

    # -------------------------------------------------------------------------
    # /universe/types/
    # /universe/types/{type_id}/
    # /universe/names/
    # -------------------------------------------------------------------------

    def get_absent_type_ids(self, ids: typing.Set[int]) -> typing.List[int]:
        absent: typing.List[int] = self.get_absent_ids(ids, "eve_sde_type_ids", "sdet_type_id")
        return absent

    def insert_or_update_type_id(self, type_id: int, data, updated_at):
        """ inserts type_id' data into database

        :param data: item type market history data
        """
        # { "capacity": 0,
        #   "description": "Contains stylish 'Imperial Loyalist' pants for both men and women to celebrate Foundation Day YC123.",
        #   "group_id": 1194,
        #   "icon_id": 24297,
        #   "mass": 0,
        #   "name": "Amarr Foundation Day Pants Crate",
        #   "packaged_volume": 0.1,
        #   "portion_size": 1,
        #   "published": true,
        #   "radius": 1,
        #   "type_id": 59978,
        #   "volume": 0.1
        # }
        # { "category": "inventory_type",
        #   "id": 47270,
        #   "name": "Vedmak"
        # }
        self.db.execute(
            "INSERT INTO eve_sde_type_ids("
            " sdet_type_id,"
            " sdet_type_name,"
            " sdet_published,"
            " sdet_icon_id,"
            " sdet_created_at) "
            "VALUES ("
            " %(t)s,"
            " %(nm)s,"
            " %(p)s,"
            " %(i)s,"
            " TIMESTAMP WITHOUT TIME ZONE %(at)s) "
            "ON CONFLICT ON CONSTRAINT pk_sdet DO UPDATE SET"
            " sdet_type_name=%(nm)s,"
            " sdet_published=%(p)s,"
            " sdet_icon_id=%(i)s;",
            {'t': type_id,
             'nm': data['name'],
             'p': data.get('published', None),
             'i': data.get('icon_id', None),
             'at': updated_at
             }
        )

    # -------------------------------------------------------------------------
    # /universe/regions/{region_id}/
    # -------------------------------------------------------------------------

    def get_absent_region_ids(self, ids: typing.Set[int]) -> typing.List[int]:
        absent: typing.List[int] = self.get_absent_ids(ids, "esi_regions", "esr_region_id")
        return absent

    def insert_or_update_region(self, id: int, data, updated_at):
        """ inserts region data into database

        :param id: unique region id
        :param data: region data
        :param updated_at: :class:`datetime.datetime`
        """
        # { "constellations": [
        #     20000448,
        #     20000449,
        #     20000450,
        #     20000451,
        #     20000452
        #   ],
        #   "description": "...",
        #   "name": "The Bleak Lands",
        #   "region_id": 10000038
        # }
        # { "category": "region",
        #   "id": 10000038,
        #   "name": "The Bleak Lands"
        # }
        self.db.execute(
            "INSERT INTO esi_regions("
            " esr_region_id,"
            " esr_name,"
            " esr_created_at,"
            " esr_updated_at) "
            "VALUES ("
            " %(id)s,"
            " %(nm)s,"
            " CURRENT_TIMESTAMP AT TIME ZONE 'GMT',"
            " TIMESTAMP WITHOUT TIME ZONE %(at)s) "
            "ON CONFLICT ON CONSTRAINT pk_esr DO UPDATE SET"
            " esr_name=%(nm)s,"
            " esr_updated_at=TIMESTAMP WITHOUT TIME ZONE %(at)s;",
            {'id': id,
             'nm': data['name'],
             'at': updated_at,
             }
        )

    # -------------------------------------------------------------------------
    # /universe/constellations/{constellation_id}/
    # -------------------------------------------------------------------------

    def get_absent_constellation_ids(self, ids: typing.Set[int]) -> typing.List[int]:
        absent: typing.List[int] = self.get_absent_ids(ids, "esi_constellations", "esc_constellation_id")
        return absent

    def insert_or_update_constellation(self, id: int, data, updated_at):
        """ inserts constellation data into database

        :param id: unique constellation id
        :param data: constellation data
        :param updated_at: :class:`datetime.datetime`
        """
        # { "constellation_id": 20000448,
        #   "name": "Sasen",
        #   "position": {
        #     "x": -144877496800077570,
        #     "y": 57858086119709010,
        #     "z": -48618946556037704
        #   },
        #   "region_id": 10000038,
        #   "systems": [
        #     30003063,
        #     30003064,
        #     30003065,
        #     30003066,
        #     30003067,
        #     30003068,
        #     30003069
        #   ]
        # }
        # { "category": "constellation",
        #   "id": 20000448,
        #   "name": "Sasen"
        # }
        self.db.execute(
            "INSERT INTO esi_constellations("
            " esc_constellation_id,"
            " esc_name,"
            " esc_position,"
            " esc_region_id,"
            " esc_created_at,"
            " esc_updated_at) "
            "VALUES ("
            " %(id)s,"
            " %(nm)s,"
            " %(p)s,"
            " %(r)s,"
            " CURRENT_TIMESTAMP AT TIME ZONE 'GMT',"
            " TIMESTAMP WITHOUT TIME ZONE %(at)s) "
            "ON CONFLICT ON CONSTRAINT pk_esc DO UPDATE SET"
            " esc_name=%(nm)s,"
            " esc_position=%(p)s,"
            " esc_region_id=%(r)s,"
            " esc_updated_at=TIMESTAMP WITHOUT TIME ZONE %(at)s;",
            {'id': id,
             'nm': data['name'],
             'p': [data['position']['x'], data['position']['y'], data['position']['z']],
             'r': data['region_id'],
             'at': updated_at,
             }
        )

    # -------------------------------------------------------------------------
    # /universe/systems/{system_id}/
    # -------------------------------------------------------------------------

    def get_absent_system_ids(self, ids: typing.Set[int]) -> typing.List[int]:
        absent: typing.List[int] = self.get_absent_ids(ids, "esi_systems", "ess_system_id")
        return absent

    def insert_or_update_system(self, id: int, data, updated_at):
        """ inserts system data into database

        :param id: unique system id
        :param data: system data
        :param updated_at: :class:`datetime.datetime`
        """
        # { "constellation_id": 20000448,
        #   "name": "Kourmonen",
        #   "planets": [
        #     {
        #       "moons": [
        #         40194991
        #       ],
        #       "planet_id": 40194990
        #     },
        #     {
        #       "moons": [
        #         40194993,40194994,40194995,40194996,40194997,40194998,40194999,40195000,
        #         40195001,40195002,40195003
        #       ],
        #       "planet_id": 40194992
        #     },
        #     {
        #       "moons": [
        #         40195005,40195006,40195007,40195008,40195009,40195010,40195011,40195012,
        #         40195013,40195014,40195015,40195016,40195017,40195018,40195019,40195020,
        #         40195021,40195022,40195023
        #       ],
        #       "planet_id": 40195004
        #     },
        #     {
        #       "moons": [
        #         40195025,40195026,40195027,40195028,40195029,40195030,40195031,40195032,
        #         40195033,40195034,40195035,40195036,40195037,40195038,40195039,40195040,
        #         40195041,40195042,40195043,40195044,40195045,40195046,40195047
        #       ],
        #       "planet_id": 40195024
        #     },
        #     {
        #       "asteroid_belts": [
        #         40195049,40195052,40195053,40195054,40195067,40195071,40195073,40195077,
        #         40195078,40195080,40195082
        #       ],
        #       "moons": [
        #         40195050,40195051,40195055,40195056,40195057,40195058,40195059,40195060,
        #         40195061,40195062,40195063,40195064,40195065,40195066,40195068,40195069,
        #         40195070,40195072,40195074,40195075,40195076,40195079,40195081
        #       ],
        #       "planet_id": 40195048
        #     }
        #   ],
        #   "position": {
        #     "x": -137144866634971220,
        #     "y": 42128767386892000,
        #     "z": -32854011328645590
        #   },
        #   "security_class": "B2",
        #   "security_status": 0.3634801506996155,
        #   "star_id": 40194989,
        #   "stargates": [
        #     50001856,50001857,50001858,50014062
        #   ],
        #   "stations": [
        #     60002200,60002206,60014563,60014566,60014569
        #   ],
        #   "system_id": 30003068
        # }
        # { "category": "solar_system",
        #   "id": 30003068,
        #   "name": "Kourmonen"
        # }
        self.db.execute(
            "INSERT INTO esi_systems("
            " ess_system_id,"
            " ess_name,"
            " ess_position,"
            " ess_constellation_id,"
            " ess_created_at,"
            " ess_updated_at) "
            "VALUES ("
            " %(id)s,"
            " %(nm)s,"
            " %(p)s,"
            " %(c)s,"
            " CURRENT_TIMESTAMP AT TIME ZONE 'GMT',"
            " TIMESTAMP WITHOUT TIME ZONE %(at)s) "
            "ON CONFLICT ON CONSTRAINT pk_ess DO UPDATE SET"
            " ess_name=%(nm)s,"
            " ess_position=%(p)s,"
            " ess_constellation_id=%(c)s,"
            " ess_updated_at=TIMESTAMP WITHOUT TIME ZONE %(at)s;",
            {'id': id,
             'nm': data['name'],
             'p': [data['position']['x'], data['position']['y'], data['position']['z']],
             'c': data['constellation_id'],
             'at': updated_at,
             }
        )
