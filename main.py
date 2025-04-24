# main.py
import discord
from discord.ext import commands
from discord import app_commands
import aiohttp
import json
import os
from dotenv import load_dotenv

# load environment variables
load_dotenv()
OSU_CLIENT_ID = os.getenv("OSU_CLIENT_ID")
OSU_CLIENT_SECRET = os.getenv("OSU_CLIENT_SECRET")
TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

linked_users = {}

# load links if file exists
if os.path.exists("linked_users.json"):
    with open("linked_users.json", "r") as f:
        linked_users = json.load(f)

# save links to file
def save_links():
    with open("linked_users.json", "w") as f:
        json.dump(linked_users, f)

# fetch osu token
async def get_osu_token():
    url = "https://osu.ppy.sh/oauth/token"
    data = {
        "client_id": OSU_CLIENT_ID,
        "client_secret": OSU_CLIENT_SECRET,
        "grant_type": "client_credentials",
        "scope": "public"
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=data) as resp:
            return (await resp.json())["access_token"]

# fetch osu profile
async def get_osu_profile(username, token):
    url = f"https://osu.ppy.sh/api/v2/users/{username}/osu"
    headers = {"Authorization": f"Bearer {token}"}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as resp:
            if resp.status == 200:
                return await resp.json()
            return None

@bot.event
async def on_ready():
    print(f"bot ready as {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"synced {len(synced)} commands")
    except Exception as e:
        print(e)

# link command
@bot.tree.command(name="link", description="link your osu! username")
@app_commands.describe(username="your osu! username")
async def link(interaction: discord.Interaction, username: str):
    linked_users[str(interaction.user.id)] = username
    save_links()
    await interaction.response.send_message(f"linked to osu! user `{username}`", ephemeral=True)

# profile command
@bot.tree.command(name="profile", description="show your linked osu! profile stats")
async def profile(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    if user_id not in linked_users:
        await interaction.response.send_message("you need to `/link` your osu! account first.", ephemeral=True)
        return

    token = await get_osu_token()
    username = linked_users[user_id]
    profile_data = await get_osu_profile(username, token)

    if not profile_data:
        await interaction.response.send_message("couldn't find osu! profile. check your link.", ephemeral=True)
        return

    embed = discord.Embed(title=f"osu! profile: {profile_data['username']}", color=discord.Color.blurple())
    embed.set_thumbnail(url=profile_data["avatar_url"])
    embed.add_field(name="pp", value=profile_data["statistics"]["pp"], inline=True)
    embed.add_field(name="rank", value=f"#{profile_data['statistics']['global_rank']}", inline=True)
    embed.add_field(name="accuracy", value=f"{profile_data['statistics']['hit_accuracy']:.2f}%", inline=True)
    embed.add_field(name="playcount", value=profile_data["statistics"]["play_count"], inline=True)
    embed.set_footer(text="osu! api v2")

    await interaction.response.send_message(embed=embed)

# run the bot
bot.run(TOKEN)
