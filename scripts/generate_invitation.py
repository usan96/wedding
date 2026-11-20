#!/usr/bin/env python3
"""Generate the Korean wedding invitation from the repository's input file."""

import argparse
import calendar
import filecmp
import json
import os
import re
import shutil
import sys
from dataclasses import dataclass
from datetime import date, time
from html import escape
from ipaddress import IPv6Address
from pathlib import Path, PurePosixPath
from string import Template
from tempfile import NamedTemporaryFile, TemporaryDirectory
from urllib.parse import quote, urlsplit


ROOT = Path(__file__).resolve().parent.parent
INPUT_FILE = ROOT / "invitation.json"
TEMPLATE_FILE = ROOT / "templates" / "invitation.html"
SAMPLE_PHOTO = ROOT / "sample.png"
PHOTO_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
REQUIRED_TEXT_FIELDS = ("groom_name", "bride_name", "venue_name", "venue_address")
OPTIONAL_TEXT_FIELDS = ("venue_hall", "venue_floor", "cover_photo_alt")
EXAMPLE_TEXT = {
    "groom_name": "예시 신랑",
    "bride_name": "예시 신부",
    "venue_name": "예시 웨딩홀",
    "venue_address": "예시 주소",
    "venue_hall": "예시 홀",
    "cover_photo_alt": "예시 웨딩 사진",
}
INPUT_FIELDS = {
    *REQUIRED_TEXT_FIELDS, *OPTIONAL_TEXT_FIELDS,
    "status", "date", "time", "directions_url", "cover_photo",
}


class InputError(ValueError):
    """An input file or field needs correction."""


@dataclass(frozen=True)
class Invitation:
    status: str
    groom_name: str
    bride_name: str
    venue_name: str
    venue_address: str
    venue_hall: str
    venue_floor: str
    cover_photo_alt: str
    date: date
    time: time
    directions_url: str
    cover_photo: Path


def unique_fields(pairs):
    values = {}
    for field, value in pairs:
        if field in values:
            raise InputError(f"{field} — 같은 항목이 두 번 입력되었습니다.")
        values[field] = value
    return values


def read_fields():
    try:
        values = json.loads(INPUT_FILE.read_text(encoding="utf-8"), object_pairs_hook=unique_fields)
    except json.JSONDecodeError as error:
        raise InputError(
            f"{INPUT_FILE.name} — {error.lineno}행 {error.colno}열의 JSON 형식을 확인해 주세요."
        ) from error
    except UnicodeDecodeError as error:
        raise InputError(f"{INPUT_FILE.name} — UTF-8로 저장해 주세요.") from error
    if not isinstance(values, dict):
        raise InputError(f"{INPUT_FILE.name} — 항목을 JSON 객체 하나로 입력해 주세요.")
    unknown = sorted(values.keys() - INPUT_FIELDS)
    if unknown:
        raise InputError(f"{', '.join(unknown)} — 사용할 수 없는 항목입니다.")
    return values


def text_field(values, field, *, optional=False):
    if field not in values:
        if optional:
            return ""
        raise InputError(f"{field} — 필수 항목이 빠졌습니다.")
    value = values[field]
    if not isinstance(value, str):
        raise InputError(f"{field} — 큰따옴표로 감싼 문자열을 입력해 주세요.")
    if not optional and not value.strip():
        raise InputError(f"{field} — 값을 입력해 주세요.")
    try:
        value.encode("utf-8")
    except UnicodeEncodeError as error:
        raise InputError(f"{field} — 올바른 문자를 입력해 주세요.") from error
    return value if value.strip() else ""


def parse_date(value):
    try:
        if re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", value):
            return date.fromisoformat(value)
    except ValueError:
        pass
    raise InputError("date — 실제 달력에 있는 날짜를 YYYY-MM-DD로 입력해 주세요.")


def parse_time(value):
    try:
        if re.fullmatch(r"[0-9]{2}:[0-9]{2}", value):
            return time.fromisoformat(value)
    except ValueError:
        pass
    raise InputError("time — 시작 시각을 24시간제 HH:MM으로 입력해 주세요.")


def validate_numeric_host(host):
    parts = host.removesuffix(".").split(".")
    last = parts[-1]
    if not last.isdecimal() and re.fullmatch(r"0x[0-9a-f]*", last) is None:
        return

    # Browsers parse hosts ending in a number as IPv4, including short forms.
    if len(parts) > 4:
        raise ValueError
    numbers = []
    for part in parts:
        if re.fullmatch(r"0x[0-9a-f]*", part):
            numbers.append(int(part[2:] or "0", 16))
        elif re.fullmatch(r"0[0-7]*", part):
            numbers.append(int(part, 8))
        elif re.fullmatch(r"[1-9][0-9]*", part):
            numbers.append(int(part, 10))
        else:
            raise ValueError
    if any(number > 255 for number in numbers[:-1]) or numbers[-1] >= 256 ** (5 - len(numbers)):
        raise ValueError


def validate_directions_url(value, status):
    try:
        if any(ch.isspace() or not ch.isprintable() or ch == "\\" for ch in value):
            raise ValueError
        url = urlsplit(value)
        host = url.hostname
        if url.scheme not in {"https", "http"} or not host or url.username is not None:
            raise ValueError
        if "[" in url.netloc or "]" in url.netloc:
            # urlsplit can return an IPv6 hostname even when the authority has a suffix.
            if not re.fullmatch(r"\[[0-9a-fA-F:.]+\](?::[0-9]*)?", url.netloc):
                raise ValueError
            IPv6Address(host)
        else:
            host = host.encode("idna").decode("ascii").lower()
            validate_numeric_host(host)
        port = url.port
        if port == 0 or not host.strip(".") or any(ch in '"<>%^`{|}' for ch in host):
            raise ValueError
    except ValueError as error:
        raise InputError("directions_url — 유효한 전체 HTTP 또는 HTTPS 주소를 입력해 주세요.") from error
    host = host.rstrip(".")
    if status == "confirmed" and (host == "example.com" or host.endswith(".example.com")):
        raise InputError("directions_url — 확정한 예식장의 길찾기 주소를 입력해 주세요.")
    return value


def jpeg_has_image_data(image, size):
    if image.read(2) != b"\xff\xd8":
        return False
    has_frame = False
    while image.tell() < size:
        if image.read(1) != b"\xff":
            return False
        marker = image.read(1)
        while marker == b"\xff":
            marker = image.read(1)
        if marker in {b"", b"\x00", b"\xd8", b"\xd9"}:
            return False
        if marker == b"\x01":  # Standalone TEM marker.
            continue
        length = int.from_bytes(image.read(2), "big")
        segment_end = image.tell() + length - 2
        if length < 2 or segment_end > size:
            return False
        if 0xC0 <= marker[0] <= 0xCF and marker[0] not in {0xC4, 0xC8, 0xCC}:
            if length < 11:
                return False
            has_frame = True
        image.seek(segment_end)
        if marker == b"\xda":
            if not has_frame or length < 8:
                return False
            # Scan bytes may contain stuffed FF bytes. An unstuffed FF D9 ends the image.
            previous = b""
            scan_start = image.tell()
            while chunk := image.read(64 * 1024):
                data = previous + chunk
                end = data.find(b"\xff\xd9")
                if end != -1:
                    return image.tell() - len(data) + end > scan_start
                previous = data[-1:]
            return False
    return False


def png_has_image_data(image, size):
    header = image.read(33)  # Signature and complete IHDR chunk.
    if not header.startswith(b"\x89PNG\r\n\x1a\n\x00\x00\x00\x0dIHDR"):
        return False
    has_data = False
    while image.tell() + 12 <= size:
        length = int.from_bytes(image.read(4), "big")
        kind = image.read(4)
        chunk_end = image.tell() + length + 4  # Include the CRC.
        if chunk_end > size:
            return False
        if kind == b"IEND":
            return has_data and length == 0 and chunk_end == size and image.read(4) == b"\xaeB\x60\x82"
        if kind == b"IDAT" and length > 0:
            has_data = True
        image.seek(chunk_end)
    return False


def webp_has_frame(image, limit, *, allow_animation=True):
    while image.tell() + 8 <= limit:
        kind = image.read(4)
        length = int.from_bytes(image.read(4), "little")
        payload_end = image.tell() + length
        chunk_end = payload_end + length % 2
        if chunk_end > limit:
            return False
        if kind == b"VP8 " and length > 10 and image.read(6)[3:] == b"\x9d\x01\x2a":
            return True
        if kind == b"VP8L" and length > 5 and image.read(1) == b"\x2f":
            return True
        if kind == b"ANMF" and allow_animation and length > 16:
            image.seek(16, os.SEEK_CUR)  # Skip animation frame parameters.
            if webp_has_frame(image, payload_end, allow_animation=False):
                return True
        image.seek(chunk_end)
    return False


def matches_photo_format(photo):
    """Check the file structure and image payload without decoding pixels."""
    suffix = photo.suffix.lower()
    with photo.open("rb") as image:
        size = image.seek(0, os.SEEK_END)
        image.seek(0)
        if suffix in {".jpg", ".jpeg"}:
            return jpeg_has_image_data(image, size)
        if suffix == ".png":
            return png_has_image_data(image, size)

        header = image.read(12)
        if header[:4] != b"RIFF" or header[8:] != b"WEBP":
            return False
        riff_end = 8 + int.from_bytes(header[4:8], "little")
        return riff_end <= size and webp_has_frame(image, riff_end)


def validate_photo(value, status):
    relative = PurePosixPath(value)
    if relative.is_absolute() or ".." in relative.parts or "\\" in value or "\x00" in value:
        raise InputError("cover_photo — 저장소에 있는 사진을 상대 경로로 입력해 주세요.")
    try:
        photo = ROOT.joinpath(*relative.parts).resolve()
    except (OSError, RuntimeError) as error:
        raise InputError("cover_photo — 사진 경로를 확인해 주세요.") from error
    if photo != SAMPLE_PHOTO and (
        not photo.is_relative_to(ROOT / "assets") or photo.suffix.lower() not in PHOTO_EXTENSIONS
    ):
        raise InputError("cover_photo — assets/ 안의 JPG, JPEG, PNG, WebP 사진을 지정해 주세요.")
    if not photo.is_file():
        raise InputError("cover_photo — 지정한 사진 파일을 찾을 수 없습니다.")
    try:
        valid_format = matches_photo_format(photo)
    except OSError as error:
        raise InputError("cover_photo — 지정한 사진 파일을 읽을 수 없습니다.") from error
    if not valid_format:
        raise InputError("cover_photo — 파일 내용이 확장자에 맞는 JPG, JPEG, PNG, WebP 이미지인지 확인해 주세요.")
    if status == "confirmed" and SAMPLE_PHOTO.is_file() and filecmp.cmp(photo, SAMPLE_PHOTO, shallow=False):
        raise InputError("cover_photo — 기본 예시 사진 대신 확정 사진을 지정해 주세요.")
    return photo


def load_invitation():
    values = read_fields()
    status = text_field(values, "status")
    if status not in {"draft", "confirmed"}:
        raise InputError("status — draft 또는 confirmed를 입력해 주세요.")
    required = {field: text_field(values, field) for field in REQUIRED_TEXT_FIELDS}
    optional = {field: text_field(values, field, optional=True) for field in OPTIONAL_TEXT_FIELDS}
    if status == "confirmed":
        for field, example in EXAMPLE_TEXT.items():
            if values.get(field, "").strip() == example:
                raise InputError(f"{field} — 예시 대신 확정한 정보를 입력해 주세요.")
    return Invitation(
        status=status,
        **required,
        **optional,
        date=parse_date(text_field(values, "date")),
        time=parse_time(text_field(values, "time")),
        directions_url=validate_directions_url(text_field(values, "directions_url"), status),
        cover_photo=validate_photo(text_field(values, "cover_photo"), status),
    )


def calendar_rows(event_date):
    weeks = calendar.Calendar(calendar.SUNDAY).monthdayscalendar(event_date.year, event_date.month)
    rows = []
    for week in weeks:
        cells = []
        for day in week:
            if day == event_date.day:
                label = (
                    f'<span class="wedding-day">{day}</span>'
                    '<span class="visually-hidden"> 예식일</span>'
                )
            else:
                label = str(day) if day else ""
            cells.append(f"<td>{label}</td>")
        rows.append("            <tr>" + "".join(cells) + "</tr>\n")
    return "".join(rows)


def render(invitation, photo_path):
    event_date, event_time = invitation.date, invitation.time
    weekday = "월화수목금토일"[event_date.weekday()] + "요일"
    period = "오전" if event_time.hour < 12 else "오후"
    display_time = f"{period} {event_time.hour % 12 or 12}시"
    if event_time.minute:
        display_time += f" {event_time.minute}분"

    draft = invitation.status == "draft"
    sample = invitation.cover_photo == SAMPLE_PHOTO
    groom, bride = escape(invitation.groom_name), escape(invitation.bride_name)
    title = f"{groom} · {bride} | 모바일 청첩장"
    draft_note = ""
    if draft:
        title += " 초안"
        note = "청첩장 초안"
        if all(getattr(invitation, field).strip() == EXAMPLE_TEXT[field] for field in REQUIRED_TEXT_FIELDS):
            note += " · 예식 일시와 장소 등 예시 정보가 포함되어 있습니다."
        elif sample:
            note += " · 예시 사진이 포함되어 있습니다."
        draft_note = f'      <p class="draft-note">{note}</p>\n\n'
    venue_details = "".join(
        f"        <div><dt>{label}</dt><dd>{escape(value)}</dd></div>\n"
        for label, value in (("홀", invitation.venue_hall), ("층", invitation.venue_floor))
        if value
    )
    photo_alt = invitation.cover_photo_alt or ("예시 웨딩 사진" if sample else "웨딩 사진")

    values = dict(
        page_title=title,
        robots='  <meta name="robots" content="noindex">\n' if draft else "",
        draft_attribute=" data-draft" if draft else "",
        draft_note=draft_note,
        sample_class=" portrait--sample" if sample else "",
        sample_dimensions=' width="2430" height="3293"' if sample else "",
        photo_url=escape("./" + quote(photo_path.as_posix())),
        photo_alt=escape(photo_alt),
        groom_name=groom,
        bride_name=bride,
        cover_date=event_date.isoformat().replace("-", ".") + " " + weekday,
        schedule_date=f"{event_date.year}년 {event_date.month}월 {event_date.day}일 {weekday}",
        event_datetime=f"{event_date.isoformat()}T{event_time.isoformat(timespec='minutes')}",
        event_time=display_time,
        calendar_month=f"{event_date.year}년 {event_date.month}월",
        calendar_rows=calendar_rows(event_date),
        venue_name=escape(invitation.venue_name),
        venue_address=escape(invitation.venue_address),
        venue_details=venue_details,
        directions_url=escape(invitation.directions_url),
    )
    try:
        template = Template(TEMPLATE_FILE.read_text(encoding="utf-8"))
        return template.substitute(values)
    except (KeyError, ValueError) as error:
        raise InputError(f"{TEMPLATE_FILE.name} — 템플릿을 확인해 주세요. {error}") from error


def write_preview(output, page):
    temporary = NamedTemporaryFile(
        mode="w", encoding="utf-8", dir=output.parent, suffix=".tmp", delete=False
    )
    temporary_path = Path(temporary.name)
    try:
        with temporary:
            temporary.write(page)
        os.replace(temporary_path, output)
    finally:
        temporary_path.unlink(missing_ok=True)


def write_publish_bundle(invitation, output):
    if invitation.status != "confirmed":
        raise InputError("status — 확정 정보와 사진을 대조한 뒤 confirmed로 바꿔 주세요.")
    if output.exists() or output.is_symlink():
        raise InputError(f"{output} — 아직 존재하지 않는 출력 경로를 지정해 주세요.")

    photo_path = Path("assets") / f"cover{invitation.cover_photo.suffix.lower()}"
    page = render(invitation, photo_path)
    with TemporaryDirectory(prefix=".wedding-", dir=output.parent) as temporary:
        bundle = Path(temporary) / "site"
        (bundle / "assets").mkdir(parents=True)
        (bundle / "index.html").write_text(page, encoding="utf-8")
        for asset in ("styles.css", "invitation.js"):
            shutil.copyfile(ROOT / asset, bundle / asset)
        shutil.copyfile(invitation.cover_photo, bundle / photo_path)
        bundle.rename(output)


def main():
    parser = argparse.ArgumentParser(description="입력 파일로 모바일 청첩장을 생성합니다.")
    parser.add_argument("--publish-dir", type=Path, help="게시 번들을 만들 새 디렉터리")
    args = parser.parse_args()
    try:
        invitation = load_invitation()
        if args.publish_dir is None:
            output = ROOT / "index.html"
            photo_path = invitation.cover_photo.relative_to(ROOT)
            write_preview(output, render(invitation, photo_path))
        else:
            output = args.publish_dir.absolute()
            write_publish_bundle(invitation, output)
    except (InputError, OSError) as error:
        print(f"생성 실패 — {error}", file=sys.stderr)
        return 1
    print(f"청첩장을 생성했습니다. {output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
