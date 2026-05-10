#!/usr/bin/env python3
"""
Fire many chat prompts against a running PrivateAI Box API (default http://127.0.0.1:8000).

Usage:
  python scripts/bulk_chat_probe.py
  python scripts/bulk_chat_probe.py --base-url http://127.0.0.1:8000 --password changeme

Requires: pip install httpx (or run from backend venv with httpx).
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from collections import Counter

import httpx

DEFAULT_EMAIL = os.environ.get("PROBE_EMAIL", "admin@example.com")
DEFAULT_PASSWORD = os.environ.get("PROBE_PASSWORD", "changeme")


def _prompts() -> list[str]:
    """100 varied prompts: chitchat, STM32/RAG, vague, off-topic, counts, follow-ups."""
    p: list[str] = []
    # Chitchat / meta (20)
    for t in (
        "hi",
        "hello there",
        "thanks",
        "bye",
        "ok",
        "what can you do?",
        "who are you",
        "good morning",
        "hey",
        "thank you very much",
        "yo",
        "sup",
        "how does this work",
        "what is this app",
        "help",
        "hiya",
        "gm",
        "thx",
        "cool",
        "nice",
    ):
        p.append(t)
    # STM32 / datasheet / peripherals (35)
    stm = [
        "what is stm32",
        "stm32f405 overview",
        "STM32F407xx features",
        "how many ADC does stm32 have?",
        "how many timers on stm32f405",
        "how many timer stm32 has",
        "what voltage stm32 works with",
        "VDD range stm32f405",
        "VBAT stm32",
        "does stm32 have AES",
        "stm32 crypto peripheral",
        "PWM timers stm32",
        "what about ADC and PWM timers?",
        "GPIO stm32",
        "SPI peripheral stm32",
        "I2C stm32",
        "brownout stm32",
        "PVD stm32",
        "how many pins stm32f405",
        "how many pin counts?",
        "LQFP package pins",
        "SDIO peripheral stm32",
        "how many SD card peripheral?",
        "DMA stm32",
        "USART stm32",
        "clock PLL stm32",
        "HSE crystal stm32",
        "backup domain stm32",
        "regulator buck stm32",
        "datasheet stm32f405",
        "do you have stm32 datasheet",
        "the datasheet you have how many timers does it say it has?",
        "its the pdf you are talking about",
        "what do you know about stm32",
        "cortex-m4 stm32",
    ]
    p.extend(stm)
    # Off-corpus / generic (15)
    off = [
        "what is the capital of France",
        "explain quantum computing",
        "write a poem about cats",
        "what is 2+2",
        "who won the superbowl in 1999",
        "recipe for lasagna",
        "what is the quarterly revenue target",
        "tell me about zebras and astronomy",
        "capital of Mars",
        "how to learn Japanese fast",
        "what is docker",
        "explain blockchain",
        "stock price of apple today",
        "weather in Tokyo",
        "translate hello to spanish",
    ]
    p.extend(off)
    # Policy-style (may hit fixture or NOT_FOUND) (10)
    pol = [
        "How fast do staff need to notify the office manager?",
        "emergency procedure office manager",
        "notify office manager how long",
        "15 minutes policy",
        "staff handbook emergency",
        "office manager notification",
        "revenue target Q3",
        "Q3 revenue target forty two million",
        "company handbook revenue",
        "integration upload content",
    ]
    p.extend(pol)
    # Short / ambiguous / follow-up style (20)
    amb = [
        "how many?",
        "how many ADC?",
        "timers?",
        "voltage?",
        "and pwm?",
        "same document",
        "that table",
        "page 140",
        "what about it",
        "more detail",
        "why",
        "source?",
        "cite that",
        "expand",
        "ok what else",
        "next question",
        "continue",
        "elaborate",
        "short answer",
        "one sentence",
    ]
    p.extend(amb)
    assert len(p) == 100, len(p)
    return p


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-url", default=os.environ.get("PROBE_BASE_URL", "http://127.0.0.1:8000"))
    ap.add_argument("--email", default=DEFAULT_EMAIL)
    ap.add_argument("--password", default=DEFAULT_PASSWORD)
    ap.add_argument("--timeout", type=float, default=45.0, help="Per-request timeout seconds")
    ap.add_argument("--session-every", type=int, default=0, help="If >0, reuse session_id every N prompts")
    args = ap.parse_args()

    prompts = _prompts()
    base = args.base_url.rstrip("/")
    timeout = httpx.Timeout(args.timeout, connect=10.0)

    results: list[dict] = []
    session_id: str | None = None

    with httpx.Client(base_url=base, timeout=timeout) as client:
        login = client.post(
            "/api/auth/login",
            json={"email": args.email, "password": args.password},
        )
        if login.status_code != 200:
            print(f"LOGIN FAILED {login.status_code}: {login.text[:500]}", file=sys.stderr)
            return 1
        token = login.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        for i, msg in enumerate(prompts, start=1):
            body: dict = {"message": msg}
            if session_id and args.session_every and i % args.session_every != 1:
                body["session_id"] = session_id

            t0 = time.perf_counter()
            try:
                r = client.post("/api/chat", headers=headers, json=body)
                elapsed = (time.perf_counter() - t0) * 1000
                row = {
                    "i": i,
                    "prompt": msg[:120],
                    "status": r.status_code,
                    "ms": round(elapsed, 1),
                }
                if r.status_code == 200:
                    data = r.json()
                    reply = data.get("reply", "")
                    cites = data.get("citations") or []
                    row["reply_preview"] = reply.replace("\n", " ")[:140]
                    row["citations"] = len(cites)
                    row["not_found"] = "could not find" in reply.lower()
                    row["chitchat_like"] = len(cites) == 0 and len(reply) < 400
                    sid = data.get("session_id")
                    if sid:
                        session_id = sid
                else:
                    row["error"] = r.text[:200]
                results.append(row)
            except Exception as exc:  # noqa: BLE001
                results.append(
                    {
                        "i": i,
                        "prompt": msg[:120],
                        "status": "exception",
                        "ms": round((time.perf_counter() - t0) * 1000, 1),
                        "error": str(exc)[:200],
                    }
                )

            if i % 10 == 0:
                print(f"... {i}/100", flush=True)

    ok = sum(1 for r in results if r.get("status") == 200)
    nf = sum(1 for r in results if r.get("not_found"))
    ch = sum(1 for r in results if r.get("chitchat_like"))
    cites_hist = Counter(r.get("citations", -1) for r in results if r.get("status") == 200)

    summary = {
        "total": len(results),
        "http_200": ok,
        "not_found_replies": nf,
        "chitchat_like_empty_cites": ch,
        "citation_count_histogram": dict(sorted(cites_hist.items())),
        "avg_ms_success": round(
            sum(r["ms"] for r in results if r.get("status") == 200) / max(ok, 1),
            1,
        ),
    }
    out_path = os.environ.get("PROBE_JSON_OUT", "/tmp/aibox_bulk_chat_probe.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({"summary": summary, "results": results}, f, indent=2)

    print(json.dumps(summary, indent=2))
    print(f"\nFull results written to {out_path}")
    return 0 if ok == len(results) else 2


if __name__ == "__main__":
    raise SystemExit(main())
