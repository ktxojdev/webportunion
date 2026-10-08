import os
import sys
import io
import tarfile
import hashlib
import base64
import json
import urllib.request
import urllib.error

FOLDER = os.path.dirname(os.path.abspath(__file__))
PACKAGE_NAME = "byod-domain-router"
VERSION = "1.0.0"

FILES = [
    "package.json",
    "index.html",
    "dist/main.js",
    "src/main.ts",
    "README.md"
]

def make_tarball():
    tar_buf = io.BytesIO()
    with tarfile.open(fileobj=tar_buf, mode="w:gz") as tar:
        for rel_path in FILES:
            full_path = os.path.join(FOLDER, rel_path.replace("/", os.sep))
            if os.path.exists(full_path):
                # npm packages must have 'package/' prefix inside the tarball
                arcname = f"package/{rel_path}"
                tar.add(full_path, arcname=arcname)
    tar_bytes = tar_buf.getvalue()
    return tar_bytes

def publish(token):
    tar_bytes = make_tarball()
    shasum = hashlib.sha1(tar_bytes).hexdigest()
    integrity = "sha512-" + base64.b64encode(hashlib.sha512(tar_bytes).digest()).decode("utf-8")
    b64_data = base64.b64encode(tar_bytes).decode("utf-8")

    pkg_json_path = os.path.join(FOLDER, "package.json")
    with open(pkg_json_path, "r", encoding="utf-8") as f:
        pkg_data = json.load(f)

    tarball_filename = f"{PACKAGE_NAME}-{VERSION}.tgz"

    payload = {
        "_id": PACKAGE_NAME,
        "name": PACKAGE_NAME,
        "description": pkg_data.get("description", ""),
        "dist-tags": {
            "latest": VERSION
        },
        "versions": {
            VERSION: {
                "name": PACKAGE_NAME,
                "version": VERSION,
                "description": pkg_data.get("description", ""),
                "main": pkg_data.get("main", "dist/main.js"),
                "readme": open(os.path.join(FOLDER, "README.md"), "r", encoding="utf-8").read(),
                "dist": {
                    "shasum": shasum,
                    "integrity": integrity,
                    "tarball": f"https://registry.npmjs.org/{PACKAGE_NAME}/-/{tarball_filename}"
                }
            }
        },
        "_attachments": {
            tarball_filename: {
                "content_type": "application/octet-stream",
                "data": b64_data,
                "length": len(tar_bytes)
            }
        }
    }

    url = f"https://registry.npmjs.org/{PACKAGE_NAME}"
    req_data = json.dumps(payload).encode("utf-8")

    req = urllib.request.Request(
        url,
        data=req_data,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        },
        method="PUT"
    )

    print(f"Publishing '{PACKAGE_NAME}@{VERSION}' directly to npm registry...")
    try:
        with urllib.request.urlopen(req) as resp:
            if resp.status in (200, 201):
                print("\n" + "="*60)
                print(f"SUCCESS! Published to npm!")
                print(f"jsDelivr CDN link is now live at:")
                print(f"https://cdn.jsdelivr.net/npm/{PACKAGE_NAME}@{VERSION}/index.html")
                print(f"https://cdn.jsdelivr.net/npm/{PACKAGE_NAME}@{VERSION}/dist/main.js")
                print("="*60 + "\n")
                return True
    except urllib.error.HTTPError as e:
        err = e.read().decode("utf-8", errors="ignore")
        print(f"Failed to publish to npm: {e.code} {err}")
        return False

def main():
    if len(sys.argv) > 1 and sys.argv[1].strip():
        token = sys.argv[1].strip()
    else:
        token = input("Enter your npm Access Token (from https://www.npmjs.com -> Access Tokens): ").strip()

    if not token:
        print("Error: npm token is required.")
        sys.exit(1)

    publish(token)

if __name__ == "__main__":
    main()
