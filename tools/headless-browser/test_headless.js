const { chromium } = require('playwright');

(async () => {
    // Launch purely in headless mode (no window, no mouse disruption, runs in RAM)
    const browser = await chromium.launch({ headless: true });
    const page = await browser.newPage();
    
    await page.goto('https://nintendo-web-emu.vercel.app');
    const title = await page.title();
    console.log(`[SUCCESS] Headless browser verified. Page title: "${title}"`);
    
    await browser.close();
})();
