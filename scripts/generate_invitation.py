#!/usr/bin/env python3
"""Generate the Korean wedding invitation from the repository's input file."""

from __future__ import annotations

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
from posixpath import normpath
from string import Template
from tempfile import NamedTemporaryFile, TemporaryDirectory
from urllib.parse import quote, unquote, urlencode, urlsplit


ROOT = Path(__file__).resolve().parent.parent
INPUT_FILE = ROOT / "invitation.json"
TEMPLATE_FILE = ROOT / "templates" / "invitation.html"
SAMPLE_PHOTO = ROOT / "sample.png"
ASSETS_DIR = ROOT / "assets"
GALLERY_DIR = ASSETS_DIR / "gallery"
PHOTO_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
DEFAULT_BACKGROUND_COLOR = "#fdfdfd"
REQUIRED_TEXT_FIELDS = ("groom_name", "bride_name", "venue_name", "venue_address")
OPTIONAL_TEXT_FIELDS = (
    "venue_hall", "venue_floor", "cover_photo_alt", "share_title", "share_description",
    "groom_father_name", "groom_mother_name", "bride_father_name", "bride_mother_name",
    "subway", "car", "bus", "parking", "shuttle", "groom_phone", "bride_phone",
)
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
    "status", "date", "time", "directions", "directions_url", "cover_photo", "gallery_photos",
    "background_color", "groom_account", "bride_account", "shuttle_photo", "gallery_order",
    "cover_title_font", "cover_title_scale", "cover_title_bold",
}
ACCOUNT_FIELDS = ("bank", "number", "holder")
DIRECTIONS_FIELDS = {"latitude", "longitude", "map_image", "naver_place_url", "tmap_place_url"}
NAVER_PLACE_HOSTS = {"map.naver.com", "m.map.naver.com", "m.place.naver.com", "naver.me"}
TMAP_PLACE_HOSTS = {"tmap.life", "poi.tmobiweb.com"}
LEAFLET_ASSETS = Path("vendor/leaflet")
FONT_ASSETS = Path("assets/fonts")
INVITATION_FONTS = ("gowun-dodum.woff2", "gowun-dodum-OFL.txt")
DEFAULT_COVER_TITLE_FONT = "qillsey-einstein"
COVER_TITLE_IMAGES = {
    "blacksword": Path("assets/cover-title-blacksword.webp"),
    "qillsey-einstein": Path("assets/cover-title.webp"),
}
LEAFLET_TAGS = (
    '  <link rel="stylesheet" href="./vendor/leaflet/leaflet.css">\n'
    '  <script src="./vendor/leaflet/leaflet.js" defer></script>\n'
)


class InputError(ValueError):
    """An input file or field needs correction."""


@dataclass(frozen=True)
class GalleryPhoto:
    path: Path
    alt: str


@dataclass(frozen=True)
class Directions:
    latitude: float
    longitude: float
    map_image: Path
    naver_place_url: str
    tmap_place_url: str
    tmap_route_url: str


@dataclass(frozen=True)
class Account:
    bank: str
    number: str
    holder: str


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
    gallery_photos: tuple[GalleryPhoto, ...] = ()
    directions: Directions | None = None
    background_color: str = DEFAULT_BACKGROUND_COLOR
    groom_father_name: str = ""
    groom_mother_name: str = ""
    bride_father_name: str = ""
    bride_mother_name: str = ""
    subway: str = ""
    car: str = ""
    bus: str = ""
    parking: str = ""
    shuttle: str = ""
    groom_phone: str = ""
    bride_phone: str = ""
    groom_account: Account | None = None
    bride_account: Account | None = None
    shuttle_photo: Path | None = None
    cover_title_font: str = DEFAULT_COVER_TITLE_FONT
    cover_title_scale: float = 1.0
    cover_title_bold: bool = False
    share_title: str = ""
    share_description: str = ""


class JsonObject(dict):
    """Keep the first duplicate key until validation knows the object's location."""

    def __init__(self, pairs):
        super().__init__()
        self.duplicate_field = None
        for field, value in pairs:
            if field in self and self.duplicate_field is None:
                self.duplicate_field = field
            self[field] = value


def check_unique_fields(values, prefix=""):
    if isinstance(values, JsonObject) and values.duplicate_field is not None:
        raise InputError(f"{prefix}{values.duplicate_field} — 같은 항목이 두 번 입력되었습니다.")


def read_fields():
    try:
        values = json.loads(INPUT_FILE.read_text(encoding="utf-8"), object_pairs_hook=JsonObject)
    except json.JSONDecodeError as error:
        raise InputError(
            f"{INPUT_FILE.name} — {error.lineno}행 {error.colno}열의 JSON 형식을 확인해 주세요."
        ) from error
    except UnicodeDecodeError as error:
        raise InputError(f"{INPUT_FILE.name} — UTF-8로 저장해 주세요.") from error
    if not isinstance(values, dict):
        raise InputError(f"{INPUT_FILE.name} — 항목을 JSON 객체 하나로 입력해 주세요.")
    check_unique_fields(values)
    unknown = sorted(values.keys() - INPUT_FIELDS)
    if unknown:
        raise InputError(f"{', '.join(unknown)} — 사용할 수 없는 항목입니다.")
    return values


def text_field(values, field, *, optional=False, location=None):
    location = location or field
    if field not in values:
        if optional:
            return ""
        raise InputError(f"{location} — 필수 항목이 빠졌습니다.")
    value = values[field]
    if not isinstance(value, str):
        raise InputError(f"{location} — 큰따옴표로 감싼 문자열을 입력해 주세요.")
    if not optional and not value.strip():
        raise InputError(f"{location} — 값을 입력해 주세요.")
    try:
        value.encode("utf-8")
    except UnicodeEncodeError as error:
        raise InputError(f"{location} — 올바른 문자를 입력해 주세요.") from error
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


def validate_directions_url(value, status, *, location="directions_url"):
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
        raise InputError(f"{location} — 유효한 전체 HTTP 또는 HTTPS 주소를 입력해 주세요.") from error
    host = host.rstrip(".")
    if status == "confirmed" and (host == "example.com" or host.endswith(".example.com")):
        raise InputError(f"{location} — 확정한 예식장의 길찾기 주소를 입력해 주세요.")
    return value


def coordinate(values, field, limit):
    value = values.get(field)
    if type(value) not in (int, float) or not -limit <= value <= limit:
        raise InputError(f"directions.{field} — {-limit}에서 {limit} 사이의 숫자를 입력해 주세요.")
    return float(value)


def place_url(values, field, hosts, status, *, optional=False):
    location = f"directions.{field}"
    value = text_field(values, field, optional=optional, location=location)
    if not value:
        return ""
    validate_directions_url(value, status, location=location)
    url = urlsplit(value)
    if url.scheme != "https" or url.hostname not in hosts or url.port not in (None, 443):
        raise InputError(f"{location} — 해당 지도 서비스에서 제공하는 HTTPS 장소 링크를 입력해 주세요.")
    if status == "confirmed":
        path = normpath("/" + unquote(url.path).lstrip("/"))
        if path == "/" or (url.hostname == "map.naver.com" and path == "/p"):
            raise InputError(f"{location} — 예식장 장소 상세 또는 공유 링크를 입력해 주세요.")
    return value


def load_directions(values, status, venue_name):
    if "directions" not in values:
        return None
    directions = values["directions"]
    if not isinstance(directions, dict):
        raise InputError("directions — 지도 설정을 JSON 객체로 입력해 주세요.")
    check_unique_fields(directions, prefix="directions.")
    unknown = sorted(directions.keys() - DIRECTIONS_FIELDS)
    if unknown:
        fields = ", ".join(f"directions.{field}" for field in unknown)
        raise InputError(f"{fields} — 사용할 수 없는 항목입니다.")

    latitude = coordinate(directions, "latitude", 90)
    longitude = coordinate(directions, "longitude", 180)
    image = text_field(directions, "map_image", location="directions.map_image")
    map_image = validate_photo(image, status, location="directions.map_image")
    if not map_image.is_relative_to(ASSETS_DIR) or map_image.suffix.lower() not in {".png", ".webp"}:
        raise InputError("directions.map_image — assets/ 안의 PNG 또는 WebP 지도를 지정해 주세요.")
    naver_url = place_url(directions, "naver_place_url", NAVER_PLACE_HOSTS, status)
    tmap_url = place_url(directions, "tmap_place_url", TMAP_PLACE_HOSTS, status, optional=True)
    tmap_route_url = ""
    public_key = os.environ.get("TMAP_PUBLIC_APP_KEY", "").strip()
    if public_key:
        parameters = urlencode(dict(
            appKey=public_key, goalname=venue_name, goalx=longitude, goaly=latitude
        ))
        tmap_route_url = f"https://apis.openapi.sk.com/tmap/app/routes?{parameters}"
    return Directions(latitude, longitude, map_image, naver_url, tmap_url, tmap_route_url)


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


def is_sample_photo(photo):
    return SAMPLE_PHOTO.is_file() and filecmp.cmp(photo, SAMPLE_PHOTO, shallow=False)


def validate_photo(value, status, *, location="cover_photo"):
    relative = PurePosixPath(value)
    if relative.is_absolute() or ".." in relative.parts or "\\" in value or "\x00" in value:
        raise InputError(f"{location} — 저장소에 있는 사진을 상대 경로로 입력해 주세요.")
    try:
        photo = ROOT.joinpath(*relative.parts).resolve()
    except (OSError, RuntimeError) as error:
        raise InputError(f"{location} — 사진 경로를 확인해 주세요.") from error
    if photo != SAMPLE_PHOTO and (
        not photo.is_relative_to(ASSETS_DIR) or photo.suffix.lower() not in PHOTO_EXTENSIONS
    ):
        raise InputError(f"{location} — assets/ 안의 JPG, JPEG, PNG, WebP 사진을 지정해 주세요.")
    if not photo.is_file():
        raise InputError(f"{location} — 지정한 사진 파일을 찾을 수 없습니다.")
    try:
        valid_format = matches_photo_format(photo)
    except OSError as error:
        raise InputError(f"{location} — 지정한 사진 파일을 읽을 수 없습니다.") from error
    if not valid_format:
        raise InputError(f"{location} — 파일 내용이 확장자에 맞는 JPG, JPEG, PNG, WebP 이미지인지 확인해 주세요.")
    if status == "confirmed" and is_sample_photo(photo):
        raise InputError(f"{location} — 기본 예시 사진 대신 확정 사진을 지정해 주세요.")
    return photo


def load_gallery_descriptions(values):
    """Read optional descriptions from the former explicit photo list."""
    entries = values.get("gallery_photos", [])
    if not isinstance(entries, list):
        raise InputError("gallery_photos — 사진 항목을 배열로 입력해 주세요.")

    descriptions = {}
    for index, entry in enumerate(entries):
        location = f"gallery_photos[{index}]"
        if not isinstance(entry, dict):
            raise InputError(f"{location} — 사진 항목을 JSON 객체로 입력해 주세요.")
        check_unique_fields(entry, prefix=f"{location}.")
        unknown = sorted(entry.keys() - {"path", "alt"})
        if unknown:
            raise InputError(f"{location} — 사용할 수 없는 항목입니다. {', '.join(unknown)}")
        path = PurePosixPath(text_field(entry, "path", location=f"{location}.path"))
        alt = text_field(entry, "alt", optional=True, location=f"{location}.alt")
        descriptions[path.as_posix()] = alt
    return descriptions


def load_gallery_photos(values, status):
    descriptions = load_gallery_descriptions(values)
    paths = sorted(
        (
            path for path in GALLERY_DIR.rglob("*")
            if path.suffix.lower() in PHOTO_EXTENSIONS and path.is_file()
        ),
        key=lambda path: (path.name.casefold(), path.relative_to(GALLERY_DIR).as_posix()),
    )
    if "gallery_order" in values:
        order = values["gallery_order"]
        available = {path.relative_to(ROOT).as_posix(): path for path in paths}
        if not isinstance(order, list) or not all(isinstance(path, str) and path in available for path in order):
            raise InputError("gallery_order — assets/gallery/에 있는 사진 경로를 배열로 입력해 주세요.")
        if len(order) != len(set(order)):
            raise InputError("gallery_order — 같은 사진 경로가 중복되어 있습니다.")
        paths = [available[path] for path in order]

    photos = []
    for path in paths:
        relative = path.relative_to(ROOT).as_posix()
        photo = validate_photo(relative, status, location=relative)
        previous_path = (ASSETS_DIR.relative_to(ROOT) / path.relative_to(GALLERY_DIR)).as_posix()
        photos.append(GalleryPhoto(photo, descriptions.get(relative, descriptions.get(previous_path, ""))))
    return tuple(photos)


def load_account(values, field):
    account = values.get(field, {})
    if not isinstance(account, dict):
        raise InputError(f"{field} — 계좌 정보를 JSON 객체로 입력해 주세요.")
    check_unique_fields(account, prefix=f"{field}.")
    unknown = sorted(account.keys() - set(ACCOUNT_FIELDS))
    if unknown:
        fields = ", ".join(f"{field}.{name}" for name in unknown)
        raise InputError(f"{fields} — 사용할 수 없는 항목입니다.")
    details = {
        name: text_field(account, name, optional=True, location=f"{field}.{name}").strip()
        for name in ACCOUNT_FIELDS
    }
    if not any(details.values()):
        return None
    for name, value in details.items():
        if not value:
            raise InputError(f"{field}.{name} — 은행명, 계좌번호, 예금주를 모두 입력해 주세요.")
    if not re.fullmatch(r"[0-9]+(?:[ -][0-9]+)*", details["number"]):
        raise InputError(f"{field}.number — 숫자와 구분용 공백 또는 하이픈을 사용해 주세요.")
    return Account(**details)


def load_invitation():
    values = read_fields()
    status = text_field(values, "status")
    if status not in {"draft", "confirmed"}:
        raise InputError("status — draft 또는 confirmed를 입력해 주세요.")
    required = {field: text_field(values, field) for field in REQUIRED_TEXT_FIELDS}
    optional = {field: text_field(values, field, optional=True) for field in OPTIONAL_TEXT_FIELDS}
    background_color = text_field(values, "background_color", optional=True).strip() or DEFAULT_BACKGROUND_COLOR
    if not re.fullmatch(r"#[0-9a-fA-F]{6}", background_color):
        raise InputError("background_color — #f8f6f0처럼 # 뒤에 6자리 색상 코드를 입력해 주세요.")
    cover_title_font = values.get("cover_title_font", DEFAULT_COVER_TITLE_FONT)
    if not isinstance(cover_title_font, str) or cover_title_font not in COVER_TITLE_IMAGES:
        choices = ", ".join(COVER_TITLE_IMAGES)
        raise InputError(f"cover_title_font — {choices} 중 하나를 입력해 주세요.")
    cover_title_scale = values.get("cover_title_scale", 1.0)
    if type(cover_title_scale) not in (int, float) or not 0.5 <= cover_title_scale <= 1.3:
        raise InputError("cover_title_scale — 0.5 이상 1.3 이하의 숫자를 입력해 주세요.")
    cover_title_bold = values.get("cover_title_bold", False)
    if not isinstance(cover_title_bold, bool):
        raise InputError("cover_title_bold — true 또는 false를 입력해 주세요.")
    if status == "confirmed":
        for field, example in EXAMPLE_TEXT.items():
            if values.get(field, "").strip() == example:
                raise InputError(f"{field} — 예시 대신 확정한 정보를 입력해 주세요.")
    directions = load_directions(values, status, required["venue_name"])
    directions_url = ""
    if directions is None:
        directions_url = validate_directions_url(text_field(values, "directions_url"), status)
    shuttle_photo_value = text_field(values, "shuttle_photo", optional=True).strip()
    shuttle_photo = (
        validate_photo(shuttle_photo_value, status, location="shuttle_photo") if shuttle_photo_value else None
    )
    return Invitation(
        status=status,
        **required,
        **optional,
        background_color=background_color,
        cover_title_font=cover_title_font,
        cover_title_scale=cover_title_scale,
        cover_title_bold=cover_title_bold,
        groom_account=load_account(values, "groom_account"),
        bride_account=load_account(values, "bride_account"),
        date=parse_date(text_field(values, "date")),
        time=parse_time(text_field(values, "time")),
        directions_url=directions_url,
        cover_photo=validate_photo(text_field(values, "cover_photo"), status),
        gallery_photos=load_gallery_photos(values, status),
        directions=directions,
        shuttle_photo=shuttle_photo,
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
            holiday = ' class="calendar-holiday"' if day == 1 and event_date.month == 3 else ""
            cells.append(f"<td{holiday}>{label}</td>")
        rows.append("            <tr>" + "".join(cells) + "</tr>\n")
    return "".join(rows)


def render_gallery(gallery):
    if not gallery:
        return ""

    images = []
    first_url = escape("./" + quote(gallery[0][1].as_posix()))
    for number, (photo, output_path) in enumerate(gallery, start=1):
        url = escape("./" + quote(output_path.as_posix()))
        alt = escape(photo.alt or f"웨딩 사진 {number}")
        span = " gallery-photo--wide" if number in (4, 5, 12, 13) else ""
        images.append(
            f'        <a class="gallery-photo{span}" href="{url}">\n'
            f'          <img src="{url}" alt="{alt}" loading="lazy">\n'
            '        </a>\n'
        )
    return (
        '    <section class="section gallery" aria-labelledby="gallery-title">\n'
        '      <h2 id="gallery-title" lang="en">Gallery</h2>\n'
        '      <div class="gallery-photos">\n'
        + "".join(images)
        + '      </div>\n'
        '      <p class="gallery-hint">클릭하면 이미지를 크게 보실 수 있습니다.</p>\n'
        '      <dialog class="gallery-dialog" aria-label="웨딩 사진 크게 보기">\n'
        '        <div class="gallery-dialog-content">\n'
        '          <button class="gallery-close" type="button" aria-label="사진 닫기" autofocus></button>\n'
        '          <div class="gallery-stage">\n'
        f'            <img class="gallery-full-photo" src="{first_url}" alt="" hidden>\n'
        '            <p class="gallery-message" role="status"></p>\n'
        '          </div>\n'
        '          <div class="gallery-controls">\n'
        '            <button type="button" data-gallery-step="-1" aria-label="이전 사진"></button>\n'
        '            <p class="gallery-position" role="status"></p>\n'
        '            <button type="button" data-gallery-step="1" aria-label="다음 사진"></button>\n'
        '          </div>\n'
        '        </div>\n'
        '      </dialog>\n'
        '    </section>\n\n'
    )


def render_directions(invitation, map_path):
    directions = invitation.directions
    address = (
        '      <div class="address-line">\n'
        f'        <p class="venue-address">{escape(invitation.venue_address)}</p>\n'
        '        <button type="button" class="address-copy" aria-label="예식장 주소 복사" hidden>'
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" aria-hidden="true">'
        '<rect x="8" y="7" width="11" height="14" rx="2"/><path d="M6 17H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2"/>'
        '</svg></button>\n'
        '        <p class="address-status" role="status"></p>\n'
        '      </div>\n'
    )
    if directions is None:
        return (
            f'      {address}'
            f'      <a class="directions-link" href="{escape(invitation.directions_url)}">길찾기</a>\n'
        )

    map_url = escape("./" + quote(map_path.as_posix()))
    venue = escape(invitation.venue_name)
    naver_client_id = os.environ.get("NAVER_MAP_CLIENT_ID", "").strip()
    naver_map_attribute = f' data-naver-client-id="{escape(naver_client_id)}"' if naver_client_id else ""
    naver_query = escape(urlencode(dict(
        dlat=directions.latitude, dlng=directions.longitude, dname=invitation.venue_name
    )))
    naver_url = escape(directions.naver_place_url)
    kakao_name = quote(invitation.venue_name, safe="")
    kakao_url = f"https://map.kakao.com/link/to/{kakao_name},{directions.latitude},{directions.longitude}"
    kakao_map = f"https://map.kakao.com/link/map/{kakao_name},{directions.latitude},{directions.longitude}"
    tmap_url = escape(directions.tmap_place_url) or "#tmap-help"
    tmap_route = directions.tmap_route_url
    tmap_action = f' data-tmap-route="{escape(tmap_route)}"' if tmap_route else ""
    tmap_help = ""
    if not directions.tmap_place_url:
        tmap_help = (
            '        <p id="tmap-help" class="directions-notice" tabindex="-1">'
            'T맵을 열 수 없으면 위 주소를 복사하거나 다른 지도를 선택해 주세요.</p>\n'
        )
    return (
        f'        {address}'
        '        <figure class="venue-map">\n'
        '          <div class="venue-map-frame">\n'
        f'            <a class="venue-map-preview" href="{kakao_map}">\n'
        f'              <img class="venue-map-image" src="{map_url}" alt="{venue} 위치와 주변 도로">\n'
        '              <span class="venue-map-hint">지도에서 위치 보기</span>\n'
        '            </a>\n'
        '            <div class="venue-map-interactive" inert role="region"\n'
        f'              aria-label="{venue} 지도" data-venue="{venue}"\n'
        f'              data-latitude="{directions.latitude}" data-longitude="{directions.longitude}"'
        f'{naver_map_attribute}></div>\n'
        '            <span class="venue-map-hint venue-map-gesture" aria-hidden="true">지도를 눌러 움직일 수 있어요</span>\n'
        '          </div>\n'
        '          <figcaption><a href="https://www.openstreetmap.org/copyright">'
        '© OpenStreetMap contributors</a></figcaption>\n'
        '        </figure>\n'
        '        <div class="directions-actions">\n'
        f'          <a class="directions-link" href="{naver_url}" data-naver-query="{naver_query}">네이버지도</a>\n'
        f'          <a class="directions-link" href="{tmap_url}"{tmap_action}>T MAP</a>\n'
        f'          <a class="directions-link" href="{kakao_url}">카카오맵</a>\n'
        '        </div>\n'
        f'{tmap_help}'
    )


def render_parents(invitation):
    lines = []
    for father, mother, relationship, name in (
        (invitation.groom_father_name, invitation.groom_mother_name, "장남", invitation.groom_name),
        (invitation.bride_father_name, invitation.bride_mother_name, "장녀", invitation.bride_name),
    ):
        parents = "·".join(escape(parent.strip()) for parent in (father, mother) if parent.strip())
        if parents:
            lines.append(f"        <p>{parents}의 {relationship} <strong>{escape(name)}</strong></p>\n")
    if not lines:
        return ""
    return '      <div class="family">\n' + "".join(lines) + '      </div>\n'


def render_transport(invitation, shuttle_photo_path):
    entries = []
    for label, description in (
        ("지하철 이용 시", invitation.subway),
        ("자차 이용 시", invitation.car),
        ("버스 이용 시", invitation.bus),
    ):
        description = escape(description.strip())
        if description:
            entries.append(
                '        <details class="transport-details">\n'
                f'          <summary>{label}</summary>\n'
                f'          <p class="transport-description">{description}</p>\n'
                '        </details>\n'
            )
    parking = escape(invitation.parking.strip())
    shuttle = escape(invitation.shuttle.strip())
    if shuttle or shuttle_photo_path is not None:
        entries.append('        <details class="transport-details"><summary>셔틀버스</summary>\n')
        if shuttle:
            entries.append(f'          <p class="transport-description">{shuttle}</p>\n')
        if shuttle_photo_path is not None:
            photo_url = escape("./" + quote(shuttle_photo_path.as_posix()))
            entries.append(
                '\n          <details class="shuttle-photo">\n'
                '            <summary>탑승지 사진 보기</summary>\n'
                f'            <img src="{photo_url}" alt="셔틀 탑승 장소" loading="lazy" decoding="async">\n'
                '          </details>\n        '
            )
        entries.append('        </details>\n')
    if parking:
        entries.append(
            '        <details class="transport-details"><summary>주차 안내</summary>\n'
            f'          <p class="transport-description">{parking}</p>\n'
            '        </details>\n'
        )
    if not entries:
        return ""
    return '      <div class="transport">\n' + "".join(entries) + '      </div>\n'


def render_contacts(invitation):
    panels = []
    for field, account, label in (
        ("groom_phone", invitation.groom_account, "신랑"),
        ("bride_phone", invitation.bride_account, "신부"),
    ):
        display_number = getattr(invitation, field).strip()
        if not display_number and account is None:
            continue
        panels.append(
            '        <details class="contact-card">\n'
            f'          <summary>{label} 측</summary>\n'
            '          <div class="contact-content">\n'
        )
        if display_number:
            dial_number = re.sub(r"[ ().-]", "", display_number)
            if not re.fullmatch(r"\+?[0-9]{7,15}", dial_number):
                raise InputError(f"{field} — 010-0000-0000과 같은 형식으로 전화번호를 입력해 주세요.")
            panels.append(
                f'            <a class="contact-link" href="tel:{dial_number}">'
                f'{escape(display_number)}</a>\n'
            )
        if account is not None:
            panels.append(
                f'            <p class="account-holder"><span>{label}</span> {escape(account.holder)}</p>\n'
                '            <div class="account-row">\n'
                f'              <p>{escape(account.bank)} <span class="account-number">{escape(account.number)}</span></p>\n'
                f'              <button type="button" class="account-copy" aria-label="{label} 측 계좌번호 복사" hidden>'
                '<span class="account-copy-icon" aria-hidden="true"></span></button>\n'
                '            </div>\n'
                '            <p class="account-status" role="status"></p>\n'
            )
        panels.append('          </div>\n        </details>\n')
    if not panels:
        return ""
    account_message = ""
    if invitation.groom_account or invitation.bride_account:
        account_message = (
            '      <p class="contacts-message">멀리서도 축하의 마음을<br>전하고 싶으신 분들을 위해<br>'
            '계좌번호를 안내드립니다.</p>\n'
        )
    return (
        '    <section class="section contacts" aria-labelledby="contacts-title">\n'
        '      <h2 id="contacts-title">마음 전하실 곳</h2>\n'
        + account_message
        + '      <p class="contacts-message">소중한 축하를 보내주셔서 감사드리며,<br>'
        '따뜻한 마음에 깊이 감사드립니다.</p>\n'
        '      <div class="contact-panels">\n'
        + "".join(panels)
        + '      </div>\n'
        '    </section>\n\n'
    )


def render(invitation, photo_path, gallery, map_path=None, shuttle_photo_path=None):
    event_date, event_time = invitation.date, invitation.time
    weekday = "월화수목금토일"[event_date.weekday()]
    period = "오전" if event_time.hour < 12 else "오후"
    display_time = f"{period} {event_time.hour % 12 or 12}시"
    if event_time.minute:
        display_time += f" {event_time.minute}분"

    draft = invitation.status == "draft"
    sample = invitation.cover_photo == SAMPLE_PHOTO
    groom, bride = escape(invitation.groom_name), escape(invitation.bride_name)
    share_title = invitation.share_title.strip() or (
        f"{invitation.groom_name} · {invitation.bride_name} | 모바일 청첩장"
    )
    schedule_date = f"{event_date.year}년 {event_date.month}월 {event_date.day}일 {weekday}요일"
    share_description = invitation.share_description.strip() or (
        f"{schedule_date} {display_time} · {invitation.venue_name}"
    )
    draft_note = ""
    if draft:
        share_title += " 초안"
        note = "청첩장 초안"
        example_info = all(
            getattr(invitation, field).strip() == EXAMPLE_TEXT[field] for field in REQUIRED_TEXT_FIELDS
        )
        if example_info:
            note += " · 예식 일시와 장소 등 예시 정보가 포함되어 있습니다."
        if (sample and not example_info) or any(is_sample_photo(photo.path) for photo in invitation.gallery_photos):
            note += " · 예시 사진이 포함되어 있습니다."
        draft_note = f'      <p class="draft-note">{note}</p>\n\n'
    venue_summary = " ".join(
        value.strip()
        for value in (invitation.venue_name, invitation.venue_floor, invitation.venue_hall)
        if value.strip()
    )
    photo_alt = invitation.cover_photo_alt or ("예시 웨딩 사진" if sample else "웨딩 사진")

    values = dict(
        share_title=escape(share_title),
        share_description=escape(share_description),
        background_color=escape(invitation.background_color),
        robots='  <meta name="robots" content="noindex">\n' if draft else "",
        leaflet_tags=LEAFLET_TAGS if invitation.directions else "",
        draft_attribute=" data-draft" if draft else "",
        draft_note=draft_note,
        sample_class=" portrait--sample" if sample else "",
        photo_url=escape("./" + quote(photo_path.as_posix())),
        photo_alt=escape(photo_alt),
        groom_name=groom,
        bride_name=bride,
        cover_title_url="./" + COVER_TITLE_IMAGES[invitation.cover_title_font].as_posix(),
        cover_title_scale=invitation.cover_title_scale,
        cover_title_class=" cover-title--bold" if invitation.cover_title_bold else "",
        cover_date=f"{event_date:%Y.%m.%d}.{'MON TUE WED THU FRI SAT SUN'.split()[event_date.weekday()]} "
                   f"{event_time.hour % 12 or 12:02d}:{event_time.minute:02d}{'AM' if period == '오전' else 'PM'}",
        schedule_date=schedule_date,
        event_datetime=f"{event_date.isoformat()}T{event_time.isoformat(timespec='minutes')}",
        event_time=display_time,
        calendar_year=event_date.year,
        calendar_month=f"{event_date.month}월",
        calendar_rows=calendar_rows(event_date),
        gallery=render_gallery(gallery),
        parents=render_parents(invitation),
        venue_summary=escape(venue_summary),
        directions_section=render_directions(invitation, map_path),
        transport=render_transport(invitation, shuttle_photo_path),
        contacts=render_contacts(invitation),
    )
    try:
        cover_ink_file = TEMPLATE_FILE.parent / f"cover-ink-{invitation.cover_title_font}.svg"
        values["cover_title_strokes"] = cover_ink_file.read_text(encoding="utf-8").rstrip()
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
    directions = invitation.directions
    if directions is None:
        raise InputError("directions — 게시 전에 예식장 지도와 길찾기 링크를 입력해 주세요.")
    if not (directions.tmap_place_url or directions.tmap_route_url):
        raise InputError("directions.tmap_place_url — 게시 전에 T맵 장소 링크 또는 TMAP_PUBLIC_APP_KEY를 설정해 주세요.")
    if output.exists() or output.is_symlink():
        raise InputError(f"{output} — 아직 존재하지 않는 출력 경로를 지정해 주세요.")

    photo_path = Path("assets") / f"cover{invitation.cover_photo.suffix.lower()}"
    gallery = [
        (photo, Path("assets/gallery") / f"{number:03d}{photo.path.suffix.lower()}")
        for number, photo in enumerate(invitation.gallery_photos, start=1)
    ]
    map_path = Path("assets") / f"venue-map{directions.map_image.suffix.lower()}"
    shuttle_photo = invitation.shuttle_photo
    shuttle_photo_path = None
    if shuttle_photo is not None:
        shuttle_photo_path = Path("assets") / f"shuttle-stop{shuttle_photo.suffix.lower()}"
    page = render(invitation, photo_path, gallery, map_path, shuttle_photo_path)
    with TemporaryDirectory(prefix=".wedding-", dir=output.parent) as temporary:
        bundle = Path(temporary) / "site"
        (bundle / "assets").mkdir(parents=True)
        (bundle / "index.html").write_text(page, encoding="utf-8")
        for asset in ("styles.css", "invitation.js"):
            shutil.copyfile(ROOT / asset, bundle / asset)
        paper_texture = Path("assets/paper-texture.png")
        shutil.copyfile(ROOT / paper_texture, bundle / paper_texture)
        (bundle / FONT_ASSETS).mkdir()
        for font in INVITATION_FONTS:
            shutil.copyfile(ROOT / FONT_ASSETS / font, bundle / FONT_ASSETS / font)
        cover_title_image = COVER_TITLE_IMAGES[invitation.cover_title_font]
        shutil.copyfile(ROOT / cover_title_image, bundle / cover_title_image)
        shutil.copytree(ROOT / LEAFLET_ASSETS, bundle / LEAFLET_ASSETS)
        shutil.copyfile(invitation.cover_photo, bundle / photo_path)
        shutil.copyfile(directions.map_image, bundle / map_path)
        if shuttle_photo_path is not None:
            shutil.copyfile(shuttle_photo, bundle / shuttle_photo_path)
        if gallery:
            (bundle / "assets/gallery").mkdir()
        for photo, output_path in gallery:
            shutil.copyfile(photo.path, bundle / output_path)
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
            gallery = [(photo, photo.path.relative_to(ROOT)) for photo in invitation.gallery_photos]
            map_path = invitation.directions.map_image.relative_to(ROOT) if invitation.directions else None
            shuttle_photo_path = invitation.shuttle_photo.relative_to(ROOT) if invitation.shuttle_photo else None
            write_preview(output, render(invitation, photo_path, gallery, map_path, shuttle_photo_path))
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
