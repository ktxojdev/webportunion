// Nintendo Switch Web Runtime - Handheld Controller & Launcher
document.addEventListener("DOMContentLoaded", () => {
    // 1. Clock Updater
    function updateClock() {
        const now = new Date();
        const hrs = String(now.getHours()).padStart(2, '0');
        const mins = String(now.getMinutes()).padStart(2, '0');
        const clockEl = document.getElementById("system-clock");
        if (clockEl) clockEl.textContent = `${hrs}:${mins}`;
    }
    setInterval(updateClock, 1000);
    updateClock();

    // 2. Sound Effects
    let soundEnabled = false;
    function playAudio(soundFn) {
        if (!soundEnabled) {
            window.nintendoAudio.init();
            soundEnabled = true;
        }
        try {
            soundFn();
        } catch (e) {}
    }

    window.addEventListener("click", () => {
        if (!soundEnabled) {
            playAudio(() => window.nintendoAudio.playSnap());
            soundEnabled = true;
        }
    }, { once: true });

    // 3. Elements
    const carouselEl = document.getElementById("game-carousel");
    const bannerTitle = document.getElementById("banner-title");
    const bannerPlatform = document.getElementById("banner-platform");
    const homeView = document.getElementById("home-menu-view");
    const gameView = document.getElementById("active-game-view");
    const gameFrame = document.getElementById("active-game-frame");
    const currentGameTitle = document.getElementById("current-game-title");
    const btnHome = document.getElementById("btn-home");
    const btnFullscreen = document.getElementById("btn-fullscreen");
    const btnRestart = document.getElementById("btn-restart");

    let selectedIndex = 0;
    const cards = [];

    // 4. Populate Game Carousel
    NINTENDO_GAMES.forEach((game, idx) => {
        const card = document.createElement("div");
        card.className = "game-card" + (idx === 0 ? " selected" : "");
        card.dataset.index = idx;

        const badgeClass = `badge-${game.badge.toLowerCase()}`;
        
        card.innerHTML = `
            <div class="game-badge ${badgeClass}">${game.badge}</div>
            <div class="game-card-cover" style="background-image: url('${game.cover}'), ${game.fallbackBg};"></div>
            <div class="game-card-footer">
                <div class="game-name">${game.title}</div>
                <div class="game-sub">${game.platform}</div>
            </div>
        `;

        card.addEventListener("click", () => {
            if (selectedIndex === idx) {
                launchGame(game);
            } else {
                selectGame(idx);
            }
        });

        carouselEl.appendChild(card);
        cards.push(card);
    });

    function selectGame(idx) {
        if (idx < 0) idx = 0;
        if (idx >= NINTENDO_GAMES.length) idx = NINTENDO_GAMES.length - 1;

        cards.forEach(c => c.classList.remove("selected"));
        cards[idx].classList.add("selected");
        cards[idx].scrollIntoView({ behavior: "smooth", block: "nearest", inline: "center" });

        selectedIndex = idx;
        const g = NINTENDO_GAMES[idx];
        bannerTitle.textContent = g.title;
        bannerPlatform.textContent = g.platform;

        playAudio(() => window.nintendoAudio.playClick());
    }

    function launchGame(game) {
        playAudio(() => window.nintendoAudio.playSelect());

        homeView.style.display = "none";
        gameView.style.display = "flex";
        currentGameTitle.textContent = game.title;

        let targetUrl = "";
        if (game.type === "workspace") {
            targetUrl = game.url;
        } else if (game.type === "custom") {
            targetUrl = `player.html?type=custom`;
        } else {
            targetUrl = `player.html?type=emulator&core=${game.core}`;
        }

        gameFrame.src = targetUrl;
        gameFrame.focus();
    }

    function exitToHome() {
        playAudio(() => window.nintendoAudio.playBack());
        gameFrame.src = "about:blank";
        gameView.style.display = "none";
        homeView.style.display = "flex";
    }

    // Controls
    btnHome.addEventListener("click", exitToHome);
    
    btnFullscreen.addEventListener("click", () => {
        if (!document.fullscreenElement) {
            document.documentElement.requestFullscreen().catch(() => {});
        } else {
            document.exitFullscreen().catch(() => {});
        }
    });

    btnRestart.addEventListener("click", () => {
        if (gameView.style.display === "flex") {
            const currentSrc = gameFrame.src;
            gameFrame.src = "about:blank";
            setTimeout(() => { gameFrame.src = currentSrc; }, 100);
        }
    });

    // Hardware Joy-Con Button Click Handlers
    document.getElementById("joycon-home-btn").addEventListener("click", exitToHome);
    document.getElementById("btn-joy-a").addEventListener("click", () => {
        if (homeView.style.display !== "none") {
            launchGame(NINTENDO_GAMES[selectedIndex]);
        }
    });
    document.getElementById("btn-joy-b").addEventListener("click", () => {
        if (gameView.style.display !== "none") {
            exitToHome();
        }
    });
    document.getElementById("dpad-left").addEventListener("click", () => selectGame(selectedIndex - 1));
    document.getElementById("dpad-right").addEventListener("click", () => selectGame(selectedIndex + 1));

    // Keyboard Navigation
    window.addEventListener("keydown", (e) => {
        if (homeView.style.display !== "none") {
            if (e.key === "ArrowLeft" || e.key === "a" || e.key === "A") {
                selectGame(selectedIndex - 1);
            } else if (e.key === "ArrowRight" || e.key === "d" || e.key === "D") {
                selectGame(selectedIndex + 1);
            } else if (e.key === "Enter" || e.key === " " || e.key === "z" || e.key === "Z") {
                launchGame(NINTENDO_GAMES[selectedIndex]);
            }
        } else {
            if (e.key === "Escape") {
                exitToHome();
            }
        }
    });

    // Select initial game
    selectGame(0);
});
