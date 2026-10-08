# The Webport Union

> High-precision WebAssembly decompilations, retro emulation cores, and unblockable web infrastructure.

---

## 🌐 Ecosystem & Live Deployments

- **Production Portal**: [webport-union.vercel.app](https://webport-union.vercel.app)
- **Permanent CDN Mirror**: `https://cdn.jsdelivr.net/gh/wasmdotrip/wasm.rip@main/`
- **Discord Community**: The Webport Union (`1557545995271807016`)

---

## 🏛️ Architecture & Projects

| Project | Type | Description |
| :--- | :--- | :--- |
| **`nintendo-web-emu`** | Retro Emulation | N64 & Nintendo WebAssembly emulation core with shadcn/ui dark tokens. |
| **`GTA3Web` / `GTA3Web-Vercel`** | WASM Decompilation | Native Grand Theft Auto III re3 WebAssembly browser port with audio/WebGL. |
| **`byod-site`** | Domain Router | Build Your Own Domain generator for client-side DNS routing and mirror creation. |
| **`haven-os`** | Web OS | Unblocked browser desktop environment. |
| **`Blobwifi`** | Proxy / Tunnel | Lightweight web proxy tunnel interface. |
| **`amethyst-mirror`** | Web Mirror | Mirror and game asset CDN proxy. |
| **`discord_bot`** | Automation | Administrative Discord controller managing server hierarchy, roles, and channels. |

---

## 🔒 Security & Performance Headers

All multithreaded WebAssembly cores and SharedArrayBuffer modules require strict Cross-Origin Isolation headers:
```json
{
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        { "key": "Cross-Origin-Opener-Policy", "value": "same-origin" },
        { "key": "Cross-Origin-Embedder-Policy", "value": "require-corp" }
      ]
    }
  ]
}
```

---

## 🤖 Discord Integration & Sync

The Discord server is automated via `discord_bot/controller.py`:
- **Verification Gates**: Automatically locks community & proxy links behind the `@Member` role.
- **Port Requests & Help**: Dedicated channels (`#port-requests`, `#porting-help`, `#your-ports`) for collaborative WebAssembly port development.
- **Commit Notifications**: Direct synchronization channel (`#github-commits`) for repository updates.
