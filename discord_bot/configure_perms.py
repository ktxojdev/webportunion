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
    print(f"Configuring complete permission structure for {guild.name}...", flush=True)

    everyone = guild.default_role
    member_role = discord.utils.get(guild.roles, name="Member")
    verified_role = discord.utils.get(guild.roles, name="✅ Verified")
    owner_role = discord.utils.get(guild.roles, name="👑 Owner")
    coowner_role = discord.utils.get(guild.roles, name="⚡ Co-Owner")
    admin_role = discord.utils.get(guild.roles, name="Administrator")
    mod_role = discord.utils.get(guild.roles, name="⚔️ Moderator")
    bot_role = discord.utils.get(guild.roles, name="🤖 Bots")
    wick_role = discord.utils.get(guild.roles, name="Wick")

    # 1. Category: 📌・START HERE (Public for everyone, read-only except verification)
    cat_start = discord.utils.get(guild.categories, name="📌・START HERE")
    if cat_start:
        overwrites = {
            everyone: discord.PermissionOverwrite(view_channel=True, send_messages=False, read_message_history=True, add_reactions=True)
        }
        await cat_start.edit(overwrites=overwrites)
        print("✓ Configured 📌・START HERE permissions", flush=True)
        await asyncio.sleep(0.5)

    # 2. Category: 🌐・OFFICIAL LINKS (Only visible to verified Member, read-only)
    cat_links = discord.utils.get(guild.categories, name="🌐・OFFICIAL LINKS")
    if cat_links:
        overwrites = {
            everyone: discord.PermissionOverwrite(view_channel=False),
            member_role: discord.PermissionOverwrite(view_channel=True, send_messages=False, read_message_history=True, add_reactions=True)
        }
        if verified_role:
            overwrites[verified_role] = discord.PermissionOverwrite(view_channel=True, send_messages=False, read_message_history=True)
        await cat_links.edit(overwrites=overwrites)
        print("✓ Configured 🌐・OFFICIAL LINKS permissions", flush=True)
        await asyncio.sleep(0.5)

    # 3. Category: 💬・COMMUNITY (Only visible to verified Member, full chatting)
    cat_comm = discord.utils.get(guild.categories, name="💬・COMMUNITY")
    if cat_comm:
        overwrites = {
            everyone: discord.PermissionOverwrite(view_channel=False),
            member_role: discord.PermissionOverwrite(view_channel=True, send_messages=True, attach_files=True, embed_links=True, read_message_history=True)
        }
        if verified_role:
            overwrites[verified_role] = discord.PermissionOverwrite(view_channel=True, send_messages=True, attach_files=True, embed_links=True)
        await cat_comm.edit(overwrites=overwrites)
        print("✓ Configured 💬・COMMUNITY permissions", flush=True)
        await asyncio.sleep(0.5)

    # 4. Category: 🎫・SUPPORT (Only visible to verified Member)
    cat_supp = discord.utils.get(guild.categories, name="🎫・SUPPORT")
    if cat_supp:
        overwrites = {
            everyone: discord.PermissionOverwrite(view_channel=False),
            member_role: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)
        }
        if verified_role:
            overwrites[verified_role] = discord.PermissionOverwrite(view_channel=True, send_messages=True)
        await cat_supp.edit(overwrites=overwrites)
        print("✓ Configured 🎫・SUPPORT permissions", flush=True)
        await asyncio.sleep(0.5)

    # 5. Category: 🔊・VOICE CHANNELS (Only visible to verified Member)
    cat_vc = discord.utils.get(guild.categories, name="🔊・VOICE CHANNELS")
    if cat_vc:
        overwrites = {
            everyone: discord.PermissionOverwrite(view_channel=False),
            member_role: discord.PermissionOverwrite(view_channel=True, connect=True, speak=True)
        }
        if verified_role:
            overwrites[verified_role] = discord.PermissionOverwrite(view_channel=True, connect=True, speak=True)
        await cat_vc.edit(overwrites=overwrites)
        print("✓ Configured 🔊・VOICE CHANNELS permissions", flush=True)
        await asyncio.sleep(0.5)

    # 6. Category: 🔒・STAFF ONLY (Only Owner, Co-Owner, Administrator, Moderator)
    cat_staff = discord.utils.get(guild.categories, name="🔒・STAFF ONLY")
    if cat_staff:
        overwrites = {
            everyone: discord.PermissionOverwrite(view_channel=False)
        }
        if member_role:
            overwrites[member_role] = discord.PermissionOverwrite(view_channel=False)
        for staff_r in [owner_role, coowner_role, admin_role, mod_role]:
            if staff_r:
                overwrites[staff_r] = discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True, manage_messages=True)
        await cat_staff.edit(overwrites=overwrites)
        print("✓ Configured 🔒・STAFF ONLY permissions", flush=True)
        await asyncio.sleep(0.5)

    # 7. Category: 🛡️・SECURITY & LOGS (Only Admins, Wick, Protector)
    cat_sec = discord.utils.get(guild.categories, name="🛡️・SECURITY & LOGS")
    if cat_sec:
        overwrites = {
            everyone: discord.PermissionOverwrite(view_channel=False)
        }
        if member_role:
            overwrites[member_role] = discord.PermissionOverwrite(view_channel=False)
        for adm in [owner_role, coowner_role, admin_role, wick_role]:
            if adm:
                overwrites[adm] = discord.PermissionOverwrite(view_channel=True, read_message_history=True)
        protector_role = discord.utils.get(guild.roles, name="Protector")
        if protector_role:
            overwrites[protector_role] = discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)
        await cat_sec.edit(overwrites=overwrites)
        print("✓ Configured 🛡️・SECURITY & LOGS permissions", flush=True)
        await asyncio.sleep(0.5)

    print("\n[SUCCESS] All channel permissions synchronized with verification & staff gates!", flush=True)
    await client.close()

client.run(token)
