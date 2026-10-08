// The Webport Union — Minimalist Games Controller
document.addEventListener("DOMContentLoaded", async () => {
    let allGames = [];
    let searchQuery = "";

    const grid = document.getElementById("game-grid");
    const countDisplay = document.getElementById("game-count-display");
    const searchInput = document.getElementById("search-input");
    
    // Player Modal Elements
    const playerModal = document.getElementById("player-modal");
    const playerFrame = document.getElementById("player-iframe");
    const playerTitle = document.getElementById("player-title");
    const btnClosePlayer = document.getElementById("btn-close-player");
    const btnFullscreen = document.getElementById("btn-player-fullscreen");
    const btnReload = document.getElementById("btn-player-reload");
    const btnPopout = document.getElementById("btn-player-popout");

    // ROM Dialog Elements
    const romDialog = document.getElementById("rom-dialog");
    const btnOpenRom = document.getElementById("btn-open-rom");
    const btnCloseRom = document.getElementById("btn-close-rom");
    const dropzone = document.getElementById("rom-dropzone");
    const romFileInput = document.getElementById("rom-file-input");

    // 1. Fetch games data
    try {
        const resp = await fetch("/games.json");
        const jsonGames = await resp.json();
        allGames = jsonGames || [];
    } catch (err) {
        console.error("Failed to load games.json", err);
    }

    // 2. Render Cards
    function render() {
        grid.innerHTML = "";

        const filtered = allGames.filter(game => {
            if (!searchQuery) return true;
            return game.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                   (game.porter && game.porter.toLowerCase().includes(searchQuery.toLowerCase()));
        });

        countDisplay.textContent = `${filtered.length} ports available`;

        if (filtered.length === 0) {
            grid.innerHTML = searchQuery 
                ? `<div class="empty-state">No ports found matching "${searchQuery}"</div>`
                : `<div class="empty-state">No ports currently active.</div>`;
            return;
        }

        filtered.forEach(game => {
            const card = document.createElement("div");
            card.className = "card";

            const imgSrc = game.imageUrl || "img/screenshot.png";
            const featuredBadge = game.featured ? `<div class="card-badge badge-featured">Featured</div>` : "";
            const porterName = game.porter ? `by ${game.porter}` : "";

            card.innerHTML = `
                <div class="card-image-wrap">
                    <img class="card-img" src="${imgSrc}" alt="${game.name}" loading="lazy" onerror="this.src='img/screenshot.png'">
                    ${featuredBadge}
                </div>
                <div class="card-content">
                    <div class="card-title" title="${game.name}">${game.name}</div>
                    <div class="card-meta">
                        <span>${porterName}</span>
                    </div>
                    <div class="card-actions">
                        <button class="btn btn-primary btn-sm btn-play" style="width: 100%;">Play</button>
                    </div>
                </div>
            `;

            const handlePlay = (e) => {
                e.stopPropagation();
                if (game.isEmulator) {
                    openRomDialog();
                } else {
                    launchGame(game);
                }
            };

            card.addEventListener("click", handlePlay);
            card.querySelector(".btn-play").addEventListener("click", handlePlay);

            grid.appendChild(card);
        });
    }

    // 3. Launch in Theater Player
    function launchGame(game) {
        playerTitle.textContent = game.name;
        playerFrame.src = game.gameUrl;
        playerModal.style.display = "flex";
        document.body.style.overflow = "hidden";
    }

    function closePlayer() {
        playerFrame.src = "about:blank";
        playerModal.style.display = "none";
        document.body.style.overflow = "auto";
    }

    btnClosePlayer.addEventListener("click", closePlayer);

    btnFullscreen.addEventListener("click", () => {
        if (!document.fullscreenElement) {
            playerModal.requestFullscreen().catch(() => {});
        } else {
            document.exitFullscreen().catch(() => {});
        }
    });

    btnReload.addEventListener("click", () => {
        const cur = playerFrame.src;
        playerFrame.src = "about:blank";
        setTimeout(() => playerFrame.src = cur, 80);
    });

    btnPopout.addEventListener("click", () => {
        if (playerFrame.src && playerFrame.src !== "about:blank") {
            window.open(playerFrame.src, "_blank");
        }
    });

    // 4. ROM Dialog
    function openRomDialog() {
        romDialog.style.display = "flex";
    }

    function closeRomDialog() {
        romDialog.style.display = "none";
    }

    btnOpenRom.addEventListener("click", openRomDialog);
    btnCloseRom.addEventListener("click", closeRomDialog);
    romDialog.addEventListener("click", (e) => {
        if (e.target === romDialog) closeRomDialog();
    });

    dropzone.addEventListener("click", () => romFileInput.click());
    dropzone.addEventListener("dragover", (e) => {
        e.preventDefault();
        dropzone.classList.add("dragover");
    });
    dropzone.addEventListener("dragleave", () => dropzone.classList.remove("dragover"));
    dropzone.addEventListener("drop", (e) => {
        e.preventDefault();
        dropzone.classList.remove("dragover");
        if (e.dataTransfer.files.length > 0) {
            handleCustomRom(e.dataTransfer.files[0]);
        }
    });

    romFileInput.addEventListener("change", (e) => {
        if (e.target.files.length > 0) {
            handleCustomRom(e.target.files[0]);
        }
    });

    function handleCustomRom(file) {
        closeRomDialog();
        const ext = file.name.split('.').pop().toLowerCase();
        let core = "n64";
        if (ext === "gba") core = "gba";
        else if (ext === "snes" || ext === "smc") core = "snes";
        else if (ext === "nds") core = "nds";
        else if (ext === "nes") core = "nes";

        const fileUrl = URL.createObjectURL(file);
        launchGame({
            name: file.name,
            porter: `Local ${core.toUpperCase()} ROM`,
            gameUrl: `player.html?core=${core}&rom=${encodeURIComponent(fileUrl)}`
        });
    }

    // 5. Search
    searchInput.addEventListener("input", (e) => {
        searchQuery = e.target.value.trim();
        render();
    });

    // Keyboard Shortcuts
    window.addEventListener("keydown", (e) => {
        if (e.key === "Escape") {
            if (romDialog.style.display === "flex") {
                closeRomDialog();
            } else if (playerModal.style.display === "flex") {
                closePlayer();
            }
        }
        if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "k") {
            e.preventDefault();
            searchInput.focus();
        }
    });

    render();
});
