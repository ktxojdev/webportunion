const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

(async () => {
    const svgPath = path.resolve(__dirname, '..', '..', 'nintendo-web-emu', 'icon.svg');
    const svgContent = fs.readFileSync(svgPath, 'utf8');
    const html = `<!DOCTYPE html><html><body style="margin:0;padding:0;background:transparent;">${svgContent}</body></html>`;

    const browser = await chromium.launch({ headless: true });
    const page = await browser.newPage({ viewport: { width: 512, height: 512 } });
    await page.setContent(html);

    // Save in project folder
    const outJpgProj = path.resolve(__dirname, '..', '..', 'nintendo-web-emu', 'icon.jpg');
    const outPngProj = path.resolve(__dirname, '..', '..', 'nintendo-web-emu', 'icon.png');
    
    // Also save directly on user's Desktop for 1-click convenience
    const desktopJpg = path.resolve('C:\\Users\\ktxoj1\\Desktop', 'webport_icon.jpg');
    const desktopPng = path.resolve('C:\\Users\\ktxoj1\\Desktop', 'webport_icon.png');

    await page.screenshot({ path: outJpgProj, type: 'jpeg', quality: 100 });
    await page.screenshot({ path: outPngProj, type: 'png' });
    await page.screenshot({ path: desktopJpg, type: 'jpeg', quality: 100 });
    await page.screenshot({ path: desktopPng, type: 'png' });

    console.log('[SUCCESS] Successfully created icon.jpg and icon.png on Desktop and in project.');
    await browser.close();
})();
