#!/bin/bash

# Project SPECTRE: Mission Control Startup Script

echo "Initializing SPECTRE Intelligence Core..."

# Start Backend in background
cd backend
source .venv/bin/activate
export GEMINI_API_KEY=$(grep GEMINI_API_KEY /home/afrifa-gilbert/Documents/Dev/Jarvis/.env | cut -d '=' -f2)
python3 main.py &
BACKEND_PID=$!

echo "Backend active (PID: $BACKEND_PID)"

# Start Frontend
cd ../frontend
pnpm dev &
FRONTEND_PID=$!

echo "Frontend active (PID: $FRONTEND_PID)"

# Handle cleanup on exit
trap "kill $BACKEND_PID $FRONTEND_PID; exit" SIGINT SIGTERM

echo "SPECTRE Mission Control is online at http://localhost:5173"
wait
