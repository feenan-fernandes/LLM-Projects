@echo off
echo Starting Ollama Daemon...
start "" /B ollama serve

echo Starting Swarm IDE Backend...
start "" /B python -u 6_builder_app.py

echo Waiting for server to boot...
timeout /t 3 /nobreak >nul

echo Opening Swarm IDE in your browser...
start http://127.0.0.1:5000

echo.
echo Swarm IDE is now running! 
echo You can close this terminal window when you are done to stop the Python server.
pause
