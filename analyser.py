from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor


class DataAnalyser:
    def __init__(self, data_list, data_preference: str, data_threshold: int):
        self._data_list = data_list
        self._data_pref = data_preference
        self._threshold = data_threshold
        
    def pack_data(self):
        print("[INFO] Formatting the data...", end=" ")
        print(len(self._data_list))
        with ThreadPoolExecutor(max_workers=20) as exec:
            self._data_list = list(exec.map(self.__format_data, self._data_list))
        packed_data = {"dates": [], "prices": []}
        print("Done!")
        print("[INFO] Packing the data...", end=" ")
        for week in range(0,53):
            occurances = overall_occurances = sum = 0
            for data in self._data_list:
                if data[0][week] is not None:
                    overall_occurances += data[1][week]
                    sum += data[0][week]
                    occurances += 1
            if occurances >= self._threshold:
                packed_data["dates"].append(datetime.fromisocalendar(year=2018, week=week, day=1))
                packed_data["prices"].append(round(sum/overall_occurances, 2))
        print(f"Packing {len(self._data_list)} entries complete!")
        return packed_data

    def __format_data(self, data):
        prices = [None] * 53
        occurances = [None] * 53
        previous_year = 0
        for point in data:
            current_year, current_week, _ = (datetime.utcfromtimestamp(int(point["date"]) / 1000) + timedelta(hours=3)).isocalendar()
            
            if current_year > previous_year: 
                average = self.__calculate_average(data, current_year)
                if average == -1: break
                previous_year = current_year
            relative_pricing = self.__to_relative_price(average, point)
            if prices[current_week - 1] is None:
                prices[current_week - 1] = relative_pricing
                occurances[current_week - 1] = 1
            else:
                prices[current_week - 1] += relative_pricing
                occurances[current_week - 1] += 1
        return (prices, occurances)
    
    def __to_relative_price(self, average, point):
        if point.get("value") is not None and self._data_pref.lower() == "avg":
            relative_pricing = (int(point["value"]) / average) * 100
        else:
            if self._data_pref.lower() == "avg":
                relative_pricing = (int(point["avg"]) / average) * 100
            elif self._data_pref.lower() == "min":
                relative_pricing = (int(point["min"]) / average) * 100
            elif self._data_pref.lower() == "max":
                relative_pricing = (int(point["max"]) / average) * 100
        return relative_pricing

    def __calculate_average(self, data, year):
        def process_points(key):
            sum = occurances = 0
            flag = False
            for point in data:
                if (datetime.utcfromtimestamp(int(point["date"]) / 1000) + timedelta(hours=3)).year == year:
                    flag = True
                    sum += int(point[key])
                    occurances += 1
                elif flag: break
            return round(sum/occurances, 2)
        
        if data[0].get("value") is not None and self._data_pref.lower() != "avg":
            return -1
            
        if self._data_pref.lower() == "avg":
            if data[0].get("value"):
                return process_points("value")
            else:
                return process_points("avg")
        elif self._data_pref.lower() == "min":
            return process_points("min")
        elif self._data_pref.lower() == "max":
            return process_points("max")