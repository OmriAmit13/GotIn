# #!/bin/bash

# # Detect OS
# OS="$(uname)"
# if [[ "$OS" == "Linux" ]]; then
#     OPEN_CMD="xdg-open"
#     PYTHON_CMD="python3"
# elif [[ "$OS" == "Darwin" ]]; then
#     OPEN_CMD="open"
#     PYTHON_CMD="python3"
# elif [[ "$OS" =~ "MINGW" || "$OS" =~ "MSYS" || "$OS" =~ "CYGWIN" ]]; then
#     OPEN_CMD="start"
#     PYTHON_CMD="python"
# else
#     echo "Unsupported OS: $OS"
#     exit 1
# fi

# # Start backend servers (run in background, save PIDs)
# cd Backend_Hebrew_university
# $PYTHON_CMD app.py & echo $! > ../backend_hu.pid
# cd ../Backend_technion
# $PYTHON_CMD app.py & echo $! > ../backend_technion.pid
# cd ../Backend-BGU
# $PYTHON_CMD app.py & echo $! > ../backend_bgu.pid
# cd ../Backend-TelAvivUniversity
# $PYTHON_CMD app.py & echo $! > ../backend_ta.pid

# # Start the frontend (open in browser)
# cd ../Frontend
# $OPEN_CMD index.html



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

# Function to start a backend server with retry logic
start_backend() {
    local backend_dir=$1
    local pid_file=$2
    local server_name=$3
    local max_retries=3
    local retry_delay=2
    
    for ((attempt=1; attempt<=max_retries; attempt++)); do
        echo "Starting $server_name (attempt $attempt/$max_retries)..."
        
        cd "$backend_dir"
        $PYTHON_CMD app.py & 
        local pid=$!
        echo $pid > "../$pid_file"
        
        # Wait a moment and check if the process is still running
        sleep 1
        if kill -0 $pid 2>/dev/null; then
            echo "✓ $server_name started successfully (PID: $pid)"
            cd ..
            return 0
        else
            echo "✗ $server_name failed to start (attempt $attempt)"
            rm -f "../$pid_file"
            cd ..
            
            if [ $attempt -lt $max_retries ]; then
                echo "Retrying in $retry_delay seconds..."
                sleep $retry_delay
            fi
        fi
    done
    
    echo "❌ Failed to start $server_name after $max_retries attempts"
    return 1
}

# Start backend servers with retry mechanism
start_backend "Backend_Hebrew_university" "backend_hu.pid" "Hebrew University Backend"
start_backend "Backend_technion" "backend_technion.pid" "Technion Backend"
start_backend "Backend-BGU" "backend_bgu.pid" "BGU Backend"
start_backend "Backend-TelAvivUniversity" "backend_ta.pid" "Tel Aviv University Backend"

# Start the frontend (open in browser)
cd Frontend
$OPEN_CMD index.html