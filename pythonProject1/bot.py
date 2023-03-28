import discord
import os
from discord.ext import commands
from discord import app_commands
import ffacts
from dotenv import load_dotenv
from pymongo import MongoClient


def run_dc_bot():
    load_dotenv()
    TOKEN = os.getenv("DISCORD_TOKEN")
    WEATHER = os.getenv("WEATHER_TOKEN")

    intents = discord.Intents.all()
    intents.message_content = True

    client = commands.Bot(command_prefix="!", intents=intents)
    dbclient = MongoClient("localhost", 27017)
    db = dbclient["mydatabase"]
    collection = db["customers"]

    @client.event
    async def on_ready():
        print("Logged in as {0.user}".format(client))
        print(f"running discord.py version {discord.__version__}")
        try:
            synced = await client.tree.sync()
            print(f"Synced {len(synced)} command(s)")
        except Exception as error:
            print(error)

    @client.tree.command(name="hello")
    async def hello(interaction: discord.Interaction):
        await interaction.response.send_message("You executed the slash command!", ephemeral=True)  # noqa

    @client.tree.command(name="tell")
    @app_commands.describe(what_you_wanna_say="what to say?")
    async def tell(interaction: discord.Interaction, what_you_wanna_say: str):
        await interaction.response.send_message(  # noqa
            f"{interaction.user.name} tells @everyone: {what_you_wanna_say}")

    @client.tree.command(name="facts")
    async def facts(interaction: discord.Interaction):
        fact = ffacts.get_request("https://uselessfacts.jsph.pl/api/v2/facts/random", "text")
        await interaction.response.send_message(fact)  # noqa

    @client.tree.command(name="bored")
    async def bored(interaction: discord.Interaction):
        fact = ffacts.get_request("https://www.boredapi.com/api/activity", "activity")
        await interaction.response.send_message(fact)  # noqa

    @client.tree.command(name="kick")
    @commands.has_permissions(kick_members=True)
    async def kick(interaction: discord.Interaction, member: discord.User, *, reason: str = None):
        if interaction.user.name == "Ferni05":
            if reason is None:
                reason = "no reason at all (:"
            await interaction.guild.kick(member)
            await interaction.response.send_message(f"User {member.mention} has been kicked for {reason}")  # noqa
        else:
            await interaction.response.send_message("You cannot execute the kick-command, filthy peasant")  # noqa

    @client.tree.command(name="register")
    async def register(interaction: discord.Interaction):
        user = interaction.user.name
        if collection.find_one({"name": user}):
            await interaction.response.send_message("You already exist in the database!")  # noqa
        else:
            collection.insert_one(
                {"name": user, "loans": 0, "tester": 0, "inv": {"amount": 0, "money": 100, "total_handel": 0}})
            print(f"user '{user}' was added to the database")
            await interaction.response.send_message("You have been added to the database!")  # noqa

    @client.tree.command(name="remove_me")
    async def remove_me(interaction: discord.Interaction):
        user = interaction.user.name
        if collection.find_one({"name": user}):
            collection.delete_one({"name": user})
            print(f"user '{user}' was removed from the database")
            await interaction.response.send_message("You were removed from the database!")  # noqa
        else:
            await interaction.response.send_message("You don't exist in the database, you cannot be deleted!")  # noqa

    @client.tree.command(name="profile")
    async def profile(interaction: discord.Interaction):
        user = interaction.user.name
        info = collection.find_one({"name": user})
        await interaction.response.send_message(  # noqa
            f"Username: {info.get('name')} \nMoney: {info.get('inv').get('money')} "
            f"\nTades made:  {info.get('inv').get('total_handel')}")

    @client.event
    async def on_message(message):
        if message.author == client.user:
            return

        if message.content.startswith("hi"):
            await message.channel.send("Hello!")

    client.run(TOKEN)
