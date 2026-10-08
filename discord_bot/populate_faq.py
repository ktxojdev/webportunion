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
    faq_ch = discord.utils.get(guild.text_channels, name="❓・faq")
    if faq_ch:
        async for m in faq_ch.history(limit=10):
            await m.delete()

        embed = discord.Embed(
            title="❓ Frequently Asked Questions (FAQ)",
            description=(
                "Got questions about web ports, mirrors, or filter bypassing? Here are the answers to the most common questions!\n\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                "### 1. What is The Webport Union?\n"
                "We are a community of reverse engineers, developers, and modders who compile authentic C/C++/Rust "
                "game source code into WebAssembly (WASM) and WebGL so games run natively in any modern web browser.\n\n"
                "### 2. How do I bypass school filters (GoGuardian / Securly)?\n"
                "School filters block known domains, but they cannot block:\n"
                "• **BYOD Links**: Create your own private link using the instructions in <#1557554343165825227> (`byod-make-links`).\n"
                "• **The `.svg` Method**: Open `https://webportunion.games/launcher.svg` or our jsDelivr SVG link, which filters see as a harmless image.\n"
                "• **Our Custom Domain**: Use [webportunion.games](https://webportunion.games).\n\n"
                "### 3. Will my game saves stay intact?\n"
                "**Yes!** All our WebAssembly ports use the browser's persistent `IndexedDB` or `localStorage` virtual filesystem. "
                "As long as you don't clear your browser cookies/site data, your game progress will be saved automatically.\n\n"
                "### 4. How do I request a game or port?\n"
                "Go to <#1557556012494622760> (`port-requests`) and provide:\n"
                "1. Game Name\n"
                "2. Open-Source GitHub / Decompilation Repository\n"
                "3. Engine (C, C++, Rust, Zig)\n\n"
                "### 5. What if a link is blocked or down?\n"
                "Open a quick ticket in <#1557554422161084428> (`open-a-ticket`) or check <#1557554344407335013> (`status`) for mirror updates.\n\n"
                "### 6. How do I get the 🛠️ Webporter role?\n"
                "If you compile, mod, or contribute WebAssembly ports or proxy mirrors to the union, open a ticket or post your work in <#1557556015501803622> (`your-ports`). Staff will review and grant you the role!"
            ),
            colour=0x5865F2
        )
        embed.set_footer(text="The Webport Union • Knowledge Base & FAQ")

        await faq_ch.send(embed=embed)
        print("✓ Successfully populated #faq with comprehensive answers!", flush=True)

    await client.close()

if __name__ == "__main__":
    client.run(token)
