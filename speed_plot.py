import sys
import os
import re
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


DPI = 96
WIDTH = 1200.0
HEIGHT = 900.0


# Check if the correct number of arguments are provided
if len(sys.argv) != 3:
    print("Usage: python3 plot_speedtest.py <speedtest_output_file> <output_folder>")
    sys.exit(1)

input_file = sys.argv[1]
output_folder = sys.argv[2]

# Create the output folder if it doesn't exist
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Read and parse the input file
with open(input_file, 'r') as f:
    data = f.read()

pattern = r'\[(.*?)\](?: Ping: (.*?) ms\nDownload: (.*?) Mbit/s\nUpload: (.*?) Mbit/s)?'
results = re.findall(pattern, data)

timestamps, pings, downloads, uploads = [], [], [], []

for result in results:
    ts, ping, download, upload = result
    timestamps.append(pd.to_datetime(ts, format='%Y-%m-%d %H:%M:%S'))
    pings.append(float(ping) if ping else 0)
    downloads.append(float(download) if download else 0)
    uploads.append(float(upload) if upload else 0)

# Create a DataFrame for easy plotting
# df = pd.DataFrame({'timestamp': timestamps, 'ping': pings, 'download': downloads, 'upload': uploads})
df = pd.DataFrame({'timestamp': timestamps, 'download': downloads, 'upload': uploads})
df.set_index('timestamp', inplace=True)

# Plot the data
fig, ax1 = plt.subplots(figsize=(WIDTH / DPI, HEIGHT / DPI))

ax1.set_xlabel('Time')
ax1.set_ylabel('Speed (Mbps)')
# ax1.plot(df.index, df['download'], label='Download Speed', color='b')
# ax1.plot(df.index, df['upload'], label='Upload Speed', color='r')
bar_width = 0.005
ax1.bar(df.index - pd.Timedelta(minutes=bar_width/2), df['download'], label='Download Speed', color='b', width=bar_width)
ax1.bar(df.index + pd.Timedelta(minutes=bar_width/2), df['upload'], label='Upload Speed', color='r', width=bar_width)
ax1.tick_params(axis='y')

# ax2 = ax1.twinx()
# ax2.set_ylabel('Ping (ms)')
# ax2.plot(df.index, df['ping'], label='Ping', color='g')
# ax2.tick_params(axis='y')

# Format the x-axis
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M:%S'))
fig.autofmt_xdate(rotation=45)

# Add a legend
lines1, labels1 = ax1.get_legend_handles_labels()
# lines2, labels2 = ax2.get_legend_handles_labels()
# ax1.legend(lines1 + lines2, labels1 + labels2, loc='best')
ax1.legend(lines1, labels1, loc='best')

# Save the plot to the output folder
output_file = os.path.join(output_folder, f'speedtest_plot_{timestamps[0]}.png')
plt.tight_layout()
plt.savefig(output_file, dpi=DPI)
print(f"Plot saved to {output_file}")
