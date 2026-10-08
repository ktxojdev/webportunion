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

IMG_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "nintendo-web-emu", "img"))

@client.event
async def on_ready():
    guild = client.get_guild(guild_id)
    peeks_ch = discord.utils.get(guild.text_channels, name="👀・sneak-peeks")
    if peeks_ch:
        async for m in peeks_ch.history(limit=10):
            await m.delete()

        # Clean Minimalist UI & Theater Canvas
        img_ui_path = os.path.join(IMG_DIR, "screenshot.png")
        if os.path.exists(img_ui_path):
            file_ui = discord.File(img_ui_path, filename="ui_preview.png")
            embed_ui = discord.Embed(
                title="🔮 Sneak Peek: Minimalist Dark UI & Webport Union Portal",
                description=(
                    "A fresh look at **The Webport Union** platform:\n\n"
                    "• **Design System**: Minimalist shadcn/ui zinc dark tokens (`#09090b` background).\n"
                    "• **Theater Canvas**: Instant full-screen expansion, reload, and popout windows.\n"
                    "• **Cross-Origin Isolation**: Native support for multithreaded WebAssembly cores.\n"
                    "• **Zero Bloat**: Clean, original, and high-performance static web infrastructure."
                ),
                color=0x5865F2
            )
            embed_ui.set_image(url="attachment://ui_preview.png")
            embed_ui.set_footer(text="The Webport Union • Official Portal Preview")
            await peeks_ch.send(file=file_ui, embed=embed_ui)
            print("✓ Sent Sneak Peek (Clean UI)", flush=True)

    await client.close()

if __name__ == "__main__":
    client.run(token)
