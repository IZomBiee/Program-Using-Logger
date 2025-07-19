import csv
import os

class DataLoader:
    def __init__(self, starting_date: str = '', end_date: str = ''):
        self._csv_paths = []
        
        
        self.starting_date_days = 0 if starting_date == '' else self.date_to_days(starting_date)

        self.end_date_days = 10000000000000 if end_date == '' else self.date_to_days(end_date)

        self.path = '.\\logs'
        self._load_paths()

    def date_to_days(self, date:str) -> int:
        day, month, year = date.split('_')
        return int(day) + int(month) * 30 + int(year) * 365

    def _load_paths(self) -> list[str]:
        for folder in os.listdir(self.path):
            folder_abs_path = os.path.join(self.path, folder)
            if not os.path.isdir(folder_abs_path): continue
            
            for file in os.listdir(folder_abs_path):
                file_abs_path = os.path.join(folder_abs_path, file)
                name, extention = os.path.splitext(os.path.basename(file_abs_path))
                if extention == '.csv':
                    days = self.date_to_days(name)
                    if self.starting_date_days <= days <= self.end_date_days:
                        self._csv_paths.append(file_abs_path)
        return self._csv_paths
    
    def __iter__(self):
        for index in range(len(self)):
            yield self[index]

    def __getitem__(self, index:int):
        with open(self._csv_paths[index], 'r') as file:
            return list(csv.DictReader(file))
    
    def __len__(self) -> int:
        return len(self._csv_paths)
