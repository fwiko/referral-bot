import datetime
import random
import string

import discord
from tinydb import Query, TinyDB

from settings import SETTINGS


def database():
    """return referral data tinydb object"""
    return TinyDB("data/referral_data.json")


def verified_check(ctx) -> bool:
    """function used as a check to make sure a member is verified"""
    return SETTINGS.permissions.verified_role in [r.id for r in ctx.author.roles]


def generate_code() -> str:
    """return a random 16 character long string"""
    blacklist = Blacklist("blacklist")
    # continue while the generated code is not unique
    while True:
        # generate a random SETTINGS.referrals.code_length character code
        characters = string.ascii_uppercase + string.digits
        code = "".join(
            [random.choice(characters) for _ in range(SETTINGS.referrals.code_length)]
        )
        # check whether or not the generated code is unique
        if not blacklist.check_code(code):
            blacklist.add_code(code)
            return code


def new_member_file(member: discord.Member) -> dict:
    """create a new member file for the given member"""
    referral_code = generate_code()
    UTILITY.Logger.info(
        f'{member.name} ({member.id}) generated a referral code "{referral_code}"'
    )

    # return a member file dictionary to be stored in the database
    return {
        "name": member.name,
        "user_id": member.id,
        "referral_code": referral_code,
        "points": 0,
        "referrals": [],
        "referred_by": None,
        "verified": SETTINGS.permissions.verified_role in [r.id for r in member.roles],
        "active": True,
    }


async def check_points(guild: discord.Guild, referee: dict) -> None:
    """Check a users points, giving them the reward role if they have met the threshold"""

    # Check if the users points meet what is required to get the reward role
    if not referee.get("points") >= SETTINGS.referrals.reward_points:
        return

    # Attempt to fetch the member object of the owner of the referral code
    try:
        referee_member = guild.get_member(referee.get("user_id"))
    except Exception as e:
        UTILITY.Logger.error(f"Cannot find user with ID ({referee.get('user_id')})")
        return

    # Check if the user already has the reward role
    if SETTINGS.permissions.reward_role in [r.id for r in referee_member.roles]:
        UTILITY.Logger.info(
            f"{referee.get('name')} ({referee.get('user_id')}) already has the reward role"
        )
        return

    # Atteempt to get the role object relative to the reward_role ID
    try:
        reward_role = discord.utils.get(
            guild.roles, id=SETTINGS.permissions.reward_role
        )
    except:
        UTILITY.Logger.error(
            f"Unable to fetch reward role with ID {SETTINGS.permissions.reward_role}"
        )
        return

    # Add the reward role to the user
    await referee_member.add_roles(reward_role)

    UTILITY.Logger.info(
        f"{referee_member.name} ({referee_member.id}) has been given the reward role"
    )


class Logger:
    @staticmethod
    def get_time():
        """returns the current timestamp"""
        return datetime.datetime.now()

    def __log(self, prefix: str, message: str):
        """prints a final log"""
        print(
            f"{self.get_time().strftime('%d-%m-%Y %H:%M:%S')} - {self.__class__.__name__}:{prefix} - {message}"
        )

    def error(self, message: str):
        """logs an error log"""
        self.__log("ERROR", message)

    def info(self, message: str):
        """logs an info log"""
        self.__log("INFO", message)

    def debug(self, message: str):
        """logs a debug log"""
        self.__log("DEBUG", message)


class Blacklist:
    def __init__(self, filename: str):
        self.__dbfile = filename

        if not TinyDB(f"data/{self.__dbfile}.json").contains(Query().id == 1):
            TinyDB(f"data/{self.__dbfile}.json").insert(
                {"id": 1, "users": [], "codes": []}
            )
        else:
            db = TinyDB(f"data/{self.__dbfile}.json").get(Query().id == 1)

    def add_user(self, user_id: int):
        new_users = TinyDB(f"data/{self.__dbfile}.json").get(Query().id == 1).get(
            "users"
        ) + [user_id]
        TinyDB(f"data/{self.__dbfile}.json").update(
            {"users": new_users}, Query().id == 1
        )

    def add_code(self, code: str):
        new_codes = TinyDB(f"data/{self.__dbfile}.json").get(Query().id == 1).get(
            "codes"
        ) + [code]
        TinyDB(f"data/{self.__dbfile}.json").update(
            {"codes": new_codes}, Query().id == 1
        )

    def check_code(self, code: str):
        return code in TinyDB(f"data/{self.__dbfile}.json").get(Query().id == 1).get(
            "codes"
        )

    def check_user(self, user_id: int):
        return user_id in TinyDB(f"data/{self.__dbfile}.json").get(Query().id == 1).get(
            "users"
        )


async def referral_submission(
    author: discord.Member, guild: discord.Guild, referral_code: str
) -> None:
    """called when someone is referred"""
    blacklist = Blacklist("blacklist")

    # if the referral code isn't of the correct length
    if not len(referral_code) == SETTINGS.referrals.code_length:
        return

    # if the user has already been referred
    if database().search(Query().referrals.any([author.id])) != []:
        try:
            await author.send("You have already been referred.")
        except discord.Forbidden:
            pass
        UTILITY.Logger.info(f"{author.name} ({author.id}) has already been referred")
        return

    # if the user is located in the blacklist
    if blacklist.check_user(author.id):
        try:
            await author.send(
                "You were in the server before the launch of this bot and are unable to be referred."
            )
        except discord.Forbidden:
            pass
        UTILITY.Logger.info(f"{author.name} ({author.id}) was in the blacklist")
        return

    # if the user is trying to refer themselves or the
    referee = database().get(Query().referral_code == referral_code)

    # if the referral code is invalid
    if not referee:
        try:
            await author.send(f"`{referral_code}` is not a valid referral code.")
        except discord.Forbidden:
            pass
        UTILITY.Logger.info(f"{author.name} ({author.id}) submitted an invalid referral code")
        return

    # if the user is trying to refer themselves
    if referee.get("user_id") == author.id:
        try:
            await author.send(f"`{referral_code}` you cannot refer yourself.")
        except discord.Forbidden:
            pass
        UTILITY.Logger.info(f"{author.name} ({author.id}) tried to refer themselves")
        return

    # if the referee is not in the server
    if not referee.get("active"):
        UTILITY.Logger.info(
            f"{referee.get('name')} ({referee.get('user_id')}) is an in-active referee. Referral has been cancelled"
        )
        return

    # if the referee is not verified
    elif not referee.get("verified"):
        UTILITY.Logger.info(
            f"{referee.get('name')} ({referee.get('user_id')}) is an un-verified referee. Referral has been cancelled"
        )
        return

    if not database().contains(Query().user_id == author.id):
        database().insert(new_member_file(author))

    # set the referred_by value of the user
    database().update(
        {"referred_by": referee.get("user_id")}, Query().user_id == author.id
    )
    UTILITY.Logger.info(
        f"{author.name} ({author.id}) was referred by {referee.get('name')} ({referee.get('user_id')})"
    )

    # update the referee's points
    new_referrals = referee.get("referrals") + [author.id]
    referee["points"] += SETTINGS.referrals.referral_points
    new_points = referee["points"]
    database().update(
        {"referrals": new_referrals, "points": new_points},
        Query().user_id == referee.get("user_id"),
    )
    UTILITY.Logger.info(
        f"{referee.get('name', 'Unknown')} ({referee.get('user_id')}) has been given 5 points"
    )
    await check_points(guild, referee)

    # Send a message to the user confirming their referral
    try:
        await author.send(
            f"{author.mention} you have been referred by {referee.get('name')} ({referee.get('user_id')}) using code `{referral_code}`."
        )
    except discord.Forbidden:
        pass

    # Update the potential referee's referee's points
    referee_referee = database().get(Query().user_id == referee.get("referred_by"))
    if not referee_referee:
        return
    referee_referee["points"] += SETTINGS.referrals.descendant_points
    new_referee_points = referee_referee["points"]
    database().update(
        {"referrals": new_referrals, "points": new_points},
        Query().user_id == referee_referee.get("user_id"),
    )
    UTILITY.Logger.info(
        f"{referee_referee.get('name', 'Unknown')} ({referee_referee.get('user_id')}) has been given 2 points"
    )
    await check_points(guild, referee_referee)


Logger = Logger()
