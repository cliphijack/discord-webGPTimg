"""
1회 실행: 브라우저 열고 ChatGPT 로그인 → 세션 저장
이후 generate.py에서 세션 재사용
"""
import asyncio
from patchright.async_api import async_playwright

SESSION_FILE = "session.json"

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=500)
        ctx = await browser.new_context()
        page = await ctx.new_page()

        print("ChatGPT 열기...")
        await page.goto("https://chatgpt.com/")
        print("로그인 완료 후 Enter 누르세요.")
        input()

        await ctx.storage_state(path=SESSION_FILE)
        print(f"세션 저장 완료 → {SESSION_FILE}")
        await browser.close()

asyncio.run(main())
