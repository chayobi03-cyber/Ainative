#!/usr/bin/env python3
"""재검토 기한을 iCalendar(.ics) 파일로 뽑는다.

왜 필요한가
    `kb/ingestion.yaml`의 `review_by`·`recheck_by`는 YAML 필드일 뿐이고 **알림을
    보내지 않는다.** 2026-09-01 모델 가격 변경을 아무 캘린더도 모른다. 담당자가
    바뀌면 그대로 잊힌다.

왜 .ics 인가
    Google Calendar / Outlook / Apple / Thunderbird 어디서나 가져오기가 된다.
    사내가 어떤 캘린더를 쓰든 맞출 수 있고, 특정 API 연동이 필요 없어 폐쇄망에서도
    파일만 옮기면 된다.

사용법:
    python3 tools/make_calendar.py > ainative-review.ics
    python3 tools/make_calendar.py --organizer "hong@corp.example" --alarm-days 14
"""
from __future__ import annotations

import argparse
import re
import sys
from datetime import date, datetime, timedelta
from pathlib import Path


def yaml_scalar(raw: str) -> str:
    """YAML 스칼라 값 하나를 읽는다.

    `name: ""   # 예: 홍길동` 같은 줄에서, 따옴표 뒤 주석을 값으로 오인하면
    빈 항목이 기입된 것처럼 보인다(실제로 담당자 미기입을 놓쳤던 버그).
    따옴표가 있으면 닫는 따옴표까지만 값이고 나머지는 버린다.
    """
    raw = raw.strip()
    m = re.match(r"^([\"'])(.*?)\1", raw)
    if m:
        return m.group(2)
    return raw.split("#", 1)[0].strip()


def parse_review(path: Path) -> list[dict]:
    """ingestion.yaml의 review 절을 읽는다(최소 파서, PyYAML 불필요)."""
    text = path.read_text(encoding="utf-8")
    m = re.search(r"^review:\s*$(.*?)(?=^\S|\Z)", text, re.M | re.S)
    if not m:
        return []
    block = m.group(1)

    out = []
    nxt = re.search(r"next_review:\s*\"?([\d-]+)\"?", block)
    cad = re.search(r"cadence:\s*\"?(\w+)\"?", block)
    if nxt:
        out.append(
            {
                "date": nxt.group(1),
                "title": "Ainative KB 전체 재검토",
                "desc": f"전체 청크 재검토 ({cad.group(1) if cad else 'periodic'}). "
                        "tools/kb_audit.py 실행 후 confidence·freshness 갱신. "
                        "히트 0회 청크 점검.",
                "assign_key": "quarterly_full",
            }
        )

    for item in re.findall(r"-\s*topic:\s*\"?([^\"\n]+)\"?\n(.*?)(?=\n\s*-\s*topic:|\Z)", block, re.S):
        topic, body = item[0].strip(), item[1]
        d = re.search(r"recheck_by:\s*\"?([\d-]+)\"?", body)
        reason = re.search(r"reason:\s*\"?([^\"\n]+)\"?", body)
        last = re.search(r"last_verified:\s*\"?([\d-]+)\"?", body)
        if not d:
            continue
        desc = reason.group(1).strip() if reason else ""
        if last:
            desc += f" (최근 확인 {last.group(1)})"
        out.append(
            {
                "date": d.group(1),
                "title": f"Ainative KB 재확인 — {topic}",
                "desc": desc + " 확인 후 kb/corrections.yaml 갱신.",
                "assign_key": "model_pricing" if "가격" in topic else "",
            }
        )
    return out


def fold(line: str) -> str:
    """RFC 5545: 75옥텟 초과 시 접는다. 한글은 멀티바이트라 바이트 기준으로 자른다."""
    raw = line.encode("utf-8")
    if len(raw) <= 75:
        return line
    parts, cur = [], b""
    for ch in line:
        b = ch.encode("utf-8")
        if len(cur) + len(b) > 74:
            parts.append(cur.decode("utf-8"))
            cur = b""
        cur += b
    if cur:
        parts.append(cur.decode("utf-8"))
    return parts[0] + "".join("\r\n " + p for p in parts[1:])


def esc(s: str) -> str:
    return s.replace("\\", "\\\\").replace(";", r"\;").replace(",", r"\,").replace("\n", r"\n")


def build_ics(events: list[dict], organizer: str, alarm_days: int, assignments: dict) -> str:
    stamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Ainative//KB Review Schedule//KO",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        "X-WR-CALNAME:Ainative KB 재검토",
    ]
    for i, e in enumerate(events, 1):
        d = date.fromisoformat(e["date"])
        who = assignments.get(e.get("assign_key", ""), "")
        desc = e["desc"] + (f" 담당: {who}" if who else " 담당: (OWNERS.yaml 미지정)")
        lines += [
            "BEGIN:VEVENT",
            f"UID:ainative-review-{i}-{e['date']}@ainative.local",
            f"DTSTAMP:{stamp}",
            f"DTSTART;VALUE=DATE:{d.strftime('%Y%m%d')}",
            f"DTEND;VALUE=DATE:{(d + timedelta(days=1)).strftime('%Y%m%d')}",
            fold(f"SUMMARY:{esc(e['title'])}"),
            fold(f"DESCRIPTION:{esc(desc)}"),
            "STATUS:CONFIRMED",
            "TRANSP:TRANSPARENT",
        ]
        if organizer:
            lines.append(f"ORGANIZER:mailto:{organizer}")
        if alarm_days > 0:
            lines += [
                "BEGIN:VALARM",
                "ACTION:DISPLAY",
                fold(f"DESCRIPTION:{esc(e['title'])} — {alarm_days}일 전"),
                f"TRIGGER:-P{alarm_days}D",
                "END:VALARM",
            ]
        lines.append("END:VEVENT")
    lines.append("END:VCALENDAR")
    return "\r\n".join(lines) + "\r\n"


def read_assignments(path: Path) -> dict:
    if not path.exists():
        return {}
    text = path.read_text(encoding="utf-8")
    m = re.search(r"^review_assignments:\s*$(.*?)(?=^\S|\Z)", text, re.M | re.S)
    if not m:
        return {}
    out = {}
    for k, v in re.findall(r"^\s+(\w+):\s*(.*)$", m.group(1), re.M):
        val = yaml_scalar(v)
        if val:
            out[k] = val
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ingestion", type=Path, default=Path("kb/ingestion.yaml"))
    ap.add_argument("--owners", type=Path, default=Path("OWNERS.yaml"))
    ap.add_argument("--organizer", default="", help="주최자 이메일 (사내 값)")
    ap.add_argument("--alarm-days", type=int, default=7, help="며칠 전 알림 (0=없음)")
    ap.add_argument("--out", type=Path, default=None)
    ap.add_argument("--list", action="store_true", help="일정만 출력")
    a = ap.parse_args()

    events = parse_review(a.ingestion)
    if not events:
        print("재검토 일정을 찾지 못했습니다.", file=sys.stderr)
        return 1

    if a.list:
        for e in sorted(events, key=lambda x: x["date"]):
            print(f"  {e['date']}  {e['title']}")
        return 0

    ics = build_ics(events, a.organizer, a.alarm_days, read_assignments(a.owners))
    if a.out:
        a.out.write_text(ics, encoding="utf-8")
        print(f"{len(events)}건 → {a.out}", file=sys.stderr)
    else:
        sys.stdout.write(ics)
    return 0


if __name__ == "__main__":
    sys.exit(main())
