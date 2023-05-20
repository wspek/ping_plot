import os
import csv
from datetime import datetime
import subprocess
import time

from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
import logging

INFLUX_DB_TOKEN = 'W9ulA5wf4nIfTay7A9rhlxSb9lE4H6e1wgQgPqMW2QR0wI-gurv6il2Quu6UMN4BgDa-i6xEmgaiJaWHWDedvQ=='
ORG = "Spek"
BUCKET = "speedtest"
LOG_FILE = '/var/log/speedtest-cli.log'

logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def run_speedtest():
    logging.info('Running speedtest')

    try:
        output = subprocess.check_output("speedtest-cli --csv", shell=True).decode()
        logging.info('Speedtest completed successfully')
        return output.strip().split(',')
    except subprocess.CalledProcessError as e:
        logging.error(f'Speedtest failed with error: {e}')
        return ['', '', '', datetime.now().isoformat(), '0.0', '0.0', '0.0', '0.0', '', '']


def write_to_csv(data, filename='speedtest_results.csv'):
    file_exists = os.path.isfile(filename)
    with open(filename, 'a') as csvfile:
        headers = ['Server ID', 'Sponsor', 'Server Name', 'Timestamp', 'Distance', 'Ping', 'Download', 'Upload', 'Share', 'IP Address']
        writer = csv.DictWriter(csvfile, fieldnames=headers)

        if not file_exists:
            writer.writeheader()

        writer.writerow({headers[i]: data[i] for i in range(len(headers))})


def get_influxdb_container_ip():
    container_name = "influxdb"  # Replace this with the name you've given to your InfluxDB container

    try:
        cmd = f"docker inspect {container_name} --format '{{{{.NetworkSettings.IPAddress}}}}'"
    except subprocess.CalledProcessError:
        raise RuntimeError("Failed to get InfluxDB container ID. Are you sure Docker is installed?")

    ip_address = subprocess.check_output(cmd, shell=True).decode().strip()
    return ip_address


def write_to_influxdb(data):
    logging.info('Writing to influxdb')

    url = f"http://{get_influxdb_container_ip()}:8086"

    client = InfluxDBClient(url=url, token=INFLUX_DB_TOKEN)
    write_api = client.write_api(write_options=SYNCHRONOUS)

    point = Point("speedtest") \
        .tag("server_id", data[0]) \
        .tag("sponsor", data[1]) \
        .tag("server_name", data[2]) \
        .tag("timestamp", data[3]) \
        .field("distance", float(data[4])) \
        .field("ping", float(data[5])) \
        .field("download", float(data[6])) \
        .field("upload", float(data[7])) \
        .time(time.time_ns(), WritePrecision.NS)

    write_api.write(bucket=BUCKET, org=ORG, record=point)
    client.close()

    logging.info('Writing to influxdb done')


def run():
    logging.info('*** START ***')

    result = run_speedtest()
    logging.info(result)

    # result = ['41338', 'Cooperativa de Colonia Caroya y Jesus Maria Ltda', 'Colonia Caroya', '2023-04-15T18:41:54.708922Z', '663.0926436032137', '78.865', '19914755.186711118', '2171532.6305631828', '', '181.102.18.27']
    write_to_influxdb(result)

    logging.info('*** END ***')


if __name__ == '__main__':
    run()
