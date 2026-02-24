@echo off
echo.
echo  ================================================
echo   AssetBlock v2.0 - Startup
echo  ================================================
echo.

:: Always work from the project root (where this .bat file lives)
cd /d "%~dp0"

echo [1/3] Starting FastAPI Backend...
:: Run uvicorn from inside src\ so relative imports (database, sha256_hash) work
start "AssetBlock API" cmd /k "cd /d "%~dp0src" && uvicorn api:app --reload --port 8000"

timeout /t 3 /nobreak > nul

echo [2/3] Starting Client Interface...
:: Streamlit is launched from the project root — load_dotenv will resolve correctly
start "AssetBlock Client" cmd /k "cd /d "%~dp0" && streamlit run src/client/client.py --server.port 8501"

timeout /t 2 /nobreak > nul

echo [3/3] Starting Admin Panel...
start "AssetBlock Admin" cmd /k "cd /d "%~dp0" && streamlit run src/server/server.py --server.port 8502"

echo.
echo  ================================================
echo   All services started!
echo.
echo   API:    http://localhost:8000/docs
echo   Client: http://localhost:8501
echo   Admin:  http://localhost:8502
echo.
echo   NOTE: Make sure .env has your real credentials before logging in.
echo  ================================================
echo.
pause
