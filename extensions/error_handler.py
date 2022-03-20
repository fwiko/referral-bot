import discord
import traceback
import sys
import datetime
import math
from discord.ext import commands
from settings import SETTINGS
import utility as UTILITY

async def embed_generator(ctx, self, error_message):
    embed = discord.Embed(description=error_message, colour=SETTINGS.embed.error_colour)
    embed.set_author(name="Error Executing Command", icon_url=self.bot.user.avatar_url)
    await ctx.send(embed=embed)


class ErrorHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        """handles errors when thrown"""
        if hasattr(ctx.command, "on_error"):
            return

        error = getattr(error, "original", error)

        if isinstance(error, commands.CommandNotFound):
            return

        try:
            if isinstance(error, commands.NoPrivateMessage):
                await embed_generator(
                    ctx, self, "This command cannot be used in direct messages."
                )

            elif isinstance(error, commands.CommandOnCooldown):
                await embed_generator(
                    ctx,
                    self,
                    f"This command is on cooldown, please retry in {math.ceil(error.retry_after)}s.",
                )

            elif isinstance(error, commands.CheckFailure):
                await embed_generator(
                    ctx, self, "You do not have permission to use this command."
                )

            elif isinstance(error, commands.BotMissingPermissions):
                await embed_generator(
                    ctx,
                    self,
                    "I am missing the permissions required to execute this command",
                )

            elif isinstance(error, commands.MissingRequiredArgument):
                await embed_generator(
                    ctx, self, f"Missing argument `{error.param.name}`"
                )

            elif isinstance(error, commands.BadArgument):
                await embed_generator(
                    ctx, self, f"Invalid argument given ({error.argument})"
                )

            else:
                print(
                    "Ignoring exception in command {}:".format(ctx.command),
                    file=sys.stderr,
                )
                traceback.print_exception(
                    type(error), error, error.__traceback__, file=sys.stderr
                )

        except discord.Forbidden:
            pass


def setup(bot):
    bot.add_cog(ErrorHandler(bot))
