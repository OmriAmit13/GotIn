#!/bin/bash

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