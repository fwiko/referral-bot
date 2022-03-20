import datetime
import random
import string

import discord
import utility as UTILITY
from discord.ext import commands
from settings import SETTINGS
from tinydb import Query, TinyDB


class Referrals(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        """triggered when a member joins the discord server"""
        if member.bot:
            return
        if UTILITY.database().contains(Query().user_id == member.id):
            UTILITY.database().update({"active": True}, Query().user_id == member.id)
        else:
            member_file = UTILITY.new_member_file(member)
            UTILITY.database().insert(member_file)

        UTILITY.Logger.info(
            f"{member.name} ({member.id}) joined the server and has been marked as Active"
        )

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        """triggered when a member leaves the discord server"""
        if member.bot:
            return
        if UTILITY.database().contains(Query().user_id == member.id):
            UTILITY.database().update({"active": False}, Query().user_id == member.id)

        UTILITY.Logger.info(
            f"{member.name} ({member.id}) left the server and has been marked as Inactive"
        )

    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        """triggered when a members attributes (whatever they may be) are updated"""
        if before.bot:
            return
        if before.roles == after.roles:
            return
        try:
            verified_role = discord.utils.get(
                after.guild.roles, id=SETTINGS.permissions.verified_role
            )
        except:
            UTILITY.Logger.error(
                f"Could not find verified role using ID ({SETTINGS.permissions.verified_role})"
            )
            return

        if not UTILITY.database().contains(Query().user_id == after.id):
            UTILITY.database().insert(UTILITY.new_member_file(after))

        if verified_role in after.roles and verified_role not in before.roles:
            UTILITY.database().update({"verified": True}, Query().user_id == after.id)
            UTILITY.Logger.info(f"{after.name} ({after.id}) is now Verified")

        elif verified_role not in after.roles and verified_role in before.roles:
            UTILITY.database().update({"verified": False}, Query().user_id == after.id)
            UTILITY.Logger.info(f"{after.name} ({after.id}) is no longer Verified")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """triggered when a message is sent in a discord channel"""
        if message.author.bot:
            return
        if (
            isinstance(message.channel, discord.channel.DMChannel)
            or message.channel.id != SETTINGS.channels.referral_channel
        ):
            return
        await UTILITY.referral_submission(
            message.author, message.guild, message.content
        )
        await message.delete()


def setup(bot):
    bot.add_cog(Referrals(bot))
