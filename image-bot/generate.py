"""
ChatGPT GPT Image 자동 생성

사용법:
  python3 generate.py --prompt "프롬프트" --out output.png
  python3 generate.py --prompt-file prompts.txt --out-dir ./outputs/
  python3 generate.py --mode detail-page --prompt-file prompts.txt --out-dir ./panels/
"""

import asyncio
import argparse
import sys
from pathlib import Path
from patchright.async_api import async_playwright

SESSION_FILE = Path(__file__).parent / "session.json"
TIMEOUT = 150_000  # 이미지 생성 최대 대기 150초


async def generate_image(page, prompt: str) -> bytes | None:
    """프롬프트 주입 → 전송 → 이미지 완료 대기 → bytes 반환"""

    ta = await page.wait_for_selector(
        '#prompt-textarea, [data-testid="prompt-textarea"], div[contenteditable="true"]',
        timeout=10_000
    )
    await ta.click()
    await page.keyboard.press("Control+a")
    await page.keyboard.press("Delete")
    await ta.type(prompt, delay=30)

    send_btn = await page.wait_for_selector(
        '[data-testid="send-button"]:not([disabled])', timeout=5_000
    )
    prev_img_count = len(await page.query_selector_all(
        '[data-testid="good-image-turn-action-button"]'
    ))
    await send_btn.click()

    print(f"  이미지 생성 중... (최대 {TIMEOUT//1000}초)")
    start = asyncio.get_event_loop().time()
    while asyncio.get_event_loop().time() - start < TIMEOUT / 1000:
        btns = await page.query_selector_all('[data-testid="good-image-turn-action-button"]')
        if len(btns) > prev_img_count:
            await page.wait_for_timeout(4_000)
            new_btn = btns[-1]
            img = None
            el = new_btn
            for _ in range(15):
                parent = await el.evaluate_handle("el => el.parentElement")
                img_el = await parent.query_selector("img[src]")
                if img_el:
                    src = await img_el.get_attribute("src")
                    if src and src.startswith("http"):
                        img = src
                        break
                el = parent

            if not img:
                imgs = await page.eval_on_selector_all(
                    "img[src]",
                    "els => els.map(e => e.src).filter(s => s.startsWith('http') && !s.includes('.svg'))"
                )
                img = imgs[-1] if imgs else None

            if img:
                print(f"  이미지 URL: {img[:80]}...")
                resp = await page.request.get(img)
                return await resp.body()
        await asyncio.sleep(1)

    print("  타임아웃: 이미지 생성 실패")
    return None


def combine_vertical(image_paths: list[Path], out_path: Path):
    """패널 이미지들을 수직으로 합치기"""
    from PIL import Image

    images = [Image.open(p) for p in image_paths]
    width = max(img.width for img in images)
    total_height = sum(img.height for img in images)

    canvas = Image.new("RGB", (width, total_height), (255, 255, 255))
    y = 0
    for img in images:
        if img.width != width:
            ratio = width / img.width
            img = img.resize((width, int(img.height * ratio)), Image.LANCZOS)
        canvas.paste(img, (0, y))
        y += img.height

    canvas.save(out_path, "PNG", optimize=True)
    print(f"  합치기 완료 → {out_path}")


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompt", help="단일 프롬프트")
    parser.add_argument("--prompt-file", help="프롬프트 파일 (한 줄 = 1장)")
    parser.add_argument("--out", help="출력 파일 (단일)")
    parser.add_argument("--out-dir", default="./outputs", help="출력 디렉토리 (다중)")
    parser.add_argument("--mode", default="single",
                        choices=["single", "detail-page"],
                        help="생성 모드 (single: 기본, detail-page: 상세페이지 패널)")
    args = parser.parse_args()

    if not SESSION_FILE.exists():
        print("세션 없음. 먼저 login.py 실행하세요.")
        sys.exit(1)

    prompts = []
    if args.prompt:
        prompts = [args.prompt]
    elif args.prompt_file:
        prompts = [l.strip() for l in Path(args.prompt_file).read_text().splitlines() if l.strip()]
    else:
        print("--prompt 또는 --prompt-file 필요")
        sys.exit(1)

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    saved_paths = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        ctx = await browser.new_context(storage_state=str(SESSION_FILE))
        page = await ctx.new_page()

        await page.goto("https://chatgpt.com/")
        await page.wait_for_timeout(2000)

        for i, prompt in enumerate(prompts, 1):
            print(f"\n[{i}/{len(prompts)}] {prompt[:60]}...")
            data = await generate_image(page, prompt)
            if data:
                if args.mode == "detail-page":
                    out_path = out_dir / f"panel_{i:02d}.png"
                elif args.out and len(prompts) == 1:
                    out_path = Path(args.out)
                else:
                    out_path = out_dir / f"image_{i:02d}.png"
                out_path.write_bytes(data)
                print(f"  저장 → {out_path}")
                saved_paths.append(out_path)
            else:
                print(f"  실패 (건너뜀)")

        await browser.close()

    # detail-page 모드: 생성된 패널들 수직 합치기
    if args.mode == "detail-page" and saved_paths:
        combined_path = out_dir / "combined.png"
        print(f"\n[합치기] {len(saved_paths)}개 패널 → combined.png")
        combine_vertical(sorted(saved_paths, key=lambda p: p.stem), combined_path)

    print("\n완료.")


asyncio.run(main())
