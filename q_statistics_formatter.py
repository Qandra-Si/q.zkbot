import typing
import datetime
import discord
from discord.ext import commands


class FormattedDiscordStatisticsMessage:
    def __init__(self,
                 period_from: datetime.datetime,
                 period_to: datetime.datetime,
                 stat: typing.Dict[str, typing.Dict[str, typing.Union[int, str, datetime.datetime]]],
                 use_russian_style_ship_name: bool,
                 use_corporation_instead_alliance: bool):
        self.paginator: typing.Optional[discord.ext.commands.Paginator] = None
        self.embed: typing.Optional[discord.Embed] = None
        self.__period_from: datetime.datetime = period_from
        self.__period_to: datetime.datetime = period_to
        self.__stat: typing.Dict[str, typing.Dict[str, typing.Union[int, str, datetime.datetime]]] = stat
        self.format(use_russian_style_ship_name, use_corporation_instead_alliance)

    def format(self,
               use_russian_style_ship_name: bool,
               use_corporation_instead_alliance: bool) -> None:
        self.paginator = discord.ext.commands.Paginator(prefix='', suffix='')
        self.paginator.add_line(":red_circle: **Статистика подъехала**")

        solo_win = self.__stat.get('solo_win')
        gang_win = self.__stat.get('gang_win')

        if solo_win:
            cnt: int = solo_win['cnt']
            destroyed: int = solo_win['destroyed']
            dropped: int = solo_win['dropped']
            total: int = destroyed + dropped
            additional: str = ""
            if not gang_win:
                additional = ", :zzz: в гангах никто не летал и ничего не убил"
            self.paginator.add_line(
                f":clap: В честном соло-pvp мы победили {self.cnt_to_enemies(cnt)}, "
                f"уничтожив `{self.isk_to_kkk(total)}` (`{self.isk_to_kkk(dropped)}` залутано)"
                f"{additional}.")

        if gang_win:
            cnt: int = gang_win['cnt']
            destroyed: int = gang_win['destroyed']
            dropped: int = gang_win['dropped']
            total: int = destroyed + dropped
            additional: str = ""
            if not solo_win:
                additional = ", :martial_arts_uniform: в соло никто ничего не убил"
            self.paginator.add_line(
                f":pirate_flag: Флотами {self.cnt_to_ships_wins(cnt, use_russian_style_ship_name)} "
                f"на сумму `{self.isk_to_kkk(total)}` (`{self.isk_to_kkk(dropped)}` залутано)"
                f"{additional}.")

        npc_loss = self.__stat.get('npc_loss')
        solo_loss = self.__stat.get('solo_loss')
        gang_loss = self.__stat.get('gang_loss')

        if solo_loss:
            cnt: int = solo_loss['cnt']
            destroyed: int = solo_loss['destroyed']
            dropped: int = solo_loss['dropped']
            total: int = destroyed + dropped
            additional: str = ""
            if not gang_loss:
                additional = ", :tada: об ганги не убились ни разу"
            self.paginator.add_line(
                f":people_wrestling: Слились в честном соло-pvp {self.cnt_to_times(cnt)}, "
                f"потеряв `{self.isk_to_kkk(total)}` (`{self.isk_to_kkk(dropped)}` досталось врагу)"
                f"{additional}.")

        if gang_loss:
            cnt: int = gang_loss['cnt']
            destroyed: int = gang_loss['destroyed']
            dropped: int = gang_loss['dropped']
            total: int = destroyed + dropped
            additional: str = ""
            if not solo_loss:
                additional = ", :no_good: потерь в соло-pvp не было"
            self.paginator.add_line(
                f":person_in_manual_wheelchair_facing_right: Об ганги мы убились {self.cnt_to_times(cnt)}, "
                f"потеряв `{self.isk_to_kkk(total)}` (`{self.isk_to_kkk(dropped)}` досталось врагу)"
                f"{additional}.")

        if npc_loss:
            cnt: int = npc_loss['cnt']
            destroyed: int = npc_loss['destroyed']
            dropped: int = npc_loss['dropped']
            total: int = destroyed + dropped
            self.paginator.add_line(
                f":crab: Об непись {self.cnt_to_ships_loss(cnt, use_russian_style_ship_name)} на "
                f"`{self.isk_to_kkk(total)}`.")

        if not solo_loss and not gang_loss and not solo_win and not gang_win:
            if npc_loss:
                self.paginator.add_line("Вылетов не было, скрабились.")
                self.paginator.add_line("— Все этим занимаются, но никто не признаётся.")
            else:
                self.paginator.add_line("— И сия пучина поглотила ея в один момент.")
                self.paginator.add_line("— В общем все умерли.")
        else:
            if not solo_loss and not gang_loss:
                self.paginator.add_line("Ни разу не слились.")
                self.paginator.add_line("— Пацаны, ваще ребята.")
                self.paginator.add_line("— Умеете, могёте.")

            if not solo_win and not gang_win:
                self.paginator.add_line("Соло побед не было, флотами не летали.")
                self.paginator.add_line("— Ленятся наверное, — подумал Штирлиц.")
                self.paginator.add_line("— Или очень не везло, — усмехнулся Мюллер.")

        largest_win = self.__stat.get('largest_win')
        largest_loss = self.__stat.get('largest_loss')

        if largest_win and largest_loss and largest_loss['total'] > largest_win['total']:
            largest = largest_loss
            is_largest_win: bool = False
        else:
            largest = largest_win if largest_win else largest_loss
            is_largest_win: bool = True if largest_win else False

        if largest:
            total: int = largest['total']
            solar_system: str = largest['solar_system']
            ship_type_id: int = largest['ship_type_id']
            ship_type_name: str = largest['ship_type_name']
            damage_taken: int = largest['damage_taken']
            killmail_id: int = largest['killmail_id']
            killmail_date: str = largest['time'].strftime('%Y-%m-%d')  # '2024-12-28'
            cargo: int = largest['cargo']
            cargo_additional: str = f" с `{self.isk_to_kkk(cargo)}` в карго" if cargo else ""
            pilot_name: str = largest['pilot_name']
            alliance_id: typing.Optional[int] = largest['alliance_id']
            corporation_id: typing.Optional[int] = largest['corporation_id']

            # выбор пояснения для footer

            footer_text: str = f"{pilot_name} ● {killmail_date}"
            # выбор иконки, которая появится в footer-е
            footer_icon: typing.Optional[str] = None
            if not is_largest_win and use_corporation_instead_alliance and corporation_id:
                footer_icon = f"https://images.evetech.net/corporations/{corporation_id}/logo?size=32"
            elif alliance_id:
                footer_icon = f"https://images.evetech.net/alliances/{alliance_id}/logo?size=32"
            elif corporation_id:
                footer_icon = f"https://images.evetech.net/corporations/{corporation_id}/logo?size=32"
            # выбор пояснения для embed-а
            if is_largest_win:
                description: str = \
                    f"Самая крупная победа на `{self.isk_to_kkk(total)}` в **{solar_system}** " + \
                    f"над **{ship_type_name}**{cargo_additional}, нанесено {damage_taken:,d} дамага."
            else:
                description: str = \
                    f"Самая крупная потеря **{ship_type_name}** на `{self.isk_to_kkk(total)}` " + \
                    f"в **{solar_system}**{cargo_additional}, откачано {damage_taken:,d} дамага."

            self.embed = discord.Embed(
                title=f"**{solar_system} | {ship_type_name}**",
                url=f"https://zkillboard.com/kill/{killmail_id}/",
                description=description,
                colour=0x2e6b4d if is_largest_win else 0xC85C70)
            self.embed.set_image(url=f"https://imageserver.eveonline.com/Type/{ship_type_id}_64.png")
            if footer_icon:
                self.embed.set_footer(text=footer_text, icon_url=footer_icon)
            else:
                self.embed.set_footer(text=footer_text)

    @staticmethod
    def cnt_to_ships_loss(cnt: int, use_russian_style_ship_name: bool) -> str:
        modulo: int = cnt % 100
        if 5 <= modulo <= 20:
            return f"потеряно {cnt} {'корабликов' if use_russian_style_ship_name else 'шипов'}"
        else:
            modulo = cnt % 10
            if (0 == modulo) or (5 <= modulo <= 9):
                return f"потеряно {cnt} {'корабликов' if use_russian_style_ship_name else 'шипов'}"
            elif 2 <= modulo <= 4:
                return f"потеряно {cnt} {'кораблика' if use_russian_style_ship_name else 'шипа'}"
            elif 1 == modulo:
                return f"потерян {cnt} {'кораблик' if use_russian_style_ship_name else 'шип'}"

    @staticmethod
    def cnt_to_ships_wins(cnt: int, use_russian_style_ship_name: bool) -> str:
        modulo: int = cnt % 100
        if 5 <= modulo <= 20:
            return f"настреляли {cnt} {'корабликов' if use_russian_style_ship_name else 'шипов'}"
        else:
            modulo = cnt % 10
            if (0 == modulo) or (5 <= modulo <= 9):
                return f"настреляли {cnt} {'корабликов' if use_russian_style_ship_name else 'шипов'}"
            elif 2 <= modulo <= 4:
                return f"убили {cnt} {'кораблика' if use_russian_style_ship_name else 'шипа'}"
            elif 1 == modulo:
                return f"убили {cnt} {'кораблик' if use_russian_style_ship_name else 'шип'}"

    @staticmethod
    def cnt_to_times(cnt: int) -> str:
        # Мы слились...
        # мы убились...
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
        # мы победили...
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
                return f"{cnt} противника"

    @staticmethod
    def isk_to_kkk(isk: int) -> str:
        if isk <= 950049:
            # 950к..10к
            res: str = f'{isk/1000:,.1f}к'
            if res[-3:] == '.0к':
                res = res[:-3] + 'к'
            return res
        elif isk <= 950049999:
            # 950кк..1.0кк
            res: str = f'{isk/1000000:,.1f}кк'
            if res[-4:] == '.0кк':
                res = res[:-4] + 'кк'
            return res
        elif isk <= 950049999999:
            # 950ккк..1.0ккк
            res: str = f'{isk/1000000000:,.1f}млрд'
            if res[-6:] == '.0млрд':
                res = res[:-6] + 'млрд'
            return res
        else:
            # 999.9трлн..1.0трлн
            res: str = f'{isk/1000000000000:,.1f}трлн'
            if res[-6:] == '.0трлн':
                res = res[:-6] + 'трлн'
            return res
