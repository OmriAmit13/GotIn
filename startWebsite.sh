#!/bin/bash

# Detect OS
OS="$(uname)"
if [[ "$OS" == "Linux" ]]; then
    OPEN_CMD="xdg-open"
    PYTHON_CMD="python3"
elif [[ "$OS" == "Darwin" ]]; then
    OPEN_CMD="open"
    PYTHON_CMD="python3"
elif [[ "$OS" =~ "MINGW" || "$OS" =~ "MSYS" || "$OS" =~ "CYGWIN" ]]; then
    OPEN_CMD="start"
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

# Start the frontend (open in browser)
cd ../Frontend
$OPEN_CMD index.html