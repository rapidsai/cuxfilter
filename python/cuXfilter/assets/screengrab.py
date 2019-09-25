import asyncio
from pyppeteer import launch

async def screengrab(url):
    browser = await launch()
    page = await browser.newPage()
    await page.setViewport({
        'width': 1600,
        'height': 900,
        'deviceScaleFactor': 1,
    })
    await page.goto(url, waitUntil='networkidle2')
    await page.screenshot({'path': 'temp.png'})
    await browser.close()

# async def screengrab(url):
#     print('screen grab started')
    
#     print('screen grabbed')


# def screengrab(url):
#     import os
#     script = 'node ./assets/js/index.js '+url
#     print(script)
#     os.system("bash -c '%s'" % script)
