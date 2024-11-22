import discord
from discord.ext import commands

import q_settings


intents = discord.Intents.default()  # подключаем "Разрешения"
intents.message_content = True
help_command = commands.DefaultHelpCommand(no_category='Справка')
bot = commands.Bot(
    command_prefix='Q.',  # префикс
    intents=intents,  # интенты
    help_command=help_command)


class StatusCommands(commands.Cog, name="Проверка состояния"):
    @commands.command(pass_context=True, description='Проверка связи', help="Проверка связи")
    async def ping(self, ctx):
        await ctx.send(':ping_pong: pong')


@bot.event
async def on_ready():
    await bot.add_cog(StatusCommands())


def main():
    bot.run(q_settings.g_discord_token)


if __name__ == "__main__":
    main()
