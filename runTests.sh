#!/bin/bash

# Detect OS
OS="$(uname)"
if [[ "$OS" == "Linux" ]]; then
    PYTHON_CMD="python3"
elif [[ "$OS" == "Darwin" ]]; then
    PYTHON_CMD="python3"
elif [[ "$OS" =~ "MINGW" || "$OS" =~ "MSYS" || "$OS" =~ "CYGWIN" ]]; then
    PYTHON_CMD="python"
else
    echo "Unsupported OS: $OS"
    exit 1
fi

# Start backend servers (run in background, save PIDs)
cd Backend_Hebrew_university
$PYTHON_CMD app.py & echo $! > ../backend_hu.pid
cd ../Backend_technion
$PYTHON_CMD app.py & echo $! > ../backend_technion.pid
cd ../Backend-BGU
$PYTHON_CMD app.py & echo $! > ../backend_bgu.pid
cd ../Backend-TelAvivUniversity
$PYTHON_CMD app.py & echo $! > ../backend_ta.pid

cd ..

# Wait for servers to start
echo "Waiting for servers to start..."
sleep 5

# Run tests
cd Tests
$PYTHON_CMD runTests.py

# Return to root directory
cd ..

# Stop all servers
for pidfile in backend_hu.pid backend_technion.pid backend_bgu.pid backend_ta.pid; do
    if [[ -f $pidfile ]]; then
        PID=$(cat $pidfile)
        if kill -0 $PID 2>/dev/null; then
            kill $PID
            echo "Stopped process $PID from $pidfile"
        fi
        rm -f $pidfile
    fi
done
