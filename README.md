# discord-webGPTimg

ChatGPT 웹 UI 자동화 기반 이미지 생성 툴. API 없이 GPT Image 2.0 웹에서 직접 생성.

## 실행 환경

- **OS**: WSL2 (Windows Subsystem for Linux)
- **브라우저**: Patchright (봇 감지 우회 Playwright 포크) — WSLg로 Chromium 창 표시
- **세션**: `session.json` (로그인 쿠키, gitignore됨)

## 봇 시스템 연동 (tmuxDISCORD_cc)

이 툴은 [tmuxDISCORD_cc](https://github.com/cliphijack/tmuxDISCORD_cc) 봇 시스템 위에서 운영됨.

```
Discord 채널
  └─ 봇 (Python) ─ send-keys ─▶ tmux pane (meta Claude REPL)
                                      └─ image-bot/generate.py 호출
                                      └─ 결과 이미지 → Discord 첨부
```

- **meta 에이전트**가 Discord 메시지를 받아 `generate.py` 를 직접 실행
- **다른 에이전트** (예: detail-page봇)도 `@meta` 마커로 이미지 생성 요청 가능
  ```
  @meta 지피티웹이미지 쇼츠 시네마틱 장면1: ... / 장면2: ...
  ```
- Stop hook → webhook POST로 결과 이미지 Discord 자동 첨부

## 스타일 메뉴판

스타일 프리셋 & 캔버스 모드 시각 메뉴:
**https://cliphijack.github.io/discord-webGPTimg/**

## 설치 & 사용법

```bash
pip install -r image-bot/requirements.txt
python -m patchright install chromium

# 1회 로그인 (WSL 터미널에서 직접 실행)
python image-bot/login.py

# 단일 이미지 생성
python image-bot/generate.py --prompt "프롬프트" --out output.png

# 상세페이지 모드 (패널별 생성 + 수직 합치기)
python image-bot/generate.py --mode detail-page --prompt-file prompts.txt --out-dir ./panels/
```

## 캔버스 모드

| 모드 | 장수 | 비율 | 용도 |
|------|------|------|------|
| single | 1장 | 자유 | 기본 |
| detail-page | N장 | 세로 | 상세페이지 패널 |
| (쇼츠/유튜브/인스타/블로그/HD — 구현 예정) | | | |
