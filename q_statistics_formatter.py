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
                f"Мы слились в честном соло-pvp {self.cnt_to_times(cnt)}, "
                f"потеряв `{self.isk_to_kkk(destroyed)}` (`{self.isk_to_kkk(dropped)}` досталось врагу).")

        s = self.__stat.get('gang_loss')
        if s:
            cnt: int = s['cnt']
            destroyed: int = s['fitted']
            dropped: int = s['dropped']
            self.paginator.add_line(
                f"Об ганги мы убились {self.cnt_to_times(cnt)}, "
                f"потеряв `{self.isk_to_kkk(destroyed)}` (`{self.isk_to_kkk(dropped)}` досталось врагу).")

        s = self.__stat.get('solo_win')
        if s:
            cnt: int = s['cnt']
            destroyed: int = s['fitted']
            dropped: int = s['dropped']
            self.paginator.add_line(
                f"В честном соло-pvp мы победили {self.cnt_to_enemies(cnt)}, "
                f"уничтожив `{self.isk_to_kkk(destroyed)}` (`{self.isk_to_kkk(dropped)}` дропнулось).")

        s = self.__stat.get('gang_win')
        if s:
            cnt: int = s['cnt']
            destroyed: int = s['fitted']
            dropped: int = s['dropped']
            self.paginator.add_line(
                f"Флотами было уничтожено {self.cnt_to_enemies(cnt)}, "
                f"на сумму `{self.isk_to_kkk(destroyed)}` (`{self.isk_to_kkk(dropped)}` дропнулось).")

    @staticmethod
    def cnt_to_times(cnt: int) -> str:
        modulo: int = cnt % 100
        if 5 <= modulo <= 20:
            return f"{cnt} раз"
        else:
            modulo = cnt % 10
            if 5 <= modulo <= 9:
                return f"{cnt} раз"
            elif 2 <= modulo <= 4:
                return f"{cnt} раза"
            elif 0 <= modulo <= 1:
                return f"{cnt} раз"

    @staticmethod
    def cnt_to_enemies(cnt: int) -> str:
        modulo: int = cnt % 100
        if 5 <= modulo <= 20:
            return f"{cnt} противников"
        else:
            modulo = cnt % 10
            if (0 == modulo) or (5 <= modulo <= 9):
                return f"{cnt} противников"
            elif 2 <= modulo <= 4:
                return f"{cnt} противника"
            elif modulo == 1:
                return f"{cnt} противник"

    @staticmethod
    def isk_to_kkk(isk: int) -> str:
        if isk <= 950049:
            # 950к..10к
            res: str = f'{isk/1000:,.1f}к'
            if res[-3:] == '.0к':
                res = res[-3:] + 'к'
            return res
        elif isk <= 950049999:
            # 950кк..1.0кк
            res: str = f'{isk/1000000:,.1f}кк'
            if res[-4:] == '.0кк':
                res = res[-4:] + 'кк'
            return res
        elif isk <= 950049999999:
            # 950ккк..1.0ккк
            res: str = f'{isk/1000000000:,.1f}млрд'
            if res[-6:] == '.0млрд':
                res = res[-6:] + 'млрд'
            return res
        else:
            # 999.9трлн..1.0трлн
            res: str = f'{isk/1000000000000:,.1f}трлн'
            if res[-6:] == '.0трлн':
                res = res[-6:] + 'трлн'
            return res
