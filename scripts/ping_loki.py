import requests
import time
import sys
import json
import datetime, zoneinfo

def ping_loki(loki_url):
    query = '{job="yourjob"}'
    params = {
        'query': query,
        'limit': 1
    }
    try:
        response = requests.get(f"{loki_url}/loki/api/v1/query", params=params)
        response.raise_for_status()
        data = response.json()
        status = data.get("status")
        if status == "success":
            print("Loki is reachable! Query succeeded.")
            results = data.get("data", {}).get("result", [])
            if results:
                print("Sample log entry:")
                print(results[0])
            else:
                print("No logs found for the query.")
        else:
            print(f"Loki query failed with status: {status}")
            print(data)
    except requests.exceptions.RequestException as e:
        print(f"Failed to connect to Loki at {loki_url}: {e}")
        sys.exit(1)

def push_log_to_loki(loki_url, log_line, labels):
    """
    Push a log line to Loki via the push API.
    labels: dict of labels, e.g. {"job": "yourjob", "host": "localhost"}
    """
    # Loki expects a stream with labels string, and an array of [timestamp_ns, line] entries.
    # Timestamp must be in nanoseconds epoch.
    
    labels_str = ",".join(f'{k}="{v}"' for k,v in labels.items())
    timestamp_ns = str(int(time.time() * 1e9))  # current time in ns
    
    payload = {
        "streams": [
            {
                "stream": labels,
                "values": [
                    [timestamp_ns, log_line]
                ]
            }
        ]
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        resp = requests.post(f"{loki_url}/loki/api/v1/push", data=json.dumps(payload), headers=headers)
        resp.raise_for_status()
        print(f"Successfully pushed log to Loki: {log_line}")
    except requests.exceptions.RequestException as e:
        print(f"Failed to push log to Loki: {e}")

if __name__ == "__main__":
    loki_url = "http://localhost:3100"
    
    print("Pinging Loki...")
    ping_loki(loki_url)
    
    print("\nPushing a test log to Loki...")
    test_log = "Hello Loki! This is a test log from Python. " + "A" * 1000
    tz = zoneinfo.ZoneInfo("America/New_York")   
    test_labels = {
        "ts": datetime.datetime.now(tz).isoformat(),
        "level": "INFO",
        "job": "python-test",
        "host": "localhost"
    }
    push_log_to_loki(loki_url, test_log, test_labels)
