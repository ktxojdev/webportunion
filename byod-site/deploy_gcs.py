import os
import sys
import mimetypes
import urllib.request
import urllib.error

FOLDER = os.path.dirname(os.path.abspath(__file__))
FILES_TO_DEPLOY = [
    "index.html",
    "dist/main.js"
]

def upload_gcs(bucket_name, token):
    headers = {
        "Authorization": f"Bearer {token}"
    }

    print(f"Uploading files to Google Cloud Storage bucket: gs://{bucket_name}/...")

    for rel_path in FILES_TO_DEPLOY:
        full_path = os.path.join(FOLDER, rel_path.replace("/", os.sep))
        content_type, _ = mimetypes.guess_type(full_path)
        if not content_type:
            content_type = "application/octet-stream"

        with open(full_path, "rb") as f:
            data = f.read()

        object_name = rel_path.replace("\\", "/")
        upload_url = f"https://storage.googleapis.com/upload/storage/v1/b/{bucket_name}/o?uploadType=media&name={object_name}"

        req = urllib.request.Request(
            upload_url,
            data=data,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": content_type
            },
            method="POST"
        )

        try:
            with urllib.request.urlopen(req) as resp:
                if resp.status in (200, 201):
                    print(f"✓ Uploaded {object_name} -> https://storage.googleapis.com/{bucket_name}/{object_name}")
        except urllib.error.HTTPError as e:
            print(f"✗ Failed uploading {object_name}: {e.code} {e.read().decode('utf-8', errors='ignore')}")
            return False

    print("\n" + "="*60)
    print("SUCCESS! Access your site at:")
    print(f"https://storage.googleapis.com/{bucket_name}/index.html")
    print("="*60 + "\n")
    return True

def main():
    bucket = input("Enter your GCS bucket name: ").strip()
    token = os.environ.get("GCP_ACCESS_TOKEN", "").strip()
    if not token:
        token = input("Enter your GCP OAuth Access Token: ").strip()

    if not bucket or not token:
        print("Bucket name and token are required.")
        sys.exit(1)

    upload_gcs(bucket, token)

if __name__ == "__main__":
    main()
