# Deployment with Docker on RPi

```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

mkdir -p ~/influxdb/data
mkdir -p ~/influxdb/config
mkdir -p ~/grafana/data

docker run -d   --name influxdb -p 8086:8086 -v ~/influxdb/data:/var/lib/influxdb -v ~/influxdb/config:/etc/influxdb arm32v7/influxdb
docker exec -it INFLUX_CONTAINER_ID influx -execute 'CREATE DATABASE speedtest'

echo "UID: $(id -u)";echo "GID: $(id -g)"
sudo chown -R $USER:$USER ~/grafana/data
docker run -d --name grafana --user UID:GID -p 3000:3000 -v ~/grafana/data:/var/lib/grafana --env GF_FEATURE_TOGGLES_ENABLE=publicDashboards grafana/grafana

crontab -e
# */10 * * * * /home/pi/dev/ping_plot/.venv/bin/python3 /home/pi/dev/ping_plot/speedtest_cli_influxdb.py

cd /tmp
wget https://bin.equinox.io/c/4VmDzA7iaHb/ngrok-stable-linux-arm.zip
unzip ngrok-stable-linux-arm.zip
sudo mv ngrok /usr/local/bin
vi /home/pi/ngrok.yml

    # authtoken: TOKEN
    # tunnels:
    #   grafana:
    #     proto: http
    #     addr: 3000

# Run ngrok in background
tmux new-session -s ngrok_session
# In tmux session. After this press Ctrl+B and then D to detach from tmux session.
ngrok start -config ~/ngrok.yml grafana
# To reattach
tmux attach-session -t ngrok_session

```