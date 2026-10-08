import os
import sys
import asyncio
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
    byod_ch = discord.utils.get(guild.text_channels, name="💻・byod-make-links")
    if byod_ch:
        async for m in byod_ch.history(limit=10):
            await m.delete()

        embed1 = discord.Embed(
            title="💻 Bring Your Own Domain (BYOD) — Overview",
            description=(
                "**What is BYOD?**\n"
                "BYOD allows you to generate your own private, personal unblockable mirrors of The Webport Union. "
                "Because your custom domain or CDN link is unique to you, school filters (GoGuardian, Securly, Lightspeed) "
                "do not have it on any blacklist!\n\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                "### 🎯 The 4 Official BYOD Methods\n"
                "Read the guides below to set up your personal mirror in under 3 minutes."
            ),
            colour=0x3498db
        )

        embed2 = discord.Embed(
            title="1️⃣ Method 1: The jsDelivr .svg Stealth Link (100% Free & No Card)",
            description=(
                "School filters categorize files by extension, treating `.svg` files as harmless images.\n\n"
                "**How to set it up:**\n"
                "1. Fork or push The Webport Union repository to a public GitHub account.\n"
                "2. Ensure `launcher.svg` is in the repository.\n"
                "3. Access your private link formatted as:\n"
                "   `https://cdn.jsdelivr.net/gh/<YOUR_USERNAME>/<REPO_NAME>@main/launcher.svg`\n\n"
                "🛡️ **Stealth Feature**: The SVG automatically disguises the browser tab as **Google Drive** with the drive icon and embeds the full app in full-screen."
            ),
            colour=0x2ecc71
        )

        embed3 = discord.Embed(
            title="2️⃣ Method 2: Custom Domain DNS Setup (Name.com / Namecheap / Porkbun)",
            description=(
                "If you bought a custom domain (e.g. from Name.com or Namecheap):\n\n"
                "**Step 1: In your Domain DNS Panel**\n"
                "Add a CNAME record:\n"
                "• **Type**: `CNAME`\n"
                "• **Host / Name**: `@` (or `play`)\n"
                "• **Target / Value**: `cname.vercel-dns.com`\n\n"
                "*(Or set Custom Nameservers to `ns1.vercel-dns.com` & `ns2.vercel-dns.com`)*\n\n"
                "**Step 2: Connect to Vercel**\n"
                "Add your domain in your Vercel Project Settings. SSL activates automatically in ~5 minutes!"
            ),
            colour=0x9b59b6
        )

        embed4 = discord.Embed(
            title="3️⃣ Method 3: Google Cloud Storage (storage.googleapis.com)",
            description=(
                "Google Classroom and Google Drive run on `storage.googleapis.com`, so school networks whitelist the entire domain.\n\n"
                "**How to deploy:**\n"
                "1. Open your terminal in the `byod-site` directory.\n"
                "2. Run: `python deploy_gcs.py`\n"
                "3. Enter your GCS bucket name.\n"
                "4. Access your games at:\n"
                "   `https://storage.googleapis.com/<YOUR_BUCKET>/launcher.svg`"
            ),
            colour=0xe67e22
        )

        embed5 = discord.Embed(
            title="4️⃣ Method 4: Cloudflare Pages (Free *.pages.dev Subdomain)",
            description=(
                "Cloudflare Pages requires **NO credit/debit card** and is free forever.\n\n"
                "1. Sign up at [pages.cloudflare.com](https://pages.cloudflare.com).\n"
                "2. Connect your GitHub repository.\n"
                "3. Cloudflare will deploy a private link such as:\n"
                "   `https://my-private-union.pages.dev`"
            ),
            colour=0xf1c40f
        )
        embed5.set_footer(text="The Webport Union • Continuous Filter Evasion Architecture")

        await byod_ch.send(embeds=[embed1, embed2, embed3, embed4, embed5])
        print("✓ Successfully published comprehensive BYOD guide to #byod-make-links!", flush=True)

    await client.close()

if __name__ == "__main__":
    client.run(token)
