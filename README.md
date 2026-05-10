# discord-webGPTimg

ChatGPT 웹 UI 자동화 기반 이미지 생성 툴 (API 없음)

## 구성
- `image-bot/` — Patchright 기반 ChatGPT 이미지 자동 생성
- `samples/` — 스타일 프리셋 샘플 이미지
- `docs/` — 스타일 메뉴판 (GitHub Pages)

## 사용법
```bash
pip install -r image-bot/requirements.txt
python -m patchright install chromium
python image-bot/login.py      # 1회 로그인 → session.json 저장
python image-bot/generate.py --prompt "..." --out output.png
```
