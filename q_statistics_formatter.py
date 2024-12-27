import typing
import datetime
import discord
from discord.ext import commands


class FormattedDiscordStatisticsMessage:
    def __init__(self,
                 period_from: datetime.datetime,
                 period_to: datetime.datetime,
                 stat: typing.Dict[str, typing.Dict[str, int]]):
        self.paginator: typing.Optional[discord.ext.commands.Paginator] = None
        self.embed: typing.Optional[discord.Embed] = None
        self.__period_from: datetime.datetime = period_from
        self.__period_to: datetime.datetime = period_to
        self.__stat: typing.Dict[str, typing.Dict[str, int]] = stat
        self.format()

    def format(self) -> None:
        if not self.__stat: return

        self.paginator = discord.ext.commands.Paginator(prefix='', suffix='')
        self.paginator.add_line("**Статистика подъехала**")

        s = self.__stat.get('solo_loss')
        if s:
            cnt: int = s['cnt']
            destroyed: int = s['fitted']
            dropped: int = s['dropped']
            self.paginator.add_line(
                f"Мы слились в честном соло-pvp {cnt} раз, "
                f"потеряв {destroyed} ISK ({dropped} ISK досталось врагу).")

        s = self.__stat.get('gang_loss')
        if s:
            cnt: int = s['cnt']
            destroyed: int = s['fitted']
            dropped: int = s['dropped']
            self.paginator.add_line(
                f"Об ганги мы убились {cnt} раз, "
                f"потеряв {destroyed} ISK ({dropped} ISK досталось врагу).")

        s = self.__stat.get('solo_win')
        if s:
            cnt: int = s['cnt']
            destroyed: int = s['fitted']
            dropped: int = s['dropped']
            self.paginator.add_line(
                f"В честном соло-pvp мы победили {cnt} раз, "
                f"уничтожив {destroyed} ISK ({dropped} ISK дропнулось).")

        s = self.__stat.get('gang_win')
        if s:
            cnt: int = s['cnt']
            destroyed: int = s['fitted']
            dropped: int = s['dropped']
            self.paginator.add_line(
                f"Флотами было уничтожено {cnt} противников, "
                f"на сумму {destroyed} ISK ({dropped} ISK дропнулось).")
