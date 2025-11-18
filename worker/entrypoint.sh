#!/bin/sh
set -e

WAIT_FOR_HOST="${WAIT_FOR_HOST:-rabbitmq}"
WAIT_FOR_PORT="${WAIT_FOR_PORT:-5672}"
WAIT_FOR_RETRIES="${WAIT_FOR_RETRIES:-30}"
WAIT_FOR_DELAY="${WAIT_FOR_DELAY:-2}"

echo "[entrypoint] Ожидание RabbitMQ на ${WAIT_FOR_HOST}:${WAIT_FOR_PORT}"

try_connect() {
python - <<PY
import socket, sys
host = "${WAIT_FOR_HOST}"
port = int("${WAIT_FOR_PORT}")
s = socket.socket()
s.settimeout(2)
try:
    s.connect((host, port))
except OSError:
    sys.exit(1)
sys.exit(0)
PY
}

i=1
while [ "$i" -le "$WAIT_FOR_RETRIES" ]; do
    if try_connect; then
        echo "[entrypoint] RabbitMQ доступен"
        exec python app.py
    fi
    echo "[entrypoint] Попытка ${i}/${WAIT_FOR_RETRIES} неудачна, повтор через ${WAIT_FOR_DELAY}с"
    i=$((i + 1))
    sleep "$WAIT_FOR_DELAY"
done

echo "[entrypoint] Не удалось дождаться RabbitMQ"
exit 1

