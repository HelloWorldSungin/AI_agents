#!/bin/bash
# Manager Session Start Hook
# Runs cleanup before manager sessions

COMM_FILE=".ai-agents/state/team-communication.json"

if [ -f "$COMM_FILE" ]; then
    # Check file size (rough estimate)
    SIZE=$(wc -c < "$COMM_FILE")
    TOKENS=$((SIZE / 4))

    if [ $TOKENS -gt 20000 ]; then
        echo "⚠️  Communication file is large (~$TOKENS tokens)"
        echo "Running cleanup..."
        python3 scripts/cleanup-team-communication.py
    else
        echo "✓ Communication file size OK (~$TOKENS tokens)"
    fi
fi
