import os
import httpx
from fastapi import HTTPException
from typing import Dict, Any
from datetime import datetime, timedelta

async def fetch_wave_data(point: str) -> Dict[str, Any]:
    coords = os.getenv(f"REACT_APP_{point.upper()}_COORDS", "000,000")
    latitude, longitude = coords.split(',')

    print(f"Fetching wave data for point: {point}")
    print(f"Coordinates: {coords}")
    print(f"Latitude: {latitude}, Longitude: {longitude}")

    base_url = "https://marine-api.open-meteo.com/v1/marine"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": ["wave_height", "wave_direction", "wind_wave_height", "wind_wave_direction", "swell_wave_height", "swell_wave_direction"],
        "timezone": "Asia/Tokyo"
    }

    if longitude == '000':
        raise HTTPException(status_code=400, detail="Invalid longitude")

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(base_url, params=params)
            response.raise_for_status()
            full_data = response.json()["hourly"]

            # 3時間ごとのデータを抽出
            three_hourly_data = {key: value[::3] for key, value in full_data.items()}

            # タイムスタンプを日本時間の読みやすい形式に変換
            time_data = full_data["time"][::3]
            formatted_time = []
            for time_str in time_data:
                dt = datetime.fromisoformat(time_str)
                formatted_time.append(dt.strftime("%m/%d %H:%M"))

            three_hourly_data["formatted_time"] = formatted_time

            return three_hourly_data
        except httpx.HTTPStatusError as e:
            print(f"HTTP error occurred: {e}")
            raise HTTPException(status_code=e.response.status_code, detail=str(e))
        except Exception as e:
            print(f"An error occurred: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")
