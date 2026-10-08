import os
import sys
import subprocess
import urllib.request
import json
from datetime import datetime

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

WEBHOOK_URL = "https://discord.com/api/webhooks/1557557694347485204/2NgPw7iMjNjIN7cj-Th9DPk8bC7TZcMh0YL8gCXqy-UXGMENTqJWYPxNNQbV9SlCqTqy"
REPO_DIR = os.path.dirname(os.path.abspath(__file__))

def run(cmd):
    res = subprocess.run(cmd, cwd=REPO_DIR, shell=True, capture_output=True, text=True)
    return res.stdout.strip(), res.stderr.strip(), res.returncode

def sync_and_notify():
    commit_msg = sys.argv[1] if len(sys.argv) > 1 else f"chore: automated synchronization {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    
    # 1. Stage and commit
    run("git add -A")
    out, err, code = run(f'git commit -m "{commit_msg}"')
    
    # 2. Get latest commit info
    rev, _, _ = run("git rev-parse --short HEAD")
    author, _, _ = run("git log -1 --pretty=format:%an")
    subject, _, _ = run("git log -1 --pretty=format:%s")
    branch, _, _ = run("git rev-parse --abbrev-ref HEAD")
    files_changed, _, _ = run("git diff-tree --no-commit-id --name-only -r HEAD")

    # 3. Push to remote if configured
    pushed = False
    remotes, _, _ = run("git remote")
    if "origin" in remotes:
        push_out, push_err, push_code = run(f"git push origin {branch}")
        if push_code == 0:
            pushed = True
            print("✓ Pushed to GitHub origin successfully!", flush=True)
        else:
            print(f"! Push warning: {push_err}", flush=True)

    # 4. Notify Discord Webhook
    file_list = files_changed.splitlines()
    file_summary = "\n".join([f"• `{f}`" for f in file_list[:8]])
    if len(file_list) > 8:
        file_summary += f"\n*...and {len(file_list) - 8} more files*"

    embed = {
        "title": f"🔄 Commit [{rev}] on branch `{branch}`",
        "description": f"**Message**: {subject}\n**Author**: `{author}`\n**Pushed to Remote**: {'Yes' if pushed else 'Local Commit'}\n\n**Files Modified:**\n{file_summary}",
        "color": 0x2ecc71 if pushed else 0x3498db,
        "fields": [
            {"name": "Official Domain", "value": "[webportunion.games](https://webportunion.games)", "inline": True},
            {"name": "Permanent Discord", "value": "[discord.gg/4e9ckAw8Fv](https://discord.gg/4e9ckAw8Fv)", "inline": True}
        ],
        "footer": {"text": "The Webport Union • Continuous Synchronization Engine"}
    }

    payload = {
        "content": f"🚀 **New updates synchronized for The Webport Union!**",
        "embeds": [embed]
    }

    req = urllib.request.Request(
        WEBHOOK_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"}
    )
    try:
        with urllib.request.urlopen(req) as resp:
            print(f"✓ Dispatched webhook notification to Discord (status {resp.status})", flush=True)
    except Exception as e:
        print(f"! Webhook error: {e}", flush=True)

if __name__ == "__main__":
    sync_and_notify()

