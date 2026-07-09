import json
import os
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("weath_ApiKey")

GEO_URL = "https://api.openweathermap.org/geo/1.0/direct"
WEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"
AIR_URL = "https://api.openweathermap.org/data/2.5/air_pollution"

HISTORY_FILE = Path(__file__).parent / "history.json"

PM10_GRADES = [(30, "좋음"), (80, "보통"), (150, "나쁨"), (float("inf"), "매우나쁨")]
PM25_GRADES = [(15, "좋음"), (35, "보통"), (75, "나쁨"), (float("inf"), "매우나쁨")]
GRADE_ORDER = ["좋음", "보통", "나쁨", "매우나쁨"]


@dataclass
class WeatherInfo:
    city: str
    temp: float
    feels_like: float
    description: str
    main: str
    wind_speed: float
    humidity: int


@dataclass
class AirInfo:
    pm10: float
    pm25: float
    pm10_grade: str
    pm25_grade: str
    overall_grade: str


def _require_api_key():
    if not API_KEY:
        raise RuntimeError("weath_ApiKey가 설정되지 않았습니다. .env 파일을 확인해 주세요.")


def geocode_city(city: str):
    _require_api_key()
    resp = requests.get(
        GEO_URL,
        params={"q": city, "limit": 1, "appid": API_KEY},
        timeout=10,
    )
    resp.raise_for_status()
    data = resp.json()
    if not data:
        raise ValueError(f"'{city}'에 해당하는 지역을 찾을 수 없습니다.")
    entry = data[0]
    name = entry.get("local_names", {}).get("ko", entry["name"])
    return entry["lat"], entry["lon"], name


def fetch_weather(lat: float, lon: float, display_name: str) -> WeatherInfo:
    resp = requests.get(
        WEATHER_URL,
        params={"lat": lat, "lon": lon, "appid": API_KEY, "units": "metric", "lang": "kr"},
        timeout=10,
    )
    resp.raise_for_status()
    data = resp.json()
    return WeatherInfo(
        city=display_name,
        temp=data["main"]["temp"],
        feels_like=data["main"]["feels_like"],
        description=data["weather"][0]["description"],
        main=data["weather"][0]["main"],
        wind_speed=data["wind"]["speed"],
        humidity=data["main"]["humidity"],
    )


def _grade_of(value: float, table) -> str:
    for limit, grade in table:
        if value <= limit:
            return grade
    return table[-1][1]


def fetch_air(lat: float, lon: float) -> AirInfo:
    resp = requests.get(
        AIR_URL,
        params={"lat": lat, "lon": lon, "appid": API_KEY},
        timeout=10,
    )
    resp.raise_for_status()
    components = resp.json()["list"][0]["components"]
    pm10 = components["pm10"]
    pm25 = components["pm2_5"]
    pm10_grade = _grade_of(pm10, PM10_GRADES)
    pm25_grade = _grade_of(pm25, PM25_GRADES)
    overall = max(pm10_grade, pm25_grade, key=GRADE_ORDER.index)
    return AirInfo(pm10=pm10, pm25=pm25, pm10_grade=pm10_grade, pm25_grade=pm25_grade, overall_grade=overall)


def build_advice(weather: WeatherInfo, air: AirInfo):
    """날씨/미세먼지 상태를 종합해 (외출 판단, 마스크 필요 여부, 행동요령 목록)을 반환한다."""
    tips = []
    risk = 0  # 0: 양호, 1: 주의, 2: 자제 권장

    rainy = weather.main in ("Rain", "Drizzle")
    snowy = weather.main == "Snow"

    if rainy:
        tips.append("비가 오니 우산을 챙기세요.")
        risk = max(risk, 1)
    if snowy:
        tips.append("눈이 오니 방수 신발과 우산을 챙기고 빙판길을 주의하세요.")
        risk = max(risk, 1)
    if weather.main == "Thunderstorm":
        tips.append("천둥·번개가 있으니 외출을 자제하고 개방된 장소를 피하세요.")
        risk = 2

    if weather.temp >= 35:
        tips.append("폭염 수준입니다. 야외활동을 피하고 수분을 충분히 섭취하세요.")
        risk = 2
    elif weather.temp >= 33:
        tips.append("무더위가 예상됩니다. 한낮 야외활동을 줄이고 물을 자주 마시세요.")
        risk = max(risk, 1)
    elif weather.temp <= -15:
        tips.append("한파 수준입니다. 불필요한 외출을 피하고 노출 부위를 최소화하세요.")
        risk = 2
    elif weather.temp <= 0:
        tips.append("날씨가 춥습니다. 따뜻한 옷차림과 장갑, 목도리를 준비하세요.")
        risk = max(risk, 1)

    if weather.wind_speed >= 14:
        tips.append("강풍이 예상됩니다. 간판이나 공사장 근처를 피하세요.")
        risk = max(risk, 1)
    elif weather.wind_speed >= 9:
        tips.append("바람이 강하게 부니 모자나 우산이 뒤집히지 않게 주의하세요.")

    mask_needed = air.overall_grade in ("나쁨", "매우나쁨")
    if air.overall_grade == "매우나쁨":
        tips.append("미세먼지가 매우나쁨 수준입니다. 외출을 자제하고, 외출 시 KF94 이상 마스크를 착용하세요.")
        risk = 2
    elif air.overall_grade == "나쁨":
        tips.append("미세먼지가 나쁨 수준입니다. 외출 시 마스크를 착용하고 장시간 야외활동을 줄이세요.")
        risk = max(risk, 1)
    elif air.overall_grade == "보통":
        tips.append("미세먼지는 보통 수준입니다. 민감군(어린이·노약자)은 마스크 착용을 고려하세요.")
    else:
        tips.append("미세먼지가 좋음 수준으로 야외활동에 적합합니다.")

    if risk == 2:
        outing = "외출 자제 권장"
    elif risk == 1:
        outing = "외출 시 주의 필요"
    else:
        outing = "외출하기 좋은 날씨"

    return outing, mask_needed, tips


def _load_history() -> dict:
    if not HISTORY_FILE.exists():
        return {}
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def _save_history(history: dict):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


def _record_today(city: str, weather: WeatherInfo) -> dict:
    """오늘 조회한 날씨를 기록하고, 전체 이력을 반환한다. (내일 이후 비교에 사용)"""
    history = _load_history()
    city_history = history.setdefault(city, {})
    city_history[date.today().isoformat()] = {
        "temp": weather.temp,
        "main": weather.main,
        "description": weather.description,
    }
    _save_history(history)
    return history


def build_comparison(city: str, weather: WeatherInfo, history: dict) -> str | None:
    """어제 기록이 있으면 오늘과 비교한 문장을 만든다. 기록이 없으면 None."""
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    entry = history.get(city, {}).get(yesterday)
    if not entry:
        return None

    diff = weather.temp - entry["temp"]
    if abs(diff) < 1:
        return f"어제({entry['temp']:.1f}°C)와 비슷한 기온입니다."
    elif diff > 0:
        return f"어제보다 {diff:.1f}°C 더 덥습니다."
    else:
        return f"어제보다 {abs(diff):.1f}°C 더 춥습니다."


def get_report(city: str):
    lat, lon, name = geocode_city(city)
    weather = fetch_weather(lat, lon, name)
    air = fetch_air(lat, lon)
    outing, mask_needed, tips = build_advice(weather, air)

    history = _record_today(name, weather)
    comparison = build_comparison(name, weather, history)

    return weather, air, outing, mask_needed, tips, comparison
