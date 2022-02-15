from datetime import datetime, timedelta
from math import floor


class DataAnalyser:
    def __init__(self, data_list, data_preference: str, data_threshold: int):
        self._dtype = data_preference
        self._thold = data_threshold
        self._data_list = self.sort_data(data_list)
        
    def pack_into_weeks(self):
        print("[INFO] Formatting the data...", end=" ")
        data_list = list(map(lambda data: self.format_data_weeks(data), self._data_list))
        print("Done!")
        
        packed_data = {"weeks": [], "prices": []}
        print("[INFO] Packing the data...", end=" ")
        for week in range(52):
            occurances = sum = 0
            for data in data_list:
                if data[week] is not None:
                    sum += data[week]
                    occurances += 1
            if occurances >= self._thold:
                dtm = datetime.fromisocalendar(1970, week + 2, 1)
                packed_data["weeks"].append(dtm)
                packed_data["prices"].append(round(sum/occurances, 2))
        print(f"Packing {len(data_list)} entries complete!")
        return packed_data

    def pack_into_months(self):
        print("[INFO] Formatting the data...", end=" ")
        data_list = list(map(lambda data: self.format_data_months(data), self._data_list))
        print("Done!")
        
        packed_data = {"months": [], "prices": []}
        print("[INFO] Packing the data...", end=" ")
        for month in range(12):
            occurances = overall_occurances = sum = 0
            for data in data_list:
                if data[0][month] is not None:
                    sum += data[0][month]
                    overall_occurances += data[1][month]
                    occurances += 1
            if occurances >= self._thold:
                dtm = datetime(1970, month + 1, 1)
                packed_data["months"].append(dtm)
                packed_data["prices"].append(round(sum/overall_occurances, 2))
        print(f"Packing {len(data_list)} entries complete!")
        return packed_data
        
    def format_data_weeks(self, data):
        prices = [None] * 52
        average = self.calculate_average(data)
        week_number = (datetime.utcfromtimestamp(float(data[0]["date"]) / 1000) + timedelta(hours=3)).isocalendar()[1] - 1
        if week_number == 52: week_number = 0
        for point in data:
            relative_price = self.to_relative_price(point, average)
            prices[week_number] = relative_price
            week_number = (week_number + 1) % 52
        return prices
    
    def format_data_months(self, data):
        prices = [None] * 12
        occurances = [None] * 12
        average = self.calculate_average(data)
        for point in data:
            month = (datetime.utcfromtimestamp(float(point["date"]) / 1000) + timedelta(hours=3)).month - 1
            relative_price = self.to_relative_price(point, average)
            if prices[month] is None:
                prices[month] = relative_price
                occurances[month] = 1
            else:
                prices[month] += relative_price
                occurances[month] += 1
        return (prices, occurances)
    
    def sort_data(self, data_list):
        new_data_list = []
        for data in data_list:
            key = self._dtype.lower()
            for i in range(floor(len(data)/52)):
                if data[0].get("value") is not None and key == "avg" or data[0].get(key) is not None:
                    new_data_list.append(data[i*52:(i+1)*52])
                
        return new_data_list
    
    def to_relative_price(self, point, average):
        key = self._dtype.lower()
        if point.get("value") is not None and key == "avg":
            key = "value"

        relative_pricing = (int(point[key]) / average) * 100
        return round(relative_pricing, 2)

    def calculate_average(self, data):
        key = self._dtype.lower()
        sum = count = 0
        if data[0].get("value") is not None and key == "avg": 
            key = "value"
        
        for point in data:
            sum += int(point[key])
            count += 1
        return round(sum/count, 2)