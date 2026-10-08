import os
import sys
import hashlib
import json
import urllib.request
import urllib.error

PROJECT_NAME = "webport-union"
FOLDER = os.path.dirname(os.path.abspath(__file__))

FILES_TO_DEPLOY = [
    "index.html",
    "favicon.svg",
    "player.html",
    "games.json",
    "vercel.json",
    os.path.join("css", "shadcn.css"),
    os.path.join("js", "shadcn_app.js")
]

def get_token():
    if len(sys.argv) > 1 and sys.argv[1].strip():
        return sys.argv[1].strip()
    env_token = os.environ.get("VERCEL_TOKEN", "").strip()
    if env_token:
        return env_token
    token = input("Enter your Vercel Token (from https://vercel.com/account/tokens): ").strip()
    return token

def sha1_file(path):
    h = hashlib.sha1()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def upload_file(token, rel_path, full_path, sha):
    size = os.path.getsize(full_path)
    url = "https://api.vercel.com/v2/files"
    with open(full_path, "rb") as f:
        data = f.read()

    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/octet-stream",
            "x-vercel-digest": sha,
            "Content-Length": str(size)
        },
        method="POST"
    )
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status in (200, 201)
    except urllib.error.HTTPError as e:
        if e.code == 409:
            return True
        print(f"Error uploading {rel_path}: {e.code} {e.read().decode('utf-8', errors='ignore')}")
        raise

def create_deployment(token, file_metadata):
    url = "https://api.vercel.com/v13/deployments"
    payload = {
        "name": PROJECT_NAME,
        "files": file_metadata,
        "projectSettings": {
            "framework": None
        }
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        },
        method="POST"
    )
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data
    except urllib.error.HTTPError as e:
        err_msg = e.read().decode("utf-8", errors="ignore")
        print(f"Deployment failed: {e.code} {err_msg}")
        return None

def main():
    token = get_token()
    if not token:
        print("Error: No Vercel token provided.")
        print("Get your token at: https://vercel.com/account/tokens")
        sys.exit(1)

    print(f"Preparing deployment for '{PROJECT_NAME}'...")
    file_metadata = []

    for rel_path in FILES_TO_DEPLOY:
        full_path = os.path.join(FOLDER, rel_path)
        if not os.path.exists(full_path):
            print(f"Missing file: {full_path}")
            sys.exit(1)

        sha = sha1_file(full_path)
        size = os.path.getsize(full_path)
        # Normalize forward slashes for Vercel file paths
        vercel_path = rel_path.replace("\\", "/")
        print(f"Uploading {vercel_path} ({size} bytes, sha1={sha[:8]}...)...")
        upload_file(token, rel_path, full_path, sha)
        file_metadata.append({
            "file": vercel_path,
            "sha": sha,
            "size": size,
            "mode": 33188
        })

    print("Creating Vercel deployment...")
    result = create_deployment(token, file_metadata)
    if result:
        deploy_url = result.get("url")
        print("\n" + "=" * 60)
        print("SUCCESS! Nintendo WebAssembly Runtime is hosted live at:")
        print(f"https://{deploy_url}")
        print("=" * 60 + "\n")
    else:
        print("Failed to deploy to Vercel.")

if __name__ == "__main__":
    main()
