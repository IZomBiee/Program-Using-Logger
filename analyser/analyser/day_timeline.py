from datetime import datetime

import matplotlib.ticker as ticker
from matplotlib import pyplot as plt

from .data_loader import DataLoader


def main():
    date = input("Write date (for ex. 06_03_2023 or nothing to current day) -> ")
    if date == "":
        date = datetime.now().strftime("%d_%m_%Y")

    data = DataLoader(date, date)
    if len(data) == 0 or not data[0]:
        print("No data found for this date.")
        return

    records = data[0]

    # Filter out short durations and reverse list
    records = list(
        filter(lambda x: x["duration"] is not None and x["duration"] > 60, records)
    )

    if not records:
        print("No records left after filtering.")
        return

    names = [record["name"] for record in records]
    durations = [record["duration"] for record in records]

    start_times = []
    for record in records:
        t = datetime.strptime(record["time"], "%H:%M:%S")
        start_times.append(t.hour * 3600 + t.minute * 60 + t.second)

    # --- 1. PREPARE RAW DATA (No filtering yet) ---
    parsed = []
    for record in records:
        t = datetime.strptime(record["time"], "%H:%M:%S")
        start_sec = t.hour * 3600 + t.minute * 60 + t.second
        parsed.append({"name": record["name"], "start": start_sec})

    # Sort by time to ensure continuity
    parsed.sort(key=lambda x: x["start"])

    if not parsed:
        print("No records to display.")
        return

    # --- 2. CLUSTERING & SNAP-TO-NEXT ---
    # THRESHOLD: Apps used for less than this many seconds are "absorbed"
    # into the previous activity to keep the graph clean.
    SMALL_APP_THRESHOLD = 240

    clean_blocks = []
    for i in range(len(parsed)):
        name = parsed[i]["name"]
        start = parsed[i]["start"]

        # Determine when this block ends: it ends exactly when the NEXT one starts
        if i < len(parsed) - 1:
            end = parsed[i + 1]["start"]
        else:
            # For the very last record of the day, use its original duration
            end = start + records[i]["duration"]

        duration = end - start

        # If this app was used for a tiny amount of time, merge it into the previous block
        if duration < SMALL_APP_THRESHOLD and clean_blocks:
            clean_blocks[-1]["end"] = end
        else:
            # If it's the same app as the last block, just extend the last block
            if clean_blocks and clean_blocks[-1]["name"] == name:
                clean_blocks[-1]["end"] = end
            else:
                clean_blocks.append({"name": name, "start": start, "end": end})

    # --- 3. PLOTTING ---
    unique_apps = list(dict.fromkeys([b["name"] for b in clean_blocks]))
    colormap = plt.get_cmap("tab20")
    color_map = {
        name: colormap(i / max(1, len(unique_apps) - 1))
        for i, name in enumerate(unique_apps)
    }

    fig, ax = plt.subplots(figsize=(12, 2.5))

    for block in clean_blocks:
        duration = block["end"] - block["start"]
        # 1. Draw the colored bar
        ax.barh(
            0,
            duration,
            left=block["start"],
            color=color_map[block["name"]],
            edgecolor="none",
        )

        # 2. ADD LABELS: Only if the block is wide enough (e.g., > 4 minutes / 240s)
        # We use your SMALL_APP_THRESHOLD here so labels only appear on non-merged blocks
        if duration >= SMALL_APP_THRESHOLD:
            text_x = block["start"] + (duration / 2)
            ax.text(
                text_x,
                0,
                block["name"],
                ha="center",
                va="center",
                color="white",
                fontweight="bold",
                rotation=90,
                fontsize=8,
                clip_on=True,
            )

    ax.set_yticks([])
    ax.set_title(f"Continuous App Usage for {date.replace('_', '.')}")

    # Set limits from very first start to very last end
    ax.set_xlim(clean_blocks[0]["start"], clean_blocks[-1]["end"])

    # --- 4. FORMATTING ---
    def format_clock_time(value, tick_number):
        hours = int((value // 3600) % 24)
        minutes = int((value % 3600) // 60)
        return f"{hours:02d}:{minutes:02d}"

    ax.xaxis.set_major_formatter(ticker.FuncFormatter(format_clock_time))
    ax.xaxis.set_major_locator(ticker.MaxNLocator(12))

    # Legend (optional now that you have labels)
    handles = [
        plt.Line2D([0], [0], color=color_map[name], lw=6, label=name)
        for name in unique_apps
    ]
    ax.legend(
        handles=handles,
        bbox_to_anchor=(1.01, 1),
        loc="upper left",
        fontsize="small",
        ncol=1,
    )

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
