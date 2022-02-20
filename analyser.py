from datetime import datetime, timedelta
from math import floor


class DataAnalyser:
    def __init__(self, data_list, data_preference: str, data_threshold: int, use_median = False):
        self._dtype = data_preference
        self._thold = data_threshold
        if use_median.lower() == "false":
            self._use_median = False
        else:
            self._use_median = True
        self._data_list = self.__sort_data(data_list)
        
    def pack_into_weeks(self):
        print("[INFO] Sorting the data by week...", end=" ")
        data_list = list(map(lambda data: self.__separate_by_week(data), self._data_list))
        print("Done!")
        
        packed_data = {"weeks": [], "prices": []}
        print(f"[INFO] Packing week data...", end=" ")
        
        for week in range(52):
            dtm = datetime.fromisocalendar(1970, week + 2, 1)
            packed_data["weeks"].append(dtm)
            if self._use_median:
                price_list = []
                for data in data_list:
                    if data[week] is not None:
                        price_list.append(data[week])
                        
                if len(price_list) >= self._thold:
                    price_list = sorted(price_list)
                    index = floor(len(price_list)/2)
                    if len(price_list)%2 == 0:
                        price = round((price_list[index] + price_list[index - 1])/2, 2)
                    else:
                        price = round(price_list[index], 2)
                    packed_data["prices"].append(price)
            else:
                occurances = sum = 0
                for data in data_list:
                    if data[week] is not None:
                        sum += data[week]
                        occurances += 1
                        
                if occurances >= self._thold:
                    packed_data["prices"].append(round(sum/occurances, 2))
        
        print(f"Packing {len(data_list)} entries complete!")
        return packed_data
        
    def __separate_by_week(self, data):
        prices = [None] * 52
        average = self.__calculate_mean(data)
        week_number = (datetime.utcfromtimestamp(float(data[0]["date"]) / 1000) + timedelta(hours=3)).isocalendar()[1] - 1
        if week_number == 52: week_number = 0
        for point in data:
            relative_price = self.__to_relative_price(point, average)
            prices[week_number] = relative_price
            week_number = (week_number + 1) % 52
        return prices
    
    def pack_into_months(self):
        print("[INFO] Sorting the data by month...", end=" ")
        data_list = list(map(lambda data: self.__separate_by_month(data), self._data_list))
        print("Done!")
        
        packed_data = {"months": [], "prices": []}
        print("[INFO] Packing month data...", end=" ")
        
        for month in range(12):
            dtm = datetime(1970, month + 1, 1)
            packed_data["months"].append(dtm)
            if self._use_median:
                price_list = []
                for data in data_list:
                    if len(data[month]) > 0:
                        price_list.extend(data[month])
                        
                if len(price_list) >= self._thold:
                    price_list = sorted(price_list)
                    index = floor(len(price_list)/2)
                    if len(price_list)%2 == 0:
                        price = round((price_list[index] + price_list[index - 1])/2, 2)
                    else:
                        price = round(price_list[index], 2)
                    packed_data["prices"].append(price)
            else:
                occurances = overall_occurances = price_sum = 0
                for data in data_list:
                    if len(data[month]) > 0:
                        price_sum += sum(data[month])
                        overall_occurances += len(data[month])
                        occurances += 1
                        
                if occurances >= self._thold:
                    packed_data["prices"].append(round(price_sum/overall_occurances, 2))
                    
        print(f"Packing {len(data_list)} entries complete!")
        return packed_data
    
    def __separate_by_month(self, data):
        prices = []
        for i in range(12):
            prices.append([])
        average = self.__calculate_mean(data)
        for point in data:
            month = (datetime.utcfromtimestamp(float(point["date"]) / 1000) + timedelta(hours=3)).month - 1
            relative_price = self.__to_relative_price(point, average)
            prices[month].append(relative_price)
        return prices
    
    def __sort_data(self, data_list):
        new_data_list = []
        for data in data_list:
            key = self._dtype.lower()
            for i in range(floor(len(data)/52)):
                if data[0].get("value") is not None and key == "avg" or data[0].get(key) is not None:
                    new_data_list.append(data[i*52:(i+1)*52])
                
        return new_data_list
    
    def __to_relative_price(self, point, average):
        key = self._dtype.lower()
        if point.get("value") is not None and key == "avg":
            key = "value"

        relative_pricing = (int(point[key]) / average) * 100
        return round(relative_pricing, 2)

    def __calculate_median(self, data):
        key = self._dtype.lower()
        price_list = []
        if data[0].get("value") is not None and key == "avg": 
            key = "value"
        for point in data:
            price_list.append(int(point[key]))
        price_list = sorted(price_list)
        return round(price_list[floor(len(price_list)/2)], 2)

    def __calculate_mean(self, data):
        key = self._dtype.lower()
        sum = count = 0
        if data[0].get("value") is not None and key == "avg": 
            key = "value"  
        for point in data:
            sum += int(point[key])
            count += 1
        return round(sum/count, 2)