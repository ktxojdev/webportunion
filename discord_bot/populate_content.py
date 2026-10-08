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
    print(f"Populating channels in {guild.name}...", flush=True)

    # 1. Rules Channel
    rules_ch = discord.utils.get(guild.text_channels, name="📜・rules")
    if rules_ch:
        async for m in rules_ch.history(limit=5):
            await m.delete()
        embed = discord.Embed(
            title="📜 The Webport Union — Official Guidelines",
            description=(
                "Welcome to **The Webport Union**. We are dedicated to high-precision WebAssembly decompilations, "
                "browser ports, and unblocked web infrastructure.\n\n"
                "**1. Respect & Decorum**\n"
                "Treat all members, contributors, and staff with respect. No harassment, hate speech, or toxicity.\n\n"
                "**2. Genuine Ports Only**\n"
                "Only share authentic WebAssembly / Canvas / WebGL ports and verified proxy mirrors. Zero phishing or malware.\n\n"
                "**3. Keep Channels Organized**\n"
                "Use `🤖・bot-commands` for bot interactions, `💡・port-requests` for port suggestions, and `🛠️・porting-help` for dev support.\n\n"
                "**4. No Spam or Advertising**\n"
                "Unsolicited DM ads or self-promotion outside of `🤝・partners` is strictly prohibited.\n\n"
                "**5. Follow Discord Community Guidelines**\n"
                "All members must adhere to Discord ToS and Community Standards."
            ),
            colour=0x3498db
        )
        embed.set_footer(text="The Webport Union • Precision Static Architecture")
        await rules_ch.send(embed=embed)
        print("✓ Populated #rules", flush=True)
        await asyncio.sleep(1.0)

    # 2. Official Links Channel
    links_ch = discord.utils.get(guild.text_channels, name="🔗・official-links")
    if links_ch:
        async for m in links_ch.history(limit=5):
            await m.delete()
        embed = discord.Embed(
            title="🌐 The Webport Union — Official Mirrors & Endpoints",
            description=(
                "Official permanent CDN mirrors and deployment hubs for The Webport Union.\n\n"
                "🔗 **Primary Hub (Vercel)**: `https://webport-union.vercel.app`\n"
                "📦 **Permanent CDN**: `https://cdn.jsdelivr.net/gh/wasmdotrip/wasm.rip@main/`\n"
                "🎮 **GTA III Web**: Native WebAssembly re3 port with full audio & graphics.\n"
                "🕹️ **Nintendo Web Emu**: High-precision WebAssembly retro emulation core.\n"
                "💻 **BYOD Tool**: Build Your Own Domain router to generate unblockable school mirrors."
            ),
            colour=0x2ecc71
        )
        embed.add_field(name="Cross-Origin Isolation", value="All multithreaded WASM ports run with mandatory COOP & COEP headers.", inline=False)
        embed.set_footer(text="Verified & Maintained by The Webport Union")
        await links_ch.send(embed=embed)
        print("✓ Populated #official-links", flush=True)
        await asyncio.sleep(1.0)

    # 3. Live Deployments
    live_ch = discord.utils.get(guild.text_channels, name="🌐・live-deployments")
    if live_ch:
        async for m in live_ch.history(limit=5):
            await m.delete()
        embed = discord.Embed(
            title="🚀 Live Deployment Dashboard",
            description=(
                "Real-time list of live production instances:\n\n"
                "• **Webport Union Portal**: [webport-union.vercel.app](https://webport-union.vercel.app)\n"
                "• **BYOD Site**: Deploy your custom DNS and domain mirrors.\n"
                "• **Haven OS & Amethyst**: Unblocked web operating environments.\n"
                "• **Blobwifi**: Lightweight proxy tunnel interface."
            ),
            colour=0x9b59b6
        )
        await live_ch.send(embed=embed)
        print("✓ Populated #live-deployments", flush=True)
        await asyncio.sleep(1.0)

    # 4. Port Requests
    req_ch = discord.utils.get(guild.text_channels, name="💡・port-requests")
    if req_ch:
        async for m in req_ch.history(limit=5):
            await m.delete()
        embed = discord.Embed(
            title="💡 How to Submit a Port Request",
            description=(
                "Want a specific retro game, open-source title, or tool ported to WebAssembly?\n\n"
                "**Format your request:**\n"
                "1. **Game/App Name**:\n"
                "2. **Open-Source Repository / Decomp** (e.g. GitHub link):\n"
                "3. **Engine / Language** (C, C++, Rust, Zig, Go):\n"
                "4. **License** (MIT, GPL, etc.):\n\n"
                "Our porting team reviews submissions regularly!"
            ),
            colour=0xf1c40f
        )
        await req_ch.send(embed=embed)
        print("✓ Populated #port-requests", flush=True)
        await asyncio.sleep(1.0)

    # 5. Porting Help
    help_ch = discord.utils.get(guild.text_channels, name="🛠️・porting-help")
    if help_ch:
        async for m in help_ch.history(limit=5):
            await m.delete()
        embed = discord.Embed(
            title="🛠️ WebAssembly & Porting Technical Resources",
            description=(
                "Need help compiling to WASM or setting up Cross-Origin Isolation?\n\n"
                "**Standard Standards:**\n"
                "• **Compiler**: Emscripten (`emcc` / `em++`) or `wasm32-unknown-emscripten`\n"
                "• **COOP Header**: `Cross-Origin-Opener-Policy: same-origin`\n"
                "• **COEP Header**: `Cross-Origin-Embedder-Policy: require-corp`\n"
                "• **Assets**: Link to permanent jsDelivr or bundle locally. Never use `raw.githack.com`.\n\n"
                "Feel free to post stack traces, build errors, or canvas rendering questions here!"
            ),
            colour=0xe67e22
        )
        await help_ch.send(embed=embed)
        print("✓ Populated #porting-help", flush=True)
        await asyncio.sleep(1.0)

    print("\n[SUCCESS] Channel content population completed!", flush=True)
    await client.close()

client.run(token)
