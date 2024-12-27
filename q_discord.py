import typing
import json
import http.client
import datetime
import discord
from discord.ext import tasks

import postgresql_interface as db
import q_settings
import q_killmail_formatter as fmk
import q_statistics_formatter as fms


def is_killmail_ready_on_zkillboard(killmail_id: int) -> typing.Tuple[bool, int, str]:
    #conn = http.client.HTTPSConnection("zkillboard.com")
    #conn.request("GET", f"/kill/{killmail_id}/")
    #res = conn.getresponse()
    #return res.status != 404, res.status, res.reason  # если всё что угодно, но не "404 Not Found", то публикуем
    # ---
    # https://discord.com/channels/849992399639281694/850216522266050570/1311753815749431449
    # Squizz попросил прекраить запрашивать статус готовности страницы
    return True, 200, "publising without checking zkillboard"


class MyClient(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__bot_id: int = 0

    async def setup_hook(self) -> None:
        # start the task to run in the background
        self.my_background_task.start()

    async def on_ready(self):
        self.__bot_id = self.user.id
        print(f'Logged in as {self.user} (ID: {self.__bot_id})')

    @tasks.loop(seconds=30)
    async def my_background_task(self):
        channel = self.get_channel(q_settings.q_discord_channel)
        if not channel:
            print(f'There are no access to channel {q_settings.q_discord_channel}')
            return

        # подключение к БД
        qzdb: db.QZKBotDatabase = db.QZKBotDatabase(debug=False)
        qzdb.connect(q_settings.g_database)
        qzm: db.QZKBotMethods = db.QZKBotMethods(qzdb)

        # изменение ранее опубликованных killmails (например при обновлении информации о стоимости корабля)
        need_refresh: typing.List[typing.Dict[str, typing.Any]] = qzm.get_need_to_refresh_killmails()
        for killmail_data in need_refresh:
            killmail_id: int = killmail_data['id']
            # поиск ранее опубликованного сообщения по killmail-коду в содержимом сообщения
            for msg in [_ async for _ in channel.history(limit=40, oldest_first=False)]:
                if self.__bot_id != msg.author.id:
                    continue
                if msg.content.find(f"https://zkillboard.com/kill/{killmail_id}/") == -1:
                    continue
                # ранее публиковавшееся сообщение найдено
                worth: typing.Optional[float] = killmail_data['zkb'].get('worth')
                points: typing.Optional[float] = killmail_data['zkb'].get('points')
                print(f'Refreshing killmail {killmail_id} (worth: {worth}, points: {points}) msg {msg.id} with ')
                # загружаем дополнительные данные из БД
                killmail_attackers: typing.Dict[str, typing.Any] = qzm.get_attackers_groups_by_killmail(killmail_id)
                # получаем форматированное сообщение
                fdm: fmk.FormattedDiscordKillmailMessage = fmk.FormattedDiscordKillmailMessage(
                    killmail_id,
                    killmail_data,
                    killmail_attackers,
                    q_settings.q_tracked_corporations,
                    q_settings.g_use_corporation_emblem_instead_alliance)
                if fdm.contents and fdm.embed:
                    await msg.edit(content=fdm.contents, embed=fdm.embed)
                del fdm
                break
            # Внимание! независимо от того, найдено ли сообщение в discord-е или нет - помечаем  его опубликованным
            # т.к. возможна ситуация, когда сообщение будет удалено вручную, и тогда алгоритм будет бесконечно
            # формировать список на редактирование
            qzm.mark_killmail_as_published(killmail_id)
            qzdb.commit()

        # публикация ещё неопубликованных killmails (могут быть без информации о стоимости корабля)
        non_published: typing.List[typing.Dict[str, typing.Any]] = qzm.get_non_published_killmails()
        for killmail_data in non_published:
            killmail_id: int = killmail_data['id']
            ready, status, reason = is_killmail_ready_on_zkillboard(killmail_id)
            if not ready:
                print(f'Can\'t publish killmail {killmail_id}: {status} {reason}')
                continue
            worth: typing.Optional[float] = killmail_data['zkb'].get('worth')
            points: typing.Optional[float] = killmail_data['zkb'].get('points')
            print(f'Publishing killmail {killmail_id} (worth: {worth}, points: {points})')
            # загружаем дополнительные данные из БД
            killmail_attackers: typing.Dict[str, typing.Any] = qzm.get_attackers_groups_by_killmail(killmail_id)
            # получаем форматированное сообщение
            fdm: fmk.FormattedDiscordKillmailMessage = fmk.FormattedDiscordKillmailMessage(
                killmail_id,
                killmail_data,
                killmail_attackers,
                q_settings.q_tracked_corporations,
                q_settings.g_use_corporation_emblem_instead_alliance)
            if fdm.contents and fdm.embed:
                await channel.send(content=fdm.contents, embed=fdm.embed)
            else:
                await channel.send(f"https://zkillboard.com/kill/{killmail_id}/")
            del fdm
            # отмечаем killmail опубликованным
            qzm.mark_killmail_as_published(killmail_id)
            qzdb.commit()

            # получение информации о текущем времени
            at_to: datetime.datetime = datetime.datetime.now(datetime.UTC)
            at_from: datetime.datetime = at_to - datetime.timedelta(days=7)
            # публикация статистических сведений
            stat = qzm.statistics_for_the_period(
                q_settings.q_tracked_corporations,
                at_from,
                at_to)
            # получаем форматированное сообщение
            fdm: fms.FormattedDiscordStatisticsMessage = fms.FormattedDiscordStatisticsMessage(
                at_from,
                at_to,
                stat)
            if fdm.paginator:
                e = fdm.embed
                for page in fdm.paginator.pages:
                    await channel.send(page, embed=e)
                    e = None
            del fdm

        # заканчиваем сеанс работы с БД
        del qzm
        qzdb.disconnect()
        del qzdb

    @my_background_task.before_loop
    async def before_my_task(self):
        await self.wait_until_ready()


client = MyClient(intents=discord.Intents.default())
client.run(q_settings.g_discord_token)
