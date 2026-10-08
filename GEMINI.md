# Precision-Static / The Webport Union Guidelines

## Project Identity & Architecture
- **Site Name**: The Webport Union
- **Design System**: Minimalist shadcn/ui dark zinc tokens (`#09090b` background, `#27272a` borders, `#fafafa` foreground).
- **Icons**: Always use high-precision vector SVG assets for brand identity and favicons (`favicon.svg`). Never use text initials or emojis.

## Port Quality & CDN Standards
- Only genuine WebAssembly decompilations, ports, and retro emulation cores. Zero AI mocks.
- Prohibit `raw.githack.com`. Use local assets or live jsDelivr CDN endpoints (`https://cdn.jsdelivr.net/gh/wasmdotrip/wasm.rip@main/files/...`).
- Ensure every port supports 1-click jsDelivr link extraction.

## Hosting & Headers
- Localhost development runs on port 3000.
- Cross-Origin Isolation (`Cross-Origin-Opener-Policy: same-origin`, `Cross-Origin-Embedder-Policy: require-corp`) is mandatory for WebAssembly shared memory.
