from datetime import datetime
import re
import sys

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Plot config
TICK_SIZE = 1.0
XLABEL = 'Timestamp'
YLABEL = 'Latency (ms)'
DPI = 96
WIDTH = 1200.0
HEIGHT = 900.0


def render(in_file, out_folder):
    with open(in_file) as file:
        content = file.read().strip()
        data = _parse(content)
        _draw_plot(title=in_file, out_folder=out_folder, data=data)


def _parse_times(lines):
    try:
        timestamps = [re.search(r"\[([^\]]+)\]", line).group(1) for line in lines]
    except Exception as e:
        print("You may need to clean up the ping plot file first")

    timestamps = [datetime.fromtimestamp(float(line)) for line in timestamps]
    return timestamps


def _parse_ping(lines):
    timestamps = _parse_times(lines)
    latencies = []

    for line in lines:
        try:
            latency = re.search(r"time=(\d+\.?\d*) ms", line).group(1)
        except Exception as e:
            latency = 0

        latencies.append(float(latency))

    return zip(timestamps, latencies)


def _parse(content):
    lines = content.split('\n')[1:]
    data = _parse_ping(lines)

    return data


def _draw_plot(title, out_folder, data):
    timestamps, latencies = list(zip(*data))
    datenums = mdates.date2num(timestamps)
    # colors = ['r' if l <= 0 else 'b' for l in latencies]

    fig, ax = plt.subplots(figsize=(WIDTH / DPI, HEIGHT / DPI))
    ax.set(title=title, xlabel=XLABEL, ylabel=YLABEL)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
    ax.bar(datenums[:], latencies[:], width=0.00002)
    ax.legend()

    plt.savefig(f'{out_folder}/{datetime.now()}.png', dpi=DPI)  # noqa


if __name__ == '__main__':
    render(
        in_file=sys.argv[1],
        out_folder=sys.argv[2],
    )
