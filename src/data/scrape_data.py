import asyncio
from playwright.async_api import async_playwright, Playwright

async def run(playwright:Playwright):
    chromium = playwright.chromium 
    browser = await chromium.launch(headless=False)
    context = await browser.new_context()
    page = await context.new_page()

    await page.goto("https://www.admissions.hci.edu.sg/faqs")
    div = await page.locator(".col.sqs-col-7.span-7")
    questions = await div.locator("h4").all()
    answers = await div.locator("p").all()
    # print([q.inner_text() for q in questions])
    # print([a.inner_text() for a in answers])
    await page.close()
    await context.close()
    await browser.close()

async def main():
    async with async_playwright() as playwright:
        await run(playwright)

asyncio.run(main())