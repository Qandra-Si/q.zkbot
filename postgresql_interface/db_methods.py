# -*- encoding: utf-8 -*-
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
    def insert_into_zkillmails(self, zkm_data: typing.Dict[str, typing.Any]):
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
            " zkm_labels) "
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
            " %(lbs)s) "
            "ON CONFLICT ON CONSTRAINT pk_zkm DO NOTHING;",
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
             }
        )
