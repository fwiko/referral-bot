import discord
import json
import datetime
from settings import SETTINGS
import utility as UTILITY
from discord.ext import commands
from tinydb import TinyDB, Query


INTENTS = discord.Intents.default()
INTENTS.members = True


def load_extensions() -> None:
    """Load all the extensions relative to what is specified in the settings file"""
    for extension in SETTINGS.bot.extensions:
        try:
            bot.load_extension(f"extensions.{extension}")
        except Exception as error:
            UTILITY.Logger.error(f"{extension} cannot be loaded. [{error}]")
        else:
            UTILITY.Logger.info(f"Loaded {extension}")


def admin_check(ctx) -> bool:
    """Check if the user executing the command has a role specified as an 'admin' role"""
    return not set(r.id for r in ctx.author.roles).isdisjoint(
        SETTINGS.permissions.admin_roles
    )


if __name__ == "__main__":
    bot = commands.AutoShardedBot(
        command_prefix=commands.when_mentioned_or(SETTINGS.bot.prefix),
        owner_id=264375928468013058,
        intents=INTENTS,
    )

    @bot.command(name="resetpoints")
    @commands.check(admin_check)
    async def reset_points(ctx):
        """Called on 'resetpoints' - resets all points to 0"""
        UTILITY.database().update({"points": 0}, Query().points > 0)
        await ctx.send(
            embed=discord.Embed(
                description=f":white_check_mark: Reset points for all users",
                colour=SETTINGS.embed.success_colour,
            )
        )
        UTILITY.Logger.info(
            f"{ctx.author.name} ({ctx.author.id}) has reset points for all users"
        )

    @bot.event
    async def on_ready():
        """Event triggered when the bot has finished starting up"""
        UTILITY.Logger.info(f"Logged in as {bot.user.name} ({bot.user.id})")
        await bot.change_presence(activity=discord.Game(name=SETTINGS.bot.status))

    load_extensions()
    bot.run(SETTINGS.bot.token)
