import typing
import json
import discord


class FormattedDiscordMessage:
    def __init__(self,
                 killmail_id: int,
                 killmail_data: typing.Dict[str, typing.Any],
                 attackers_data: typing.List[typing.Dict[str, typing.Any]],
                 solo_attacker: typing.Optional[typing.Dict[str, typing.Any]],
                 tracked_corporation_ids: typing.List[int]):
        self.contents: typing.Optional[str] = None
        self.embed: typing.Optional[discord.Embed] = None
        self.__killmail_id: int = killmail_id
        self.__killmail_data: typing.Dict[str, typing.Any] = killmail_data
        self.__attackers_data: typing.List[typing.Dict[str, typing.Any]] = attackers_data
        self.__solo_attacker: typing.Optional[typing.Dict[str, typing.Any]] = solo_attacker
        self.format(tracked_corporation_ids)

    def format(self, tracked_corporation_ids: typing.List[int]) -> None:
        attacker_corps: typing.List[typing.Dict[str, typing.Any]] = self.__attackers_data
        zkb: typing.Dict[str, typing.Any] = self.__killmail_data['zkb']
        solar_system: typing.Dict[str, typing.Any] = self.__killmail_data['solar_system']
        victim: typing.Dict[str, typing.Any] = self.__killmail_data['victim']
        final_blow: typing.Dict[str, typing.Any] = self.__killmail_data['final_blow']

        loss: bool = victim.get('corporation_id', 0) in tracked_corporation_ids
        attacker_pilots_qty: int = sum([_['corp']['pilots'] for _ in attacker_corps])
        solo: bool = attacker_pilots_qty == 1
        final_character_id: typing.Optional[int] = final_blow.get('id')
        final_ship_name: typing.Optional[int] = final_blow.get('ship')

        # Внимание!
        #  * solo выставляется, если атакующий пилот был один (непись не учитывается)
        #  * final_blow-пилот может быть неписью
        #  * solo_attacker-пилот не является неписью

        # см. про расположение элементов в embed-е тут: https://guide.disnake.dev/popular-topics/embeds
        if solo and self.__solo_attacker:
            solo_attacker_id: int = self.__solo_attacker.get('character_id')
            solo_attacker_name: str = self.__solo_attacker.get('character_name', str(solo_attacker_id))
            # Бой был выигран в соло пилотом Qandra Si
            attackers_txt: str = \
                f"Бой был выигран в соло пилотом" \
                f" [{solo_attacker_name}](https://zkillboard.com/character/{solo_attacker_id}/)"
            solo_ship_name: int = self.__solo_attacker.get('ship_name')
            if solo_ship_name:
                # Бой был выигран в соло пилотом Qandra Si на Tristan
                attackers_txt += f" на **{solo_ship_name}**"
        else:
            attackers_txt: str = "Окончательный удар нанёс"
            if final_character_id:
                # Окончательный удар нанёс Qandra Si
                final_character_name: str = final_blow.get('name', str(final_character_id))
                attackers_txt += f" [{final_character_name}](https://zkillboard.com/character/{final_character_id}/)"
            if final_ship_name:
                if solo or final_ship_name is not None:
                    # Окончательный удар нанёс Qandra Si на Tristan
                    attackers_txt += f" на **{final_ship_name}**"
                else:
                    # Окончательный удар нанёс Tristan
                    attackers_txt += f" **{final_ship_name}**"
        attackers_txt += "."

        if attacker_pilots_qty >= 2:
            attackers_txt += f"\nАтакующие: {attacker_pilots_qty}"
            attacker_corps_len: int = len(attacker_corps)
            if attacker_corps_len == 1:
                # Атакующие: (2) из Warriors tribe
                corp: typing.Dict[str, typing.Any] = attacker_corps[0]['corp']
                corporation_id: int = corp['id']
                corporation_name: str = corp.get('name', str(corporation_id))
                attackers_txt += f" из [{corporation_name}](https://zkillboard.com/corporation/{corporation_id}/)"
            elif attacker_corps_len >= 2:
                sorted_corps: typing.List[typing.Dict[str, typing.Any]] = [_['corp'] for _ in attacker_corps]
                sorted_corps.sort(key=lambda _: _['pilots'], reverse=True)
                if sorted_corps[0]['pilots'] > sorted_corps[1]['pilots']:
                    # Атакующие: (5), основная группа из Warriors tribe
                    corp: typing.Dict[str, typing.Any] = sorted_corps[0]
                    corporation_id: int = corp['id']
                    corporation_name: str = corp.get('name', str(corporation_id))
                    attackers_txt += \
                        ", основная группа из " \
                        f"[{corporation_name}](https://zkillboard.com/corporation/{corporation_id}/) " \
                        f"({corp['pilots']})"
            attackers_txt += "."

        victim_character_id: typing.Optional[int] = victim.get('character_id')
        victim_corporation_id: typing.Optional[int] = victim.get('corporation_id')
        victim_alliance_id: typing.Optional[int] = victim.get('alliance_id')
        if victim_character_id:
            character_name: str = victim.get('character_name', str(victim_character_id))
            victim_txt: str = f"[{character_name}](https://zkillboard.com/character/{victim_character_id}/)"
        else:
            victim_txt: str = ""
        if victim_corporation_id:
            corporation_name: str = victim.get('corporation_name', str(victim_corporation_id))
            victim_txt += f" ([{corporation_name}](https://zkillboard.com/corporation/{victim_corporation_id}/))"

        victim_ship_type_id: int = victim['ship_type_id']
        victim_ship_type_name: str = victim.get('ship_name', str(victim_ship_type_id))
        victim_txt += f" потерял свой **{victim_ship_type_name}**"

        solar_system_id: int = solar_system['id']
        solar_system_name: str = solar_system.get('name', str(solar_system_id))
        region_name: typing.Optional[str] = solar_system.get('region')
        victim_txt += f" в [{solar_system_name}](https://zkillboard.com/system/{solar_system_id}/)"
        if region_name:
            victim_txt += f" в **{region_name}**"

        worth: typing.Optional[float] = zkb.get('worth')
        if worth:
            if worth < 1000000.0:
                victim_txt += f" стоимостью **{worth/1000.0:.2f}k** ISK."
            elif worth < 1000000000.0:
                victim_txt += f" стоимостью **{worth/1000000.0:.2f}m** ISK."
            else:
                victim_txt += f" стоимостью **{worth/1000000000.0:,.2f}b** ISK."

        datetime_txt: str = self.__killmail_data['time']
        datetime_txt = f"{datetime_txt[:10]} {datetime_txt[11:16]}"
        footer_txt: str = datetime_txt
        if zkb.get('points', 0):
            footer_txt += f" ● {zkb['points']} points"
        if zkb.get('solo', False):
            footer_txt += " ● solo"
        if zkb.get('npc', False):
            footer_txt += " ● npc"
        if zkb.get('awox', False):
            footer_txt += " ● awox"

        # await channel.send(contents=text, embed=embed)
        self.contents = \
            f"[**{solar_system_name} | {victim_ship_type_name}**]" \
            f"(https://zkillboard.com/kill/{self.__killmail_id}/)"
        self.embed = discord.Embed(
            description=victim_txt + "\n" + attackers_txt,
            colour=0xC85C70 if loss else 0x2e6b4d)
        self.embed.set_thumbnail(
            url=f"https://images.evetech.net/types/{victim_ship_type_id}/render?size=64")
        if victim_alliance_id:
            self.embed.set_footer(
                text=footer_txt,
                icon_url=f"https://images.evetech.net/alliances/{victim_alliance_id}/logo?size=32")
        else:
            self.embed.set_footer(text=footer_txt)
