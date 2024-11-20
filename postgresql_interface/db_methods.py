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
            " zkm_updated_at) "
            "VALUES ("
            " %(id)s,"
            " %(h)s,"
            " CURRENT_TIMESTAMP AT TIME ZONE 'GMT',"
            " TIMESTAMP WITHOUT TIME ZONE %(at)s) "
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
            "VALUES ("
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
            " TIMESTAMP WITHOUT TIME ZONE %(at)s) "
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
