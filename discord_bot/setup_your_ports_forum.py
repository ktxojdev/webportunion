import os
import sys
import asyncio
import discord
from dotenv import load_dotenv

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

ENV_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
load_dotenv(ENV_PATH)
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
GUILD_ID = int(os.getenv("DISCORD_GUILD_ID", "1557545995271807016"))

client = discord.Client(intents=discord.Intents.default())

@client.event
async def on_ready():
    print(f"Logged in as {client.user}", flush=True)
    guild = client.get_guild(GUILD_ID)
    if not guild:
        print(f"[ERROR] Could not find guild {GUILD_ID}", flush=True)
        await client.close()
        return

    # 1. Find existing your-ports channel
    old_channel = None
    for c in guild.channels:
        if "your-ports" in c.name:
            old_channel = c
            break

    category = None
    pos = 27
    if old_channel:
        category = old_channel.category
        pos = old_channel.position
        print(f"Found existing channel: {old_channel.name} (ID: {old_channel.id}, Type: {old_channel.type})", flush=True)
        # Delete old text channel
        print("Deleting old text channel...", flush=True)
        await old_channel.delete(reason="Converting to forum discussion channel")
        await asyncio.sleep(1.0)
    else:
        # Find category by name if channel wasn't found
        for cat in guild.categories:
            if "THE WEBPORT UNION" in cat.name.upper():
                category = cat
                break

    # 2. Define Forum Tags
    tags = [
        discord.ForumTag(name="WASM Port", emoji="🎮", moderated=False),
        discord.ForumTag(name="Retro Emu", emoji="🕹️", moderated=False),
        discord.ForumTag(name="In Progress", emoji="🔧", moderated=False),
        discord.ForumTag(name="Playable", emoji="✅", moderated=False),
        discord.ForumTag(name="Help Wanted", emoji="💡", moderated=False),
        discord.ForumTag(name="CDN Mirror", emoji="📦", moderated=False),
    ]

    # 3. Setup Overwrites
    member_role = discord.utils.get(guild.roles, name="Member")
    everyone_role = guild.default_role

    overwrites = {
        everyone_role: discord.PermissionOverwrite(
            view_channel=False
        )
    }

    if member_role:
        overwrites[member_role] = discord.PermissionOverwrite(
            view_channel=True,
            read_messages=True,
            send_messages=True,
            create_public_threads=True,
            send_messages_in_threads=True,
            read_message_history=True,
            embed_links=True,
            attach_files=True,
            add_reactions=True
        )

    # 4. Create Forum Channel
    topic = "Showcase community WebAssembly decompilations, retro cores, and custom browser ports. Create a post for each project!"
    print(f"Creating forum channel in category {category.name if category else 'None'} at position {pos}...", flush=True)

    forum = await guild.create_forum(
        name="🚀・your-ports",
        topic=topic,
        category=category,
        position=pos,
        available_tags=tags,
        overwrites=overwrites,
        reason="Upgraded to Forum discussion channel"
    )
    print(f"✓ Created forum channel: {forum.name} (ID: {forum.id})", flush=True)
    await asyncio.sleep(1.0)

    # 5. Create Pinned Guidelines / Showcase Template Post
    guidelines_tag = [t for t in forum.available_tags if t.name == "Playable"]

    embed = discord.Embed(
        title="🚀 Community Port Showcase — Rules & Submission Template",
        description=(
            "Welcome to **#your-ports**! This is a dedicated discussion forum for developers, "
            "porters, and web engineers to publish their custom WebAssembly ports and retro emulation builds.\n\n"
            "Each port or release should have its own post so other union members can test, discuss, and review it."
        ),
        color=0x2ecc71
    )
    embed.add_field(
        name="📋 Post Format / Template",
        value=(
            "When creating a new post, please provide:\n"
            "```markdown\n"
            "**Game / Project Title**: \n"
            "**Engine / Architecture**: (e.g. WASM, Emscripten, Godot HTML5, Canvas)\n"
            "**Live Demo / jsDelivr CDN**: \n"
            "**GitHub / Source Repository**: \n"
            "**Controls**: \n"
            "**Known Issues / Status**: \n"
            "```"
        ),
        inline=False
    )
    embed.add_field(
        name="🔒 Performance & Security Headers",
        value=(
            "If your port uses multithreaded WASM or `SharedArrayBuffer`, remind testers to access it with Cross-Origin Isolation (`COOP: same-origin`, `COEP: require-corp`)."
        ),
        inline=False
    )
    embed.add_field(
        name="⚡ Permanent CDN Integration",
        value=(
            "We strongly encourage providing direct **jsDelivr** links or static bundles so community ports can be integrated into the stealth `.svg` launcher."
        ),
        inline=False
    )
    embed.set_footer(text="The Webport Union • Porting & WebAssembly Community")

    thread_with_msg = await forum.create_thread(
        name="📌 Showcase Guidelines & Submission Template",
        content="Welcome to the **#your-ports** forum! Read the guidelines below before publishing your port:",
        embed=embed,
        applied_tags=guidelines_tag if guidelines_tag else []
    )
    
    # Pin the thread
    try:
        await thread_with_msg.thread.edit(pinned=True)
        print("✓ Pinned guidelines thread successfully!", flush=True)
    except Exception as e:
        print(f"Note: Could not pin thread: {e}", flush=True)

    print("\n[SUCCESS] your-ports successfully converted to a Forum discussion channel!", flush=True)
    await client.close()

client.run(TOKEN)
