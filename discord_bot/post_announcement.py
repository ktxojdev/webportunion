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
    print(f"Publishing official announcement and onboarding in {guild.name}...", flush=True)

    # 1. ANNOUNCEMENTS CHANNEL
    announcements_ch = discord.utils.get(guild.text_channels, name="📢・announcements")
    if announcements_ch:
        embed_announce = discord.Embed(
            title="🌐 THE WEBPORT UNION — OFFICIAL LAUNCH",
            description=(
                "**Welcome to the next generation of unblocked WebAssembly infrastructure!**\n\n"
                "The Webport Union is an open community dedicated to archiving, compiling, "
                "and hosting authentic WebAssembly decompilations, retro emulation cores, and resilient web proxies.\n\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                "### ⚡ What We Offer\n"
                "• 🎮 **Genuine Web Ports**: High-performance browser WebAssembly architecture and retro emulation.\n"
                "• 🔗 **Unblockable Architecture**: BYOD (Build Your Own Domain) tools and permanent CDN endpoints via jsDelivr.\n"
                "• 🚀 **High Speed**: Zero bloat, hosted on Vercel Edge networks.\n"
                "• 🛡️ **Community Driven**: Request new ports, share your own, and get active help from developers.\n\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                "### 🧭 Quick Navigation\n"
                "• **Working Mirrors**: <#1557554341991419944> / `official-links`\n"
                "• **Production Portal**: [webport-union.vercel.app](https://webport-union.vercel.app)\n"
                "• **Rules & Safety**: <#1557554336048091219> / `rules`\n"
                "• **Request a Port**: <#1557556012494622760> / `port-requests`\n\n"
                "Enjoy your stay and game on! 🎉"
            ),
            colour=0x5865F2
        )
        embed_announce.set_image(url="https://images.unsplash.com/photo-1550745165-9bc0b252726f?auto=format&fit=crop&w=1200&q=80")
        embed_announce.set_footer(text="The Webport Union • Built for the Community", icon_url=guild.icon.url if guild.icon else None)
        
        # Ping @everyone
        await announcements_ch.send(content="@everyone 🚀 **The Webport Union is officially live!**", embed=embed_announce)
        print("✓ Sent @everyone launch announcement", flush=True)
        await asyncio.sleep(1.0)

    # 2. WELCOME / ONBOARDING CHANNEL
    welcome_ch = discord.utils.get(guild.text_channels, name="👋・welcome")
    if welcome_ch:
        async for m in welcome_ch.history(limit=5):
            await m.delete()

        embed_onboarding = discord.Embed(
            title="👋 Welcome to The Webport Union — Member Onboarding",
            description=(
                "Hey there! Welcome to **The Webport Union**. Follow this quick 4-step checklist to get fully set up in the server:\n\n"
                "### 1️⃣ Step 1: Verify Your Account\n"
                "Head over to <#1557546295504273458> (`verification`) and click the green verify button. This unlocks all public chat rooms, game links, and voice lobbies.\n\n"
                "### 2️⃣ Step 2: Read The Rules\n"
                "Familiarize yourself with our server guidelines in <#1557554336048091219> (`rules`) to ensure a safe, fun community for everyone.\n\n"
                "### 3️⃣ Step 3: Grab Official Links\n"
                "Looking for unblocked games or proxy mirrors? Check out <#1557554341991419944> (`official-links`) and <#1557556023307669524> (`live-deployments`).\n\n"
                "### 4️⃣ Step 4: Say Hi & Get Involved!\n"
                "Jump into <#1557554350354857994> (`general`) to chat with members, or submit ideas in <#1557556009848143922> (`port-requests`)!\n\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                "*Need assistance? Open a ticket anytime in <#1557554359410364467> (`open-a-ticket`).*"
            ),
            colour=0x2ecc71
        )
        embed_onboarding.set_footer(text="Step into the Union • Fast, Unblocked, Community-Powered")
        await welcome_ch.send(embed=embed_onboarding)
        print("✓ Sent onboarding guide to #welcome", flush=True)

    print("\n[COMPLETE] Announcement and onboarding posted successfully!", flush=True)
    await client.close()

client.run(token)
