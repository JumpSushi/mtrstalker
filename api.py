import requests
from typing import Dict, Optional, List
from concurrent.futures import ThreadPoolExecutor

class MTRAPI:
    KTL_STATIONS = {
        "WHA", "HOM", "YMT", "MOK", "PRE", "SKM", "KOT",
        "LOF", "WTS", "DIH", "CHH", "KOB", "NTK", "KWT", 
        "LAT","YAT","TIK"
    }
    STATION_NAMES = {
        "WHA": "Whampoa", "HOM": "Ho Man Tin", "YMT": "Yau Ma Tei", "MOK": "Mong Kok", "PRE": "Prince Edward", "SKM": "Shek Kip Mei", "KOT": "Kowloon Tong",
        "LOF": "Lok Fu", "WTS": "Wong Tai Sin", "DIH": "Diamond Hill", "CHH": "Choi Hung", "KOB": "Kowloon Bay", "NTK": "Ngau Tau Kok", "KWT": "Kwun Tong", "LAT": "Lam Tin", "YAT": "Yau Tong", "TIK": "Tiu Keng Leng"
        
    }

    def __init__(self):
        self.url = "https://rt.data.gov.hk/v1/transport/mtr/getSchedule.php"
        self.params = {
            "station": "WHA",
            "lang": "en"
        }
    def get_station_data(self, station: str) -> Optional[Dict]:
        params = {
            "line": "KTL",
            "sta": station,
        }
    
        try: 
            response = requests.get(self.url, params=params, timeout=5)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException:
            return None
        
    def process_train_data(self, station: str, data: Dict) -> List[Dict]:
        trains = []
        if not data or "data" not in data:
            return trains
        station_key = f"KTL-{station}"
        if station_key not in data["data"]:
            return trains
        station_data = data["data"][station_key]
        for direction in ["UP", "DOWN"]:  # up is tkl, down is wha
            if direction in station_data:
                for train in station_data[direction]:
                    if "time" in train and train.get("valid") == "Y":
                        trains.append({
                            "direction": direction,
                            "destination": self.STATION_NAMES.get(train["dest"], train["dest"]),
                            "platform": train.get("plat", ""),
                            "arrival_time": train["time"],
                            "minutes": train.get("ttnt", ""),
                            "current_station": self.STATION_NAMES[station],
                            "sequence": train.get("seq", "")
                        })
        return trains

    def get_ALL_trains(self) -> List[Dict]:
        all_trains = []
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(self.get_station_data, station) for station in self.KTL_STATIONS]
            for station, future in zip(self.KTL_STATIONS, futures):
                try:
                    data = future.result()
                    if data:
                        trains = self.process_train_data(station, data)
                        all_trains.extend(trains)
                except Exception:
                    continue
        return all_trains
