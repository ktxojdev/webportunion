# Bring Your OWN Domain! - TypeScript Site & Deployment Suite

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

This directory contains the complete source code, TypeScript configuration, and automated deployment scripts to host your site across **Vercel**, **Google Cloud Storage (GCS)**, and **jsDelivr**.

---

## 📁 Project Structure

- `index.html` - Sleek, responsive landing page with setup instructions and live DNS tester.
- `src/main.ts` - TypeScript source code handling copy actions and live Cloudflare DNS-over-HTTPS querying.
- `dist/main.js` - Pre-compiled browser-compatible JavaScript (runs with zero dependencies).
- `tsconfig.json` - TypeScript configuration.
- `run_local.bat` - Double-click to instantly preview the site on `http://localhost:8080`.
- `deploy_vercel.py` - Automated zero-dependency Python script to deploy directly to Vercel.
- `deploy_gcs.py` - Python script to upload assets to any Google Cloud Storage bucket.
- `push_to_github_for_jsdelivr.bat` - Automates committing and pushing to GitHub so it serves over `cdn.jsdelivr.net`.

---

## 🚀 How to Run & Deploy

### 1. Test Locally
Run in terminal:
```bash
python -m http.server 8080
```
Then visit `http://localhost:8080`.

---

### 2. Deploy to Vercel
Run:
```bash
python deploy_vercel.py
```
Paste your Vercel Token (from [vercel.com/account/tokens](https://vercel.com/account/tokens)), and it will upload all files directly and output your live `.vercel.app` URL.

---

### 3. Serve via jsDelivr CDN
jsDelivr mirrors files directly from public GitHub repositories:
1. Run deployment helper or push directly via git.
2. Enter your GitHub repo URL.
3. Access your files instantly through:
   ```text
   https://cdn.jsdelivr.net/gh/<username>/<repo>@main/index.html
   https://cdn.jsdelivr.net/gh/<username>/<repo>@main/dist/main.js
   ```

---

### 4. Deploy to Google Cloud Storage
Run:
```bash
python deploy_gcs.py
```
Enter your bucket name and access token.

---

## 🌐 Custom Domain Setup (`159.195.17.92`)
In your domain registrar's DNS panel:
- **Type**: `A`
- **Name**: `@` (or subdomain)
- **Target / Value**: `159.195.17.92`
- Wait ~15 minutes for global DNS propagation, then test using the built-in DNS checker tool on the page!

---

## 📄 License

This project is open-source under the [MIT License](../LICENSE).
