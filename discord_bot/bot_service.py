import os
import sys
import asyncio
from datetime import datetime
from dotenv import load_dotenv
import discord
from discord import app_commands
from discord.ext import commands
import re
from ai_assistant import query_ai

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
token = os.getenv("DISCORD_BOT_TOKEN")
guild_id = int(os.getenv("DISCORD_GUILD_ID", 0))

intents = discord.Intents.default()
intents.members = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ----------------- TICKETING UI VIEWS -----------------

class TicketActionView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Close Ticket", style=discord.ButtonStyle.danger, emoji="🔒", custom_id="persistent_close_ticket")
    async def close_ticket_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("🔒 **Ticket closed. Deleting channel now...**")
        
        # Log to mod-logs if channel exists
        try:
            mod_logs = discord.utils.get(interaction.guild.text_channels, name="📋・mod-logs")
            if mod_logs:
                embed = discord.Embed(
                    title="🎫 Ticket Closed",
                    description=f"Ticket **{interaction.channel.name}** closed by {interaction.user.mention}.",
                    color=0xe74c3c,
                    timestamp=datetime.now()
                )
                await mod_logs.send(embed=embed)
        except Exception:
            pass

        await asyncio.sleep(2)
        try:
            await interaction.channel.delete(reason=f"Ticket closed by {interaction.user}")
        except Exception as e:
            print(f"! Error deleting ticket channel: {e}", flush=True)

class TicketLaunchView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Open a Ticket", style=discord.ButtonStyle.primary, emoji="📩", custom_id="persistent_open_ticket")
    async def open_ticket_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        user = interaction.user

        clean_name = "".join(c for c in user.name.lower() if c.isalnum() or c in "-_")
        target_name = f"ticket-{clean_name}"

        # 1. Check if user already has an active ticket
        for ch in guild.text_channels:
            if ch.name == target_name:
                await interaction.response.send_message(
                    f"⚠️ You already have an open ticket: {ch.mention}", 
                    ephemeral=True
                )
                return

        await interaction.response.defer(ephemeral=True)

        # 2. Support Category
        support_cat = discord.utils.get(guild.categories, name="🎫・SUPPORT")

        # 3. Build Permission Overwrites
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            user: discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                read_message_history=True,
                attach_files=True,
                embed_links=True
            ),
            guild.me: discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                manage_channels=True,
                read_message_history=True
            )
        }

        # Add staff permissions
        for role_name in ["👑 Owner", "⚡ Co-Owner", "Administrator", "⚔️ Moderator"]:
            r = discord.utils.get(guild.roles, name=role_name)
            if r:
                overwrites[r] = discord.PermissionOverwrite(
                    view_channel=True,
                    send_messages=True,
                    read_message_history=True,
                    manage_messages=True
                )

        # 4. Create the private ticket channel
        try:
            ticket_ch = await guild.create_text_channel(
                name=target_name,
                category=support_cat,
                overwrites=overwrites,
                topic=f"Support ticket for {user} ({user.id}) | Created {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            )
        except Exception as e:
            await interaction.followup.send(f"❌ Failed to create ticket: {e}", ephemeral=True)
            return

        # 5. Send initial welcome inside ticket
        ticket_embed = discord.Embed(
            title=f"🎫 Support Ticket — {user.display_name}",
            description=(
                f"Welcome {user.mention}!\n\n"
                "A staff member will assist you shortly.\n"
                "**Please explain your question or issue in detail:**\n"
                "• Broken link or unblocked mirror report\n"
                "• Webport / WASM technical question\n"
                "• General server support or report\n\n"
                "Click the red button below when finished to close this ticket."
            ),
            color=0x2ecc71
        )
        ticket_embed.set_thumbnail(url=user.display_avatar.url if user.display_avatar else guild.icon.url)
        ticket_embed.set_footer(text="The Webport Union Help Desk • Click below to close")

        await ticket_ch.send(
            content=f"{user.mention} Staff has been notified!", 
            embed=ticket_embed, 
            view=TicketActionView()
        )

        # 6. Reply to user
        await interaction.followup.send(
            f"✅ Your ticket has been created: {ticket_ch.mention}", 
            ephemeral=True
        )
        print(f"[TICKET] Created {ticket_ch.name} for {user.name}", flush=True)

# ----------------- BOT EVENTS -----------------

@bot.event
async def on_ready():
    print(f"\n==========================================", flush=True)
    print(f"The Webport Union Bot Online: {bot.user}", flush=True)
    print(f"Monitoring Guild ID: {guild_id}", flush=True)
    print(f"==========================================\n", flush=True)

    # 1. Register persistent views
    bot.add_view(TicketLaunchView())
    bot.add_view(TicketActionView())

    # 2. Ensure Ticket Panel exists in 📩・open-a-ticket
    guild = bot.get_guild(guild_id)
    if guild:
        ticket_panel_ch = discord.utils.get(guild.text_channels, name="📩・open-a-ticket")
        if ticket_panel_ch:
            # Check if panel message already posted
            has_panel = False
            async for msg in ticket_panel_ch.history(limit=5):
                if msg.author == bot.user and msg.components:
                    has_panel = True
                    break

            if not has_panel:
                async for m in ticket_panel_ch.history(limit=10):
                    await m.delete()

                panel_embed = discord.Embed(
                    title="📩 The Webport Union — Support & Help Desk",
                    description=(
                        "Need help with a web port, BYOD mirror, broken link, or general support?\n\n"
                        "Click the button below to open a private ticket with our staff.\n\n"
                        "**Ticket Guidelines:**\n"
                        "• Please be patient — staff will reply as soon as possible.\n"
                        "• Provide full details, errors, or screenshots right away.\n"
                        "• One open ticket per member at a time."
                    ),
                    color=0x5865F2
                )
                panel_embed.set_footer(text="The Webport Union • 24/7 Support Desk")
                await ticket_panel_ch.send(embed=panel_embed, view=TicketLaunchView())
                print("✓ Posted persistent Ticket Panel in #open-a-ticket!", flush=True)

    # 3. Sync Slash Commands
    try:
        guild_obj = discord.Object(id=guild_id)
        bot.tree.copy_global_to(guild=guild_obj)
        synced = await bot.tree.sync(guild=guild_obj)
        print(f"✓ Synchronized {len(synced)} Slash Commands to guild!", flush=True)
    except Exception as e:
        print(f"! Error syncing slash commands: {e}", flush=True)

@bot.event
async def on_member_join(member: discord.Member):
    if member.guild.id != guild_id:
        return
    
    welcome_ch = discord.utils.get(member.guild.text_channels, name="👋・welcome")
    if not welcome_ch:
        return

    embed = discord.Embed(
        title="👋 Welcome to The Webport Union!",
        description=(
            f"Hey {member.mention}, welcome to the community!\n\n"
            f"• **Member Count**: You are member **#{member.guild.member_count}**\n"
            f"• **Step 1**: Head to <#1557546295504273458> (`verification`) to unlock games & chat!\n"
            f"• **Step 2**: Review <#1557554336048091219> (`rules`) to stay safe.\n"
            f"• **Step 3**: Grab unblocked web ports in <#1557554341991419944> (`official-links`).\n\n"
            f"🌐 **Official Domain**: [webportunion.games](https://webportunion.games)"
        ),
        color=0x2ecc71
    )
    if member.display_avatar:
        embed.set_thumbnail(url=member.display_avatar.url)
    embed.set_footer(text="The Webport Union • Continuous Network", icon_url=member.guild.icon.url if member.guild.icon else None)

    try:
        await welcome_ch.send(content=f"Welcome {member.mention}! 🎉", embed=embed)
        print(f"[JOIN] Welcomed {member.name} ({member.id})", flush=True)
    except Exception as e:
        print(f"! Error sending welcome: {e}", flush=True)

# ----------------- SLASH COMMANDS -----------------

@bot.tree.command(name="portal", description="Get full unblocked link drops, mirrors, and game endpoints")
async def slash_portal(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🌐 The Webport Union — Link Drops & Mirrors",
        description="Official permanent mirrors, stealth `.svg` CDN endpoints, and direct game link drops.\n*Bookmark and copy these links for unblocked access.*",
        color=0x2ecc71
    )
    embed.add_field(
        name="🟢 Primary Domains & Mirrors",
        value=(
            "• `https://webportunion.games`\n"
            "• `https://webport-union.vercel.app`\n"
            "• `https://webportunion.games/launcher.svg` (Google Drive Cloak)\n"
            "• `https://webportunion.games/player.html` (Retro Core Player)"
        ),
        inline=False
    )
    embed.add_field(
        name="⚡ Permanent jsDelivr CDN Links (.svg Stealth)",
        value=(
            "• `https://cdn.jsdelivr.net/gh/ktxojdev/webportunion@main/launcher.svg`\n"
            "• `https://cdn.jsdelivr.net/gh/ktxojdev/dr-langeskov-webport@main/index.html`\n"
            "• `https://github.com/ktxojdev/webportunion` (Full Source)"
        ),
        inline=False
    )
    embed.add_field(
        name="🎮 Webport Union Platform",
        value=(
            "• **Clean Minimalist Portal**: `https://webportunion.games`\n"
            "• **Stealth SVG Launcher**: `https://cdn.jsdelivr.net/gh/ktxojdev/webportunion@main/launcher.svg`\n"
            "• **Vercel Edge Mirror**: `https://webport-union.vercel.app`"
        ),
        inline=False
    )
    embed.add_field(
        name="💻 BYOD Tools & Community",
        value=(
            "• **BYOD Site Tool**: `https://webportunion.games/byod`\n"
            "• **Permanent Discord**: `https://discord.gg/4e9ckAw8Fv`"
        ),
        inline=False
    )
    embed.set_footer(text="The Webport Union • Unblocked WebAssembly Infrastructure")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="links", description="Get full link drops for all game ports and mirrors")
async def slash_links(interaction: discord.Interaction):
    await slash_portal.callback(interaction)

@bot.tree.command(name="rules", description="View The Webport Union server rules")
async def slash_rules(interaction: discord.Interaction):
    embed = discord.Embed(
        title="📜 The Webport Union Rules",
        description=(
            "1. **Respect & Decorum**: Zero toxicity, hate speech, or harassment.\n"
            "2. **Authentic Ports Only**: Only verified WebAssembly and web ports. No scams or malware.\n"
            "3. **Channel Cleanliness**: Keep discussions in their appropriate categories.\n"
            "4. **No Advertising**: Keep self-promo in `🤝・partners` only."
        ),
        color=0x3498db
    )
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="close", description="Close and delete the current support ticket")
async def slash_close(interaction: discord.Interaction):
    if not interaction.channel.name.startswith("ticket-"):
        await interaction.response.send_message("❌ This command can only be used inside a ticket channel!", ephemeral=True)
        return
    await interaction.response.send_message("🔒 **Ticket closed. Deleting channel now...**")
    await asyncio.sleep(2)
    try:
        await interaction.channel.delete(reason=f"Ticket closed by {interaction.user}")
    except Exception as e:
        print(f"! Error deleting ticket channel: {e}", flush=True)

@bot.tree.command(name="ask", description="Ask UnionAI any question about games, mirrors, porting, or code")
@app_commands.describe(question="Your question or prompt for UnionAI")
async def slash_ask(interaction: discord.Interaction, question: str):
    await interaction.response.defer(thinking=True)
    ans = await query_ai(question)
    embed = discord.Embed(
        title="🤖 UnionAI Response",
        description=ans[:4000],
        color=0x2ecc71
    )
    embed.set_footer(text=f"Requested by {interaction.user.display_name} • The Webport Union")
    await interaction.followup.send(embed=embed)

@bot.tree.command(name="ai", description="Chat with UnionAI assistant")
@app_commands.describe(prompt="Your prompt or question")
async def slash_ai(interaction: discord.Interaction, prompt: str):
    await slash_ask.callback(interaction, prompt)

@bot.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return
    # If the bot is pinged/mentioned directly
    if bot.user in message.mentions:
        clean_text = re.sub(r'<@!?[0-9]+>', '', message.content).strip()
        if not clean_text:
            await message.reply("Hey! I'm **UnionAI**. Ask me anything with `/ask <question>` or just mention me here!")
            return
        async with message.channel.typing():
            ans = await query_ai(clean_text)
            # Split if exceeds 2000 characters
            if len(ans) > 2000:
                parts = [ans[i:i+1900] for i in range(0, len(ans), 1900)]
                for p in parts:
                    await message.reply(p)
            else:
                await message.reply(ans)
    await bot.process_commands(message)

if __name__ == "__main__":
    bot.run(token)
