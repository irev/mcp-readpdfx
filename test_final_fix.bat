@echo off
echo 🎯 LM Studio SSE Fix - Final Test
echo =====================================
echo.

echo 📡 Starting MCP Server...
start /b python run.py
timeout /t 3 /nobreak >nul

echo.
echo 🔍 Testing SSE Endpoints...
python FINAL_LM_STUDIO_FIX.py

echo.
echo 📋 Server Status:
netstat -an | findstr :8000

echo.
echo ✅ SOLUTION SUMMARY:
echo • Server running on: http://localhost:8000
echo • LM Studio SSE endpoint: http://localhost:8000/events  
echo • Test result above shows compatibility status
echo.
pause