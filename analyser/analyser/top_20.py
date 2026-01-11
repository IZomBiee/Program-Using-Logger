def main():
    pass

from matplotlib import pyplot as plt
from .data_loader import DataLoader

data = DataLoader(input("Write starting date (for ex. 06_03_2023 or nothing) -> "),
                  input("Write end date (for ex. 02_05_2026 or nothing) -> "))

data_sums = {}
for records in data:
    for record in records:
        try:
            if record['duration'] is not None:
                if record['name'] in data_sums:
                    data_sums[record['name']] += float(record['duration'])
                else:
                    data_sums[record['name']] = float(record['duration'])
        except KeyError:
            continue

data_sums = dict(
    sorted(
        {
            name: round(seconds / 3600, 2)
            for name, seconds in data_sums.items()
        }.items(),
        key=lambda item: item[1],
        reverse=True
    )
)

top_n = 20
names = list(data_sums.keys())[:top_n]
hours = list(data_sums.values())[:top_n]

plt.figure(figsize=(12, 8))
bars = plt.barh(names, hours, color='skyblue')
plt.xlabel("Time Spent (hours)")
plt.title(f"Top {top_n} Applications by Usage Time")
plt.gca().invert_yaxis()
plt.tight_layout()

for bar in bars:
    width = bar.get_width()
    plt.text(width + 1, bar.get_y() + bar.get_height()/2,
             f'{width:.2f}h', va='center')

plt.show()
