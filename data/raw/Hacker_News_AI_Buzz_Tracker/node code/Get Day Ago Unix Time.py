# n8n code node: Get Day Ago Unix Time
import time

windowHours = 24

return [{
    "json": {
        "sinceUnix": int(time.time()) - windowHours * 3600
    }
}]
