import typing
import discord
from discord.ext import tasks

import postgresql_interface as db
import q_settings


class MyClient(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def setup_hook(self) -> None:
        # start the task to run in the background
        self.my_background_task.start()

    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')

    @tasks.loop(seconds=30)
    async def my_background_task(self):
        channel = self.get_channel(q_settings.q_discord_channel)
        if channel:
            # подключение к БД
            qzdb: db.QZKBotDatabase = db.QZKBotDatabase(debug=False)
            qzdb.connect(q_settings.g_database)
            qzm: db.QZKBotMethods = db.QZKBotMethods(qzdb)
            non_published: typing.List[int] = qzm.get_all_non_published_killmails()
            if non_published:
                for killmail_id in non_published:
                    await channel.send(f'https://zkillboard.com/kill/{killmail_id}/')
                    qzm.mark_killmail_as_published(killmail_id)
                qzdb.commit()
            del qzm
            qzdb.disconnect()
            del qzdb
        else:
            print(f'There are no access to channel {q_settings.q_discord_channel}')

    @my_background_task.before_loop
    async def before_my_task(self):
        await self.wait_until_ready()


client = MyClient(intents=discord.Intents.default())
client.run(q_settings.g_discord_token)