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
    print(f"Updating Webporting Community focus on {guild.name}...", flush=True)

    # 1. Update Server Description
    bio_text = "The Webport Union — The home for WebAssembly porters, game decompilations, retro emulation cores, and unblockable web infrastructure."
    try:
        await guild.edit(description=bio_text)
        print("✓ Updated server bio to Webporting Community focus", flush=True)
    except Exception as e:
        print("Note on guild description:", e, flush=True)

    # 2. Update Announcements
    announce_ch = discord.utils.get(guild.text_channels, name="📢・announcements")
    if announce_ch:
        embed = discord.Embed(
            title="🛠️ THE WEBPORT UNION — WEBPORTING & DECOMPILATION COMMUNITY",
            description=(
                "**Welcome to the central hub for WebAssembly decompilations & browser porting.**\n\n"
                "We are a community of porters, reverse engineers, and developers bringing native titles, "
                "retro engines, and WebAssembly games to the modern web.\n\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                "### 🔨 What We Build & Support\n"
                "• 🕹️ **Source Decomps & Web Ports**: Native C/C++/Rust compiled directly to WASM + WebGL.\n"
                "• 📦 **Direct CDN Mirroring**: Permanent unthrottled jsDelivr asset delivery.\n"
                "• 🛠️ **Developer Collaboration**: Porting help, Cross-Origin Isolation (COOP/COEP), and memory optimizations.\n"
                "• 🔗 **BYOD Infrastructure**: Decentralized domain routing so ports stay accessible anywhere.\n\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                "### 👥 Get Involved\n"
                "• Show off your builds in <#1557556015501803622> (`your-ports`)\n"
                "• Submit decomp requests in <#1557556012494622760> (`port-requests`)\n"
                "• Get debugging assistance in <#1557556013627084880> (`porting-help`)\n"
                "• Grab live production links in <#1557554341991419944> (`official-links`)"
            ),
            colour=0x5865F2
        )
        embed.set_footer(text="The Webport Union • Compiled for the Web")
        await announce_ch.send(embed=embed)
        print("✓ Sent updated Webporting Community announcement", flush=True)
        await asyncio.sleep(1.0)

    # 3. Update Partners Ad
    partners_ch = discord.utils.get(guild.text_channels, name="🤝・partners")
    if partners_ch:
        ad_text = """# 🛠️ THE WEBPORT UNION
> The premier WebAssembly porting & game decompilation community. Built by porters, for porters.

### ⚡ What We Do:
* 🕹️ **Authentic Web Ports** — Genuine browser decompilations & retro cores (WASM, Canvas, WebGL).
* 🛠️ **Dev Collaboration** — Technical porting help, Emscripten setup, and COOP/COEP isolation.
* 📦 **Permanent CDN Mirrors** — Unthrottled jsDelivr endpoints with 1-click link extraction.
* 🔗 **BYOD Domain Generator** — Create unblockable custom client-side domain links.
* 💡 **Active Port Requests** — Work together on decompiling and porting new titles.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🌐 **Web Hub**: https://webport-union.vercel.app
🔗 **Join the Community**: https://discord.gg/4e9ckAw8Fv
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""
        async for m in partners_ch.history(limit=5):
            await m.delete()
        await partners_ch.send(ad_text)
        print("✓ Updated #partners ad to Webporting Community focus", flush=True)

    print("\n[SUCCESS] Webporting Community branding synchronized!", flush=True)
    await client.close()

client.run(token)
