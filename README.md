### Setup
```
python -m venv .venv
.venv/Scripts/activate
python -m pip install -r requirements.txt
```

### Run Server
```
python main.py
```

### Setup Cassandra
```
mkdir -p cassandra_data/data
mkdir -p cassandra_data/commitlog
mkdir -p cassandra_data/saved_caches
mkdir -p config/cassandra.yaml
docker pull cassandra:latest
```

```
docker ps  # check that Cassandra is running
docker stop cassandra  # gracefully stop
docker restart cassandra  # start
docker rm -f cassandra  # remove Cassandra
docker exec -it cassandra cqlsh  # Run CQL
```

### Start Cassandra (Powershell)
```
docker run --name cassandra `
  -d `
  -p 9042:9042 `
  -v $PWD\config\cassandra.yaml:/etc/cassandra/cassandra.yaml `
  -v $PWD\data\cassandra:/var/lib/cassandra `
  cassandra
```

### Start Humio (Powershell)
```
docker run --name humio `
  -d `
  -p 8080:8080 `
  -p 8443:8443 `
  --ulimit="nofile=250000:250000" `
  --stop-timeout 300 `
  -v C:\Users\bfrem\Documents\Projects\carcassonne\humio_data:/data `
  --env-file=C:\Users\bfrem\Documents\Projects\carcassonne\config\logscale.env `
  humio/humio-single-node-demo:latest
```

### Run Loki
```
docker run -d `
  --name loki `
  -p 3100:3100 `
  -v $PWD\config\loki-config.yaml:/etc/loki/local-config.yaml `
  -v $PWD\data\loki\loki:/tmp/loki `
  -v $PWD\data\loki\compactor:/tmp/compactor `
  -v $PWD\data\loki\wal:/wal `
  grafana/loki:2.8.2 `
  --config.file=/etc/loki/local-config.yaml
```

### Run Grafana
```
docker run -d `
  -p 3000:3000 `
  --name grafana `
  -v $PWD\data\grafana:/var/lib/grafana `
  -e "GF_SECURITY_ADMIN_USER=admin" `
  -e "GF_SECURITY_ADMIN_PASSWORD=admin" `
  grafana/grafana:11.1.0
```

### Ping server
```
python scripts/ping_http.py
python scripts/ping_websocket.py
python scripts/ping_cassandra.py
```

### Cloudflare

```Powershell
winget install --id Cloudflare.cloudflared
cloudflared login
cloudflared tunnel create iot
cloudflared tunnel route dns iot iot.brandonfremin.com
code C:\Users\bfrem\.cloudflared\config.yml

cloudflared tunnel --url http://localhost:8000

```

### Environemnt Setup

```
source ./scripts/load_env.sh .env
```