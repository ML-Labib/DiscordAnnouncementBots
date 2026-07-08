#!/bin/bash

SESSION="tournament"

# Kill existing session
tmux kill-session -t $SESSION 2>/dev/null

# Create new session
tmux new-session -d -s $SESSION

# Activate virtual environment
tmux send-keys -t $SESSION \
"source .bots/bin/activate" C-m

# Start master in first window
tmux send-keys -t $SESSION \
"python master.py" C-m

# Create 16 worker windows
for i in $(seq 1 16)
do
    tmux new-window -t $SESSION -n "Worker-$i"

    tmux send-keys -t "$SESSION:Worker-$i" \
    "source .bots/bin/activate" C-m

    tmux send-keys -t "$SESSION:Worker-$i" \
    "python worker.py $i" C-m
done

# Attach
tmux attach -t $SESSION