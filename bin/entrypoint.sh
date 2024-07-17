#! /bin/bash

export PATH="/opt/site/.local/bin:$PATH"
BASE_DIR="/opt/site/code"
CMD="opentelemetry-instrument flask --app app run -h 0.0.0.0 -p ${FLASK_PORT}"

sigterm() {
  echo "SIGTERM received"
  kill -TERM $PID
  wait $PID
  exit 0
}

sigint() {
  echo "SIGINT received"
  kill -INT $PID
  wait $PID
  exit 0
}

trap sigint SIGINT
trap sigterm SIGTERM

cd ${BASE_DIR} || exit 1

echo "Running: ${CMD}"
${CMD}

