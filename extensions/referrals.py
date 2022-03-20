import discord
import datetime
import random
import string
from settings import SETTINGS
import utility as UTILITY
from tinydb import TinyDB, Query
from discord.ext import commands


class Referrals(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="referral", aliases=["ref", "code", "invite", "i"])
    @commands.check(UTILITY.verified_check)
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.guild_only()
    async def get_referral(self, ctx):
        """called to generate a referral code"""
        stored_user = UTILITY.database().get(Query().user_id == ctx.author.id)
        if stored_user:
            UTILITY.Logger.info(
                f"{ctx.author.name} ({ctx.author.id}) already has a referral code \"{stored_user.get('referral_code')}\""
            )
        else:
            stored_user = UTILITY.new_member_file(ctx.author)
            UTILITY.database().insert(stored_user)

        try:
            await ctx.author.send(
                f"{ctx.author.mention} Here is your referral code: `{stored_user.get('referral_code')}`\n"
                f"People you refer can send this code in <#{SETTINGS.channels.referral_channel}> to give you points."
            )
        except discord.Forbidden:
            await ctx.send(
                f"{ctx.author.mention} I am unable to DM you your referral code. Please check your settings.."
            )

        try:
            await ctx.message.delete()
        except:
            UTILITY.Logger.error(f"Failed to delete invite command message")

    @commands.command(name="referred", aliases=["refd"])
    @commands.check(UTILITY.verified_check)
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.guild_only()
    async def get_referred(self, ctx, referral_code: str):
        """called to get the user who referred the user"""
        await UTILITY.referral_submission(ctx.author, ctx.guild, referral_code)
        await ctx.message.delete()


def setup(bot):
    bot.add_cog(Referrals(bot))
