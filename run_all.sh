#!/bin/bash
# chmod +x run_all.sh
# ./run_all.sh

# Start vm1.py in the background
python src/vm1.py &
pid1=$!
echo "Started vm1.py with PID $pid1"

# Start vm2.py in the background
python src/vm2.py &
pid2=$!
echo "Started vm2.py with PID $pid2"

# Start vm3.py in the background
python src/vm3.py &
pid3=$!
echo "Started vm3.py with PID $pid3"

# Wait for all processes to finish (if needed)
wait $pid1 $pid2 $pid3