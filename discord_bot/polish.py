import os, sys, asyncio, discord
from dotenv import load_dotenv

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
token = os.getenv("DISCORD_BOT_TOKEN")
guild_id = int(os.getenv("DISCORD_GUILD_ID"))

client = discord.Client(intents=discord.Intents.default())

@client.event
async def on_ready():
    guild = client.get_guild(guild_id)
    print(f"Polishing and perfecting {guild.name}...", flush=True)

    # 1. Categories
    start_here = discord.utils.get(guild.categories, name="📌・START HERE")
    staff_only = discord.utils.get(guild.categories, name="🔒・STAFF ONLY")
    
    # Create or get Security & Logs category
    security_cat = discord.utils.get(guild.categories, name="🛡️・SECURITY & LOGS")
    if not security_cat:
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False)
        }
        for role_name in ["👑 Owner", "⚡ Co-Owner", "Administrator", "Wick", "SetupServer", "Protector"]:
            r = discord.utils.get(guild.roles, name=role_name)
            if r:
                overwrites[r] = discord.PermissionOverwrite(view_channel=True, read_message_history=True)
        security_cat = await guild.create_category(name="🛡️・SECURITY & LOGS", overwrites=overwrites)
        print("Created 🛡️・SECURITY & LOGS category", flush=True)
        await asyncio.sleep(1.0)

    # 2. Fix Verification channel (keep the one with Protector's prompt)
    old_verify = None
    new_verify = None
    for ch in guild.text_channels:
        if ch.id == 1557546295504273458:
            old_verify = ch
        elif ch.id == 1557554338740703376:
            new_verify = ch

    if old_verify and new_verify:
        await new_verify.delete()
        print("Removed duplicate empty verification channel", flush=True)
        await old_verify.edit(name="✅・verification", category=start_here, position=0)
        print("Moved Protector's active verification into 📌・START HERE", flush=True)
        await asyncio.sleep(1.0)

    # 3. Move logs into 🛡️・SECURITY & LOGS
    for log_name in ["logs-protector", "wick-logs", "modlogs"]:
        ch = discord.utils.get(guild.text_channels, name=log_name)
        if ch:
            await ch.edit(category=security_cat)
            print(f"Moved {log_name} into 🛡️・SECURITY & LOGS", flush=True)
            await asyncio.sleep(1.0)

    # 4. Remove default empty categories & channels
    for cat_name in ["Text Channels", "Voice Channels"]:
        cat = discord.utils.get(guild.categories, name=cat_name)
        if cat:
            for ch in list(cat.channels):
                if ch.name.lower() == "general":
                    await ch.delete()
                    print(f"Deleted default placeholder {ch.name}", flush=True)
                    await asyncio.sleep(0.5)
            await cat.delete()
            print(f"Deleted default {cat_name} category", flush=True)
            await asyncio.sleep(0.5)

    print("\n[COMPLETE] Server layout polished to perfection!", flush=True)
    await client.close()

client.run(token)
