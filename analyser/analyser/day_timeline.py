from datetime import datetime
from matplotlib import pyplot as plt
import matplotlib.ticker as ticker
from .data_loader import DataLoader

def main():
    date = input("Write date (for ex. 06_03_2023 or nothing to current day) -> ")
    if date == '':
        date = datetime.now().strftime("%d_%m_%Y")

    data = DataLoader(date, date)
    if len(data) == 0 or not data[0]:
        print("No data found for this date.")
        return
        
    records = data[0]

    # Filter out short durations and reverse list
    records = list(filter(lambda x: x['duration'] is not None and x['duration'] > 60, records))

    if not records:
        print("No records left after filtering.")
        return

    names = [record['name'] for record in records]
    durations = [record['duration'] for record in records]
    
    # --- GET THE REAL STARTING TIME ---
    # Take the time string of the very first record to be plotted
    first_time_str = records[0]['time']
    first_t = datetime.strptime(first_time_str, "%H:%M:%S")
    # Convert it into total seconds since midnight
    start_time_seconds = first_t.hour * 3600 + first_t.minute * 60 + first_t.second

    # Merge adjacent blocks of the same app
    merged_names = []
    merged_durations = []
    
    if names:
        merged_names.append(names[0])
        merged_durations.append(durations[0])
        
        for i in range(1, len(names)):
            if names[i] == merged_names[-1]:
                merged_durations[-1] += durations[i]
            else:
                merged_names.append(names[i])
                merged_durations.append(durations[i])

    unique_apps = list(dict.fromkeys(merged_names))
    colormap = plt.get_cmap('tab20')
    color_map = {name: colormap(i / max(1, len(unique_apps)-1)) for i, name in enumerate(unique_apps)}

    fig, ax = plt.subplots(figsize=(12, 2))

    # --- PLOT CONTINUOUSLY WITHOUT GAPS ---
    # Start drawing at the real clock time instead of 0
    current_start = start_time_seconds
    for name, length in zip(merged_names, merged_durations):
        ax.barh(0, length, left=current_start, color=color_map[name], edgecolor='white')
        current_start += length  # Slide the next bar directly next to this one

    ax.set_yticks([])
    ax.set_title(f"App Usage Timeline for {date.replace('_', '.')}")
    # Fit the view exactly to our drawn timeline
    ax.set_xlim(start_time_seconds, current_start)

    # Convert the seconds on the x-axis back into HH:MM text
    def format_clock_time(value, tick_number):
        hours = int((value // 3600) % 24)
        minutes = int((value % 3600) // 60)
        return f"{hours:02d}:{minutes:02d}"
        
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(format_clock_time))
    ax.xaxis.set_major_locator(ticker.MaxNLocator(12)) # Automatically pick ~12 evenly spaced tick marks

    handles = []
    added = set()
    for name in merged_names:
        if name not in added:
            handles.append(plt.Line2D([0], [0], color=color_map[name], lw=6, label=name))
            added.add(name)
            
    ax.legend(handles=handles, bbox_to_anchor=(1.01, 1), loc='upper left')

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()