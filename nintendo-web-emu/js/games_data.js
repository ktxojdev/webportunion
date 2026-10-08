// Nintendo Switch Web Game Library
const NINTENDO_GAMES = [
    {
        id: "sm64",
        title: "Super Mario 64",
        platform: "Nintendo 64",
        badge: "N64",
        type: "emulator",
        core: "n64",
        cover: "https://images.igdb.com/igdb/image/upload/t_cover_big/co20tf.png",
        fallbackBg: "linear-gradient(135deg, #e11d48, #fbbf24)",
        description: "Groundbreaking 3D platformer running via N64 WebAssembly core at 60 FPS."
    },
    {
        id: "oot",
        title: "The Legend of Zelda: OoT",
        platform: "Nintendo 64",
        badge: "N64",
        type: "emulator",
        core: "n64",
        cover: "https://images.igdb.com/igdb/image/upload/t_cover_big/co1x77.png",
        fallbackBg: "linear-gradient(135deg, #15803d, #eab308)",
        description: "The timeless adventure in Hyrule running in high-resolution WebGL 2."
    },
    {
        id: "mk64",
        title: "Mario Kart 64",
        platform: "Nintendo 64",
        badge: "N64",
        type: "emulator",
        core: "n64",
        cover: "https://images.igdb.com/igdb/image/upload/t_cover_big/co204v.png",
        fallbackBg: "linear-gradient(135deg, #2563eb, #dc2626)",
        description: "Classic 4-player kart racing running on WebAssembly hardware pipeline."
    },
    {
        id: "poke-emerald",
        title: "Pokémon Emerald",
        platform: "Game Boy Advance",
        badge: "GBA",
        type: "emulator",
        core: "gba",
        cover: "https://images.igdb.com/igdb/image/upload/t_cover_big/co1yd1.png",
        fallbackBg: "linear-gradient(135deg, #059669, #10b981)",
        description: "Hoenn region adventure running with mGBA WebAssembly core."
    },
    {
        id: "smw",
        title: "Super Mario World",
        platform: "Super Nintendo",
        badge: "SNES",
        type: "emulator",
        core: "snes",
        cover: "https://images.igdb.com/igdb/image/upload/t_cover_big/co1w6k.png",
        fallbackBg: "linear-gradient(135deg, #ea580c, #f59e0b)",
        description: "Classic 16-bit masterpiece running on Snes9x WebAssembly core."
    },
    {
        id: "hnport",
        title: "Hello Neighbor (Alpha 4)",
        platform: "Web Port",
        badge: "WASM",
        type: "workspace",
        url: "/games/hnport/index.html",
        cover: "https://images.igdb.com/igdb/image/upload/t_cover_big/co1x3t.png",
        fallbackBg: "linear-gradient(135deg, #f59e0b, #b45309)",
        description: "Unreal Engine AI & physics decompiled and running natively in WebAssembly."
    },
    {
        id: "gta3",
        title: "Grand Theft Auto III",
        platform: "Web Port",
        badge: "WASM",
        type: "workspace",
        url: "/games/gta3/index.html",
        cover: "https://images.igdb.com/igdb/image/upload/t_cover_big/co1r7v.png",
        fallbackBg: "linear-gradient(135deg, #475569, #1e293b)",
        description: "Liberty City open-world decompilation running in WebGL 2."
    },
    {
        id: "batim",
        title: "Bendy & Ink Machine",
        platform: "Web Port",
        badge: "WASM",
        type: "workspace",
        url: "/games/batim/index.html",
        cover: "https://images.igdb.com/igdb/image/upload/t_cover_big/co1rh9.png",
        fallbackBg: "linear-gradient(135deg, #ca8a04, #713f12)",
        description: "First-person puzzle action game running via Unity WebAssembly."
    },
    {
        id: "cuphead",
        title: "Cuphead",
        platform: "Web Port",
        badge: "WASM",
        type: "workspace",
        url: "/games/cuphead/index.html",
        cover: "https://images.igdb.com/igdb/image/upload/t_cover_big/co1r7h.png",
        fallbackBg: "linear-gradient(135deg, #e11d48, #fbbf24)",
        description: "Classic run and gun action game running in WebAssembly."
    },
    {
        id: "stardew",
        title: "Stardew Valley",
        platform: "Web Port",
        badge: "WASM",
        type: "workspace",
        url: "/games/wasmdotrip/stardewvalley/index.html",
        cover: "https://images.igdb.com/igdb/image/upload/t_cover_big/co1m3b.png",
        fallbackBg: "linear-gradient(135deg, #15803d, #84cc16)",
        description: "Farming RPG running in browser WebAssembly."
    },
    {
        id: "amongus",
        title: "Among Us",
        platform: "Web Port",
        badge: "WASM",
        type: "workspace",
        url: "/games/wasmdotrip/amongus/index.html",
        cover: "https://images.igdb.com/igdb/image/upload/t_cover_big/co2e20.png",
        fallbackBg: "linear-gradient(135deg, #dc2626, #991b1b)",
        description: "Multiplayer social deduction game running in WebAssembly."
    },
    {
        id: "custom",
        title: "+ Insert ROM / Game",
        platform: "Universal Loader",
        badge: "LOAD",
        type: "custom",
        cover: "",
        fallbackBg: "linear-gradient(135deg, #0ab9e6, #ff3c28)",
        description: "Drop any .z64, .n64, .gba, .snes, .nds, .nes, or .zip to play immediately!"
    }
];

window.NINTENDO_GAMES = NINTENDO_GAMES;
