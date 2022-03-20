import discord
import datetime
import random
import string
from settings import SETTINGS
import utility as UTILITY
from tinydb import TinyDB, Query
from discord.ext import commands


class Statistics(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="leaderboard", aliases=["l", "table", "r", "ranks"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.guild_only()
    async def leaderboard(self, ctx, user: discord.Member = None):
        """will display a leaderboard embed when called"""
        if not user:
            user = ctx.author

        in_order = sorted(
            UTILITY.database().all(), key=lambda k: k["points"], reverse=True
        )

        leaderboard = "\n".join(
            [
                f"**{pos + 1}.** {user.get('name', user.get('user_id', 'Unknown'))} - "
                f"***{user.get('points', 0)} points***"
                for pos, user in enumerate(in_order[:10])
            ]
        )

        user_stat = UTILITY.database().search(Query().user_id == user.id)

        if user_stat:
            user_stat = user_stat[0]
            user_pos = in_order.index(user_stat) + 1
            leaderboard += (
                f"\n\n{user.mention}'s _current ranking_ is: **#{user_pos}** "
                f"with **{user_stat['points']} points**!"
            )
        else:
            leaderboard += f"\n\nNo recorded statistics for {user.mention}!"

        leaderboard_embed = discord.Embed(
            description=leaderboard,
            color=SETTINGS.embed.success_colour,
            timestamp=datetime.datetime.utcnow(),
        )

        leaderboard_embed.set_author(
            name="Referral Leaderboard",
            icon_url=self.bot.user.avatar_url,
        )

        await ctx.send(embed=leaderboard_embed)
        UTILITY.Logger.info(
            f"{ctx.author.name} ({ctx.author.id}) requested the referral leaderboard."
        )


def setup(bot):
    bot.add_cog(Statistics(bot))
