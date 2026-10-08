import os
import sys
import json
import asyncio

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from typing import Optional, Dict, Any, List
from dotenv import load_dotenv
import discord
from discord import Permissions, PermissionOverwrite, Colour

dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path)

TOKEN = os.getenv("DISCORD_BOT_TOKEN")
GUILD_ID = int(os.getenv("DISCORD_GUILD_ID", 0))

if not TOKEN:
    print("[ERROR] DISCORD_BOT_TOKEN not found in .env")
    sys.exit(1)

intents = discord.Intents.default()
intents.guilds = True
client = discord.Client(intents=intents)

def log(msg: str):
    print(msg, flush=True)

async def get_target_guild() -> Optional[discord.Guild]:
    await client.wait_until_ready()
    guild = client.get_guild(GUILD_ID)
    if not guild:
        try:
            guild = await client.fetch_guild(GUILD_ID)
        except Exception as e:
            print(f"[ERROR] Could not fetch guild {GUILD_ID}: {e}")
            return None
    return guild

def parse_color(hex_str: Optional[str]) -> Colour:
    if not hex_str:
        return Colour.default()
    hex_str = hex_str.strip().lstrip("#")
    try:
        return Colour(int(hex_str, 16))
    except Exception:
        return Colour.default()

async def cmd_apply(layout_file: str):
    guild = await get_target_guild()
    if not guild:
        print(f"[ERROR] Cannot connect to server {GUILD_ID}")
        return

    if not guild.me.guild_permissions.administrator and not guild.me.guild_permissions.manage_channels:
        print("[ERROR] Bot lacks Manage Channels / Administrator permissions!")
        return

    with open(layout_file, "r", encoding="utf-8") as f:
        config = json.load(f)

    print(f"\n==========================================")
    print(f"Applying High-Precision Layout to: {guild.name}")
    print(f"==========================================")

    # 1. SETUP ROLES
    print("\n--- 1. CONFIGURING ROLES ---")
    current_roles = {r.name.lower(): r for r in guild.roles}
    created_or_updated_roles: Dict[str, discord.Role] = {}

    for rdef in config.get("roles", []):
        name = rdef["name"]
        color = parse_color(rdef.get("color"))
        hoist = rdef.get("hoist", True)
        mentionable = rdef.get("mentionable", False)

        perms = Permissions()
        if rdef.get("admin", False):
            perms = Permissions.all()
        elif rdef.get("moderator", False):
            perms.manage_messages = True
            perms.kick_members = True
            perms.ban_members = True
            perms.moderate_members = True
            perms.view_audit_log = True
            perms.manage_nicknames = True

        existing = current_roles.get(name.lower())
        if existing:
            if not existing.managed:
                try:
                    await existing.edit(
                        colour=color,
                        hoist=hoist,
                        mentionable=mentionable,
                        permissions=perms if (rdef.get("admin") or rdef.get("moderator")) else existing.permissions
                    )
                    log(f" ✓ Updated Role: {name}")
                    created_or_updated_roles[name.lower()] = existing
                except Exception as e:
                    print(f" ! Could not update role {name}: {e}")
            else:
                print(f" - Role {name} is managed by Discord bot integration.")
                created_or_updated_roles[name.lower()] = existing
        else:
            try:
                new_role = await guild.create_role(
                    name=name,
                    colour=color,
                    hoist=hoist,
                    mentionable=mentionable,
                    permissions=perms
                )
                print(f" + Created Role: {name}")
                created_or_updated_roles[name.lower()] = new_role
                await asyncio.sleep(1.0)
            except Exception as e:
                print(f" ! Error creating role {name}: {e}")

    # Reload all roles
    all_guild_roles = {r.name.lower(): r for r in guild.roles}

    # 2. CATEGORIES & CHANNELS
    print("\n--- 2. CONFIGURING CHANNELS & CATEGORIES ---")
    
    # Map existing channels for reuse (so we don't wipe logs-protector or verification)
    existing_channels_by_clean_name = {}
    for ch in guild.channels:
        clean = ch.name.replace("・", "-").replace(" ", "-").lower().strip("-")
        existing_channels_by_clean_name[clean] = ch
        existing_channels_by_clean_name[ch.name.lower()] = ch

    existing_categories = {c.name.lower(): c for c in guild.categories}

    for cat_def in config.get("categories", []):
        cat_name = cat_def["name"]
        
        # Build category overwrites
        cat_overwrites = {}
        for ow in cat_def.get("overwrites", []):
            role_name = ow["role"].lower()
            role_obj = all_guild_roles.get(role_name)
            if role_name == "@everyone":
                role_obj = guild.default_role

            if role_obj:
                overwrite = PermissionOverwrite()
                for perm_k, perm_v in ow.get("permissions", {}).items():
                    if hasattr(overwrite, perm_k):
                        setattr(overwrite, perm_k, perm_v)
                cat_overwrites[role_obj] = overwrite

        # Create or update Category
        category = existing_categories.get(cat_name.lower())
        if not category:
            try:
                category = await guild.create_category(name=cat_name, overwrites=cat_overwrites)
                print(f"\n[+] Created Category: {cat_name}")
                await asyncio.sleep(1.2)
            except Exception as e:
                print(f"\n[!] Category create error {cat_name}: {e}")
                continue
        else:
            try:
                await category.edit(overwrites=cat_overwrites)
                print(f"\n[✓] Synced Category Overwrites: {cat_name}")
                await asyncio.sleep(0.5)
            except Exception as e:
                print(f"\n[!] Category edit error {cat_name}: {e}")

        # Channels in category
        for ch_def in cat_def.get("channels", []):
            ch_name = ch_def["name"]
            ch_type = ch_def.get("type", "text").lower()
            topic = ch_def.get("topic", "")

            clean_target = ch_name.replace("・", "-").replace(" ", "-").lower().strip("-")
            existing_ch = existing_channels_by_clean_name.get(clean_target) or existing_channels_by_clean_name.get(ch_name.lower())

            # Specific channel overwrites
            ch_overwrites = dict(cat_overwrites)
            for ow in ch_def.get("overwrites", []):
                role_name = ow["role"].lower()
                role_obj = all_guild_roles.get(role_name)
                if role_name == "@everyone":
                    role_obj = guild.default_role
                if role_obj:
                    overwrite = ch_overwrites.get(role_obj, PermissionOverwrite())
                    for perm_k, perm_v in ow.get("permissions", {}).items():
                        if hasattr(overwrite, perm_k):
                            setattr(overwrite, perm_k, perm_v)
                    ch_overwrites[role_obj] = overwrite

            if existing_ch and not isinstance(existing_ch, discord.CategoryChannel):
                # Update & Move into category
                try:
                    await existing_ch.edit(name=ch_name, category=category, topic=topic if hasattr(existing_ch, 'topic') else None, overwrites=ch_overwrites)
                    print(f"   ✓ Reused & Moved Channel: {ch_name}")
                except Exception as e:
                    print(f"   ! Could not move {existing_ch.name}: {e}")
            else:
                # Create New
                try:
                    if ch_type == "voice":
                        await guild.create_voice_channel(name=ch_name, category=category, overwrites=ch_overwrites)
                        print(f"   🔊 Created Voice: {ch_name}")
                    elif ch_type == "announcement":
                        # If server is not a community server yet, announcement might fallback to text
                        try:
                            await guild.create_text_channel(name=ch_name, category=category, topic=topic, overwrites=ch_overwrites, news=True)
                            print(f"   📢 Created Announcement: {ch_name}")
                        except Exception:
                            await guild.create_text_channel(name=ch_name, category=category, topic=topic, overwrites=ch_overwrites)
                            print(f"   # Created Text (Announcement): {ch_name}")
                    else:
                        await guild.create_text_channel(name=ch_name, category=category, topic=topic, overwrites=ch_overwrites)
                        print(f"   # Created Text: {ch_name}")
                    await asyncio.sleep(1.0)
                except Exception as e:
                    print(f"   ! Error creating {ch_name}: {e}")

    print("\n[COMPLETE] Successfully applied the complete server setup!")

@client.event
async def on_ready():
    mode = sys.argv[1] if len(sys.argv) > 1 else "inspect"
    if mode == "apply":
        layout_file = sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.path.dirname(__file__), "layout.json")
        await cmd_apply(layout_file)
    else:
        await cmd_inspect()
    await client.close()

if __name__ == "__main__":
    client.run(TOKEN)
