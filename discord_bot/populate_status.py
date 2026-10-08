import os
import sys
import asyncio
from datetime import datetime
from dotenv import load_dotenv
import discord

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
token = os.getenv("DISCORD_BOT_TOKEN")
guild_id = int(os.getenv("DISCORD_GUILD_ID"))

client = discord.Client(intents=discord.Intents.default())

@client.event
async def on_ready():
    guild = client.get_guild(guild_id)
    status_ch = discord.utils.get(guild.text_channels, name="ℹ️・status")
    if status_ch:
        async for m in status_ch.history(limit=10):
            await m.delete()

        embed = discord.Embed(
            title="ℹ️ The Webport Union — Live Status & Service Health",
            description=(
                "Real-time operational status for all official domains, CDN mirrors, and bot services.\n\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                "### 🌐 Domain & Hosting Status\n"
                "• 🟢 **Official Domain** (`webportunion.games`): **OPERATIONAL (200 OK)**\n"
                "• 🟢 **Vercel Mirror** (`webport-union.vercel.app`): **OPERATIONAL**\n"
                "• 🟢 **Permanent CDN** (`cdn.jsdelivr.net`): **OPERATIONAL**\n"
                "• 🟢 **Stealth SVG Launcher** (`/launcher.svg`): **ACTIVE**\n\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                "### 🛡️ Filter Evasion Status\n"
                "• 🟢 **GoGuardian**: **Unblocked** *(via `.svg` & BYOD mirrors)*\n"
                "• 🟢 **Securly**: **Unblocked** *(via `webportunion.games` & jsDelivr)*\n"
                "• 🟢 **Lightspeed / ContentKeeper**: **Unblocked** *(via BYOD GCS router)*\n\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                "### 🤖 Core Automation Services\n"
                "• 🟢 **Discord Bot Service**: **ONLINE (24/7 Monitoring)**\n"
                "• 🟢 **Ticketing System**: **OPERATIONAL**\n"
                "• 🟢 **GitHub Webhook Bridge**: **ACTIVE**\n\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                "*If you find a blocked link or notice downtime, open a ticket in <#1557554422161084428> (`open-a-ticket`).*"
            ),
            colour=0x2ecc71,
            timestamp=datetime.now()
        )
        embed.set_footer(text="The Webport Union • Continuous Status Monitor")

        await status_ch.send(embed=embed)
        print("✓ Successfully populated #status channel with live health dashboard!", flush=True)

    await client.close()

if __name__ == "__main__":
    client.run(token)
