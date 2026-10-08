import os, sys, asyncio, discord
from dotenv import load_dotenv

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
token = os.getenv("DISCORD_BOT_TOKEN")
guild_id = int(os.getenv("DISCORD_GUILD_ID"))

intents = discord.Intents.default()
intents.guilds = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    await client.wait_until_ready()
    print("Guilds in cache:", [g.name for g in client.guilds], flush=True)
    guild = client.get_guild(guild_id)
    if not guild:
        guild = await client.fetch_guild(guild_id)
    print("Guild:", guild.name, flush=True)
    member = guild.get_member(client.user.id)
    if not member:
        member = await guild.fetch_member(client.user.id)
    print("Bot member:", member.name, flush=True)
    print("Bot top role:", member.top_role.name, "pos:", member.top_role.position, flush=True)
    print("Bot admin perm:", member.guild_permissions.administrator, flush=True)
    print("Bot manage_channels perm:", member.guild_permissions.manage_channels, flush=True)
    print("Bot manage_roles perm:", member.guild_permissions.manage_roles, flush=True)
    
    roles = await guild.fetch_roles()
    print("All roles:")
    for r in sorted(roles, key=lambda x: x.position, reverse=True):
        print(f" - {r.name} (id: {r.id}, pos: {r.position})", flush=True)
    await client.close()

client.run(token)
