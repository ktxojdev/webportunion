import os
import sys
import asyncio
from dotenv import load_dotenv
import discord

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
token = os.getenv("DISCORD_BOT_TOKEN")
guild_id = int(os.getenv("DISCORD_GUILD_ID"))

intents = discord.Intents.default()
intents.members = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    guild = client.get_guild(guild_id)
    owner_role = discord.utils.get(guild.roles, name="👑 Owner")
    admin_role = discord.utils.get(guild.roles, name="Administrator")
    mod_role = discord.utils.get(guild.roles, name="⚔️ Moderator")
    member_role = discord.utils.get(guild.roles, name="Member")

    async for m in guild.fetch_members(limit=100):
        # 1. ktxojdev -> Owner
        if m.id == guild.owner_id or "ktxoj" in m.name.lower():
            if owner_role:
                await m.add_roles(owner_role, member_role)
                print(f"✓ ktxojdev confirmed as Owner & Member", flush=True)

        # 2. q8j -> Administrator
        elif "q8j" in m.name.lower():
            if admin_role:
                await m.add_roles(admin_role, member_role)
                print(f"✓ q8j promoted to Administrator", flush=True)

        # 3. turg -> Moderator
        elif "turg" in m.name.lower():
            if mod_role:
                await m.add_roles(mod_role, member_role)
                print(f"✓ turg promoted to Moderator", flush=True)

    print("\n[SUCCESS] Staff roles successfully assigned!", flush=True)
    await client.close()

if __name__ == "__main__":
    client.run(token)
