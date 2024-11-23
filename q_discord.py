import discord
from discord.ext import commands
from discord.ext import tasks

import q_settings


intents = discord.Intents.default()  # подключаем "Разрешения"
intents.message_content = True
help_command = commands.DefaultHelpCommand(no_category='Справка')
bot = commands.Bot(
    command_prefix='Q.',  # префикс
    intents=intents,  # интенты
    help_command=help_command)
client = discord.Client(intents=discord.Intents.all())


class StatusCommands(commands.Cog, name="Проверка состояния"):
    @commands.command(pass_context=True, description='Проверка связи', help="Проверка связи")
    async def ping(self, ctx):
        await ctx.send(':ping_pong: pong')


@tasks.loop(seconds=30)
async def check_non_published_task():
    await client.wait_until_ready()
    channel = client.get_channel(q_settings.q_discord_channel)
    await channel.send('https://zkillboard.com/kill/117716344/')


@bot.event
async def on_ready():
    print(f'Logged in as \'{client.user.name}\' with id {client.user.id}')
    await bot.add_cog(StatusCommands())
    check_non_published_task.start()


def main():
    bot.run(q_settings.g_discord_token)


if __name__ == "__main__":
    main()
