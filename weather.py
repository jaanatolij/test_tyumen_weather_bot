#!/usr/bin/env python3
"""Fetch Tyumen weather from Open-Meteo and send a morning summary to Telegram."""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

LATITUDE = 57.1522
LONGITUDE = 65.5272
CITY = "Тюмень"

OPEN_METEO_URL = (
    "https://api.open-meteo.com/v1/forecast"
    f"?latitude={LATITUDE}&longitude={LONGITUDE}"
    "&current=temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m"
    "&daily=weather_code,temperature_2m_max,temperature_2m_min"
    "&wind_speed_unit=ms"
    "&timezone=Asia%2FYekaterinburg"
    "&forecast_days=1"
)

WEATHER_CODES: dict[int, str] = {
    0: "ясно",
    1: "преимущественно ясно",
    2: "переменная облачность",
    3: "пасмурно",
    45: "туман",
    48: "изморозь",
    51: "лёгкая морось",
    53: "морось",
    55: "сильная морось",
    56: "ледяная морось",
    57: "сильная ледяная морось",
    61: "небольшой дождь",
    63: "дождь",
    65: "сильный дождь",
    66: "ледяной дождь",
    67: "сильный ледяной дождь",
    71: "небольшой снег",
    73: "снег",
    75: "сильный снег",
    77: "снежная крупа",
    80: "небольшой ливень",
    81: "ливень",
    82: "сильный ливень",
    85: "небольшой снегопад",
    86: "сильный снегопад",
    95: "гроза",
    96: "гроза с градом",
    99: "гроза с сильным градом",
}


def weather_label(code: int) -> str:
    return WEATHER_CODES.get(code, f"код {code}")


def format_temp(value: float) -> str:
    rounded = int(round(value))
    if rounded > 0:
        return f"+{rounded}°"
    return f"{rounded}°"


def http_get_json(url: str) -> dict:
    request = urllib.request.Request(url, headers={"User-Agent": "tyumen-morning-weather/1.0"})
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code} for {url}: {body}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Request failed for {url}: {exc.reason}") from exc


def fetch_weather() -> dict:
    return http_get_json(OPEN_METEO_URL)


def build_message(data: dict) -> str:
    current = data["current"]
    daily = data["daily"]

    now_temp = format_temp(current["temperature_2m"])
    now_label = weather_label(int(current["weather_code"]))
    day_temp = format_temp(daily["temperature_2m_max"][0])
    night_temp = format_temp(daily["temperature_2m_min"][0])
    wind = current["wind_speed_10m"]
    humidity = int(current["relative_humidity_2m"])

    return (
        f"Доброе утро, {CITY}\n"
        f"Сейчас: {now_temp}, {now_label}\n"
        f"Днём: {day_temp} … ночью {night_temp}\n"
        f"Ветер {wind:.0f} м/с, влажность {humidity}%"
    )


def send_telegram(token: str, chat_id: str, text: str) -> None:
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = urllib.parse.urlencode(
        {
            "chat_id": chat_id,
            "text": text,
            "disable_web_page_preview": "true",
        }
    ).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=payload,
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "tyumen-morning-weather/1.0",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            result = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Telegram HTTP {exc.code}: {body}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Telegram request failed: {exc.reason}") from exc

    if not result.get("ok"):
        raise RuntimeError(f"Telegram API error: {result}")


def main() -> int:
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    chat_id = os.environ.get("TELEGRAM_CHAT_ID", "").strip()
    if not token or not chat_id:
        print("TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID are required", file=sys.stderr)
        return 1

    try:
        data = fetch_weather()
        message = build_message(data)
        send_telegram(token, chat_id, message)
    except Exception as exc:  # noqa: BLE001 — surface any failure to Actions
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print(message)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
