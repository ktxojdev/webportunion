import os
import re
import json
import asyncio
from typing import Optional

# Webport Union Knowledge Base
KNOWLEDGE_BASE = {
    "domains": [
        "https://webportunion.games (Primary Domain)",
        "https://webport-union.vercel.app (Vercel Edge Mirror)",
        "https://cdn.jsdelivr.net/gh/ktxojdev/webportunion@main/launcher.svg (Permanent jsDelivr Stealth SVG)"
    ],
    "svg_launcher": "https://cdn.jsdelivr.net/gh/ktxojdev/webportunion@main/launcher.svg",
    "github": "https://github.com/ktxojdev/webportunion",
    "discord_invite": "https://discord.gg/4e9ckAw8Fv",
    "staff": {
        "owner": "ktxojdev",
        "admin": "q8j",
        "mod": "turg"
    },
    "byod": (
        "BYOD (Build Your Own Domain) allows members to connect their own domains or use our client-side "
        "router to generate custom, unblockable school mirrors. Access the tool at https://webportunion.games/byod."
    ),
    "isolation": (
        "Multithreaded WebAssembly cores require Cross-Origin Isolation headers: "
        "'Cross-Origin-Opener-Policy: same-origin' and 'Cross-Origin-Embedder-Policy: require-corp'. "
        "These enable SharedArrayBuffer for maximum FPS and multi-core CPU emulation."
    )
}

# System prompt for Gemini AI
SYSTEM_INSTRUCTION = """
You are UnionAI, the official intelligent AI assistant for The Webport Union Discord community.
The Webport Union is a high-precision WebAssembly decompilation, retro emulation, and unblockable web infrastructure platform.

Brand & Aesthetic Guidelines:
- Identity: Minimalist shadcn/ui zinc theme (#09090b background, clean, technical, helpful).
- Tone: Extremely sharp, fast, accurate, developer/hacker friendly, and respectful.
- Owner: ktxojdev
- Administrator: q8j
- Moderator: turg

Core Knowledge:
- Official Domain: https://webportunion.games
- Vercel Mirror: https://webport-union.vercel.app
- Stealth jsDelivr CDN Launcher: https://cdn.jsdelivr.net/gh/ktxojdev/webportunion@main/launcher.svg
  (Uses an SVG image container with Google Drive tab cloaking to evade web filters).
- GitHub Repository: https://github.com/ktxojdev/webportunion
- BYOD: Tool to route custom domains for unblocked school gaming (https://webportunion.games/byod).
- Cross-Origin Isolation: Multithreaded WASM requires COOP: same-origin and COEP: require-corp.
- Support & Tickets: Members can open a ticket in #open-a-ticket or use /ticket. Staff closes it with /close.
- Forum: #your-ports is a post-based discussion forum where members share their custom WASM ports.

When asked about mirrors, web tech, byod, code, or general questions, respond concisely with precise markdown links and instructions.
"""

def get_gemini_client():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return None
    try:
        from google import genai
        return genai.Client(api_key=api_key)
    except Exception:
        return None

async def query_ai(prompt: str) -> str:
    """Answers user questions using Google Gemini if available, or smart knowledge base fallback."""
    client = get_gemini_client()
    
    # 1. Try Google Gemini if key configured
    if client:
        try:
            loop = asyncio.get_running_loop()
            
            def _call():
                for model_name in ["gemini-3.8-flash", "gemini-3.5-flash-lite", "gemini-flash-latest"]:
                    try:
                        resp = client.models.generate_content(
                            model=model_name,
                            contents=prompt,
                            config=dict(
                                system_instruction=SYSTEM_INSTRUCTION,
                                max_output_tokens=800,
                                temperature=0.7
                            )
                        )
                        if resp and resp.text:
                            return resp.text.strip()
                    except Exception:
                        continue
                return None

            result = await loop.run_in_executor(None, _call)
            if result:
                return result
        except Exception:
            pass

    # 2. High-speed Built-in Knowledge Matcher Fallback
    p_lower = prompt.lower()
    
    if any(w in p_lower for w in ["link", "mirror", "domain", "portal", "url", "website"]):
        return (
            "🌐 **The Webport Union Official Link Drops**:\n\n"
            "• **Primary Domain**: `https://webportunion.games`\n"
            "• **Permanent jsDelivr CDN**: `https://cdn.jsdelivr.net/gh/ktxojdev/webportunion@main/launcher.svg`\n"
            "• **Vercel Mirror**: `https://webport-union.vercel.app`\n"
            "• **GitHub Repo**: [github.com/ktxojdev/webportunion](https://github.com/ktxojdev/webportunion)\n"
            "• **Permanent Discord**: [discord.gg/4e9ckAw8Fv](https://discord.gg/4e9ckAw8Fv)\n\n"
            "*(Tip: The jsDelivr `.svg` link evades school filters by serving as an image with Google Drive tab cloaking!)*"
        )
    
    if any(w in p_lower for w in ["svg", "stealth", "cloak", "unblock", "filter", "school"]):
        return (
            "🛡️ **Stealth SVG Filter Evasion Method**:\n\n"
            "We host an interactive vector launcher at:\n"
            "`https://cdn.jsdelivr.net/gh/ktxojdev/webportunion@main/launcher.svg`\n\n"
            "**How it works**:\n"
            "1. Most firewalls allow `.svg` files because they believe it is just an image asset.\n"
            "2. When opened in a browser, the SVG executes an embedded viewport rendering the entire Union site.\n"
            "3. It automatically cloaks the tab title to **'Google Drive'** and replaces the favicon with Google's icon!"
        )

    if any(w in p_lower for w in ["byod", "own domain", "router"]):
        return (
            "💻 **BYOD (Build Your Own Domain)**:\n\n"
            "The BYOD router lets you point any custom domain or sub-domain to The Webport Union to create personal unblocked school mirrors.\n"
            "• Visit: `https://webportunion.games/byod`\n"
            "• Check `#byod-make-links` in Discord for step-by-step walkthroughs."
        )

    if any(w in p_lower for w in ["owner", "admin", "mod", "staff"]):
        return (
            "👥 **The Webport Union Staff**:\n\n"
            "• 👑 **Owner**: `ktxojdev`\n"
            "• 🛠️ **Administrator**: `q8j`\n"
            "• ⚔️ **Moderator**: `turg`\n\n"
            "Need help? Open a ticket in <#1557556942950367332> or ask in `#general`."
        )

    if any(w in p_lower for w in ["ticket", "support", "help", "faq"]):
        return (
            "🎫 **Support & Assistance**:\n\n"
            "• To open a private staff ticket, use `/ticket` or visit <#1557556942950367332> (`#open-a-ticket`).\n"
            "• For common questions, check <#1557556944321908837> (`#faq`).\n"
            "• Staff can close any open ticket channel using `/close`."
        )

    return (
        f"🤖 **UnionAI**: I received your query: *\"{prompt[:100]}\"*\n\n"
        "Here are the quick resources you might need:\n"
        "• 🌐 **Official Site**: `https://webportunion.games`\n"
        "• ⚡ **jsDelivr Stealth Link**: `https://cdn.jsdelivr.net/gh/ktxojdev/webportunion@main/launcher.svg`\n"
        "• 🕹️ **Link Directory**: Type `/portal` or check `#official-links`\n"
        "• 🎫 **Support**: Type `/ticket` to speak with staff."
    )
