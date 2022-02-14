import asyncio
from datetime import datetime, timedelta
from isoweek import Week


class DataAnalyser:
    def __init__(self, data_list, data_preference: str, data_threshold: int):
        self._data_list = data_list
        self._dtype = data_preference
        self._thold = data_threshold
        
    def pack_data(self):
        print("[INFO] Formatting the data...", end=" ")
        loop = asyncio.get_event_loop()
        self._data_list = list(map(lambda data: self.format_data(data), self._data_list))
        loop.close()
        print("Done!")
        
        packed_data = {"dates": [], "prices": []}
        print("[INFO] Packing the data...", end=" ")
        for week in range(0,53):
            occurances = sum = 0
            for data in self._data_list:
                if data[0][week] is not None:
                    sum += data[0][week]
                    occurances += data[1][week]
            if occurances >= self._thold:
                date = Week(2018, week + 1).monday()
                packed_data["dates"].append(date)
                packed_data["prices"].append(round(sum/occurances, 2))
        print(f"Packing {len(self._data_list)} entries complete!")
        return packed_data

    def format_data(self, data):
        prices = [None] * 53
        occurances = [None] * 53
        average = self.calculate_average(data)
        for point in data:
            point_datetime = (datetime.utcfromtimestamp(float(point["date"]) / 1000) + timedelta(hours=3))
            week_number = Week.withdate(point_datetime).year_week()[1] - 1
            relative_price = self.to_relative_price(point, average)
            if prices[week_number] is None:
                prices[week_number] = relative_price
                occurances[week_number] = 1
            else:
                prices[week_number] += relative_price
                occurances[week_number] += 1
        return (prices, occurances)
    
    def to_relative_price(self, point, average):
        key = self._dtype
        if point.get("value") is not None and key.lower() == "avg":
            key = "value"
        if point.get(key.lower()) is not None:
            relative_pricing = (int(point[key.lower()]) / average) * 100
            return round(relative_pricing, 2)

    def calculate_average(self, data):
        key = self._dtype
        sum = count = 0
        if data[0].get("value") is not None and key.lower() == "avg": 
            key = "value"
        if data[0].get(key.lower()) is not None:
            for point in data:
                sum += int(point[key.lower()])
                count += 1
        else:
            return None
        return round(sum/count, 2)