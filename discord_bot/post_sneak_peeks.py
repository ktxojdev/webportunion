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

        # Sneak Peek 1: UI & Theater Mode
        img1_path = os.path.join(IMG_DIR, "screenshot.png")
        if os.path.exists(img1_path):
            file1 = discord.File(img1_path, filename="ui_preview.png")
            embed1 = discord.Embed(
                title="🔮 Sneak Peek #01: Minimalist Dark UI & Theater Player",
                description=(
                    "Here's a preview of the upcoming **Webport Union v2 UI** currently in local staging:\n\n"
                    "• **Design System**: Minimalist shadcn/ui zinc tokens with zero bloat.\n"
                    "• **Theater Canvas**: Instant full-screen expansion, reload, and popout windows.\n"
                    "• **Custom ROM Loader**: Direct client-side `.z64`, `.n64`, `.gba` drag-and-drop loading.\n"
                    "• **Instant Search**: Quick fuzzy search with `Ctrl + K` navigation."
                ),
                color=0x5865F2
            )
            embed1.set_image(url="attachment://ui_preview.png")
            embed1.set_footer(text="The Webport Union • Local Staging Preview")
            await peeks_ch.send(file=file1, embed=embed1)
            print("✓ Sent Sneak Peek #01 (UI)", flush=True)
            await asyncio.sleep(1.0)

        # Sneak Peek 2: Featured WebAssembly Ports
        img2_path = os.path.join(IMG_DIR, "cuphead.png")
        if os.path.exists(img2_path):
            file2 = discord.File(img2_path, filename="cuphead.png")
            embed2 = discord.Embed(
                title="☕ Sneak Peek #02: Native WebAssembly Ports In Testing",
                description=(
                    "Currently optimizing and testing genuine WebAssembly browser decompilations:\n\n"
                    "• **Cuphead Web**: Full 60 FPS Canvas/WebGL render loop with gamepad support.\n"
                    "• **Bendy and the Ink Machine (BATIM)**: Dynamic lighting and audio pipeline.\n"
                    "• **MiSide**: Interactive web port with custom touch/keyboard bindings.\n"
                    "• **Persistent Saves**: IndexedDB save slots so your progress is never wiped."
                ),
                color=0xe67e22
            )
            embed2.set_image(url="attachment://cuphead.png")
            embed2.set_footer(text="The Webport Union • Development Testing")
            await peeks_ch.send(file=file2, embed=embed2)
            print("✓ Sent Sneak Peek #02 (Cuphead / BATIM)", flush=True)
            await asyncio.sleep(1.0)

        # Sneak Peek 3: 3D Titles & Retro Cores
        img3_path = os.path.join(IMG_DIR, "gta3.png")
        if os.path.exists(img3_path):
            file3 = discord.File(img3_path, filename="gta3.png")
            embed3 = discord.Embed(
                title="🚗 Sneak Peek #03: 3D Decomps & Retro Emulation",
                description=(
                    "Testing advanced 3D titles and retro core integrations:\n\n"
                    "• **Grand Theft Auto III (re3 Web)**: Native C++ decompilation compiled via Emscripten.\n"
                    "• **Clustertruck Web & Counter-Strike**: High-efficiency WebGL physics.\n"
                    "• **COOP / COEP Memory Isolation**: Running multithreaded WASM SharedArrayBuffers.\n\n"
                    "Stay tuned for the next deployment drop!"
                ),
                color=0x2ecc71
            )
            embed3.set_image(url="attachment://gta3.png")
            embed3.set_footer(text="The Webport Union • Upcoming Deployments")
            await peeks_ch.send(file=file3, embed=embed3)
            print("✓ Sent Sneak Peek #03 (GTA3 / 3D)", flush=True)

    await client.close()

if __name__ == "__main__":
    client.run(token)
