from pyppeteer import launch


async def screengrab(url):
    browser = await launch({"slowMo": 5}, args=["--no-sandbox"])
    page = await browser.newPage()
    await page.setViewport(
        {"width": 1920, "height": 1080, "deviceScaleFactor": 1}
    )
    await page.goto(url, waitUntil="networkidle2")
    await page.screenshot({"path": "temp.png"})
    await browser.close()
