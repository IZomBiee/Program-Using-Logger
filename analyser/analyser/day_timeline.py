def main():
    pass

from datetime import datetime
from matplotlib import pyplot as plt
from .data_loader import DataLoader

date = input("Write date (for ex. 06_03_2023 or nothing to current day) -> ")
if date == '':
    date = datetime.now().strftime("%d_%m_%Y")

data = DataLoader(date, date)
records = data[0]

records = list(filter(lambda x: x['duration'] is not None and x['duration'] > 15, records))
records = records[::-1]

durations = [record['duration'] for record in records]
names = [record['name'] for record in records]

total_time = sum(durations)
timeline_length = 100
normalized_lengths = [int((d / total_time) * timeline_length) for d in durations]

for i in range(len(normalized_lengths)):
    if durations[i] > 0 and normalized_lengths[i] == 0:
        normalized_lengths[i] = 1

while sum(normalized_lengths) > timeline_length:
    idx = normalized_lengths.index(max(normalized_lengths))
    normalized_lengths[idx] -= 1
while sum(normalized_lengths) < timeline_length:
    idx = normalized_lengths.index(max(normalized_lengths))
    normalized_lengths[idx] += 1

unique_apps = list(dict.fromkeys(names))
colormap = plt.get_cmap('tab20')
color_map = {name: colormap(i / len(unique_apps)) for i, name in enumerate(unique_apps)}

fig, ax = plt.subplots(figsize=(12, 2))

start = 0
for name, length in zip(names, normalized_lengths):
    ax.barh(0, length, left=start, color=color_map[name], edgecolor='white')
    start += length

ax.set_yticks([])
ax.set_xlim(0, timeline_length)
ax.set_title(f"App Usage Timeline for {date.replace('_', '.')}")

handles = []
added = set()
for name in names:
    if name not in added:
        handles.append(plt.Line2D([0], [0], color=color_map[name], lw=6, label=name))
        added.add(name)
ax.legend(handles=handles, bbox_to_anchor=(1.01, 1), loc='upper left')

plt.tight_layout()
plt.show()
