@echo off
REM ==========================================
REM RiskShield Startup Script (Windows)
REM ==========================================

setlocal enabledelayedexpansion

REM Configuration
set HOST=0.0.0.0
set PORT=8000
set WORKERS=4

echo ======================================
echo    RiskShield Fraud Detection API
echo ======================================
echo.

REM Check if virtual environment exists
if not exist "venv\" (
    echo [WARNING] Virtual environment not found!
    echo Creating virtual environment...
    python -m venv venv
    echo [SUCCESS] Virtual environment created
    echo.
)

REM Activate virtual environment
echo [INFO] Activating virtual environment...
call venv\Scripts\activate.bat
echo.

REM Check if requirements are installed
echo [INFO] Checking dependencies...
python -c "import fastapi" 2>nul
if errorlevel 1 (
    echo [WARNING] Dependencies not installed!
    echo Installing requirements...
    pip install -r requirements.txt
    echo [SUCCESS] Dependencies installed
) else (
    echo [SUCCESS] Dependencies already installed
)
echo.

REM Check database connection
echo [INFO] Checking database connection...
python -c "from database import engine; engine.connect().close(); print('[SUCCESS] Database connection successful')" 2>nul
if errorlevel 1 (
    echo [ERROR] Database connection failed!
    echo Please check your PostgreSQL configuration
    pause
    exit /b 1
)
echo.

REM Check if model file exists
echo [INFO] Checking ML model...
if exist "model\catboost_fraud_model_balanced_tuned.cbm" (
    echo [SUCCESS] Model file found
) else (
    echo [WARNING] Model file not found!
    echo Please place your model at: model\catboost_fraud_model_balanced_tuned.cbm
)
echo.

REM Create logs directory
if not exist "logs\" mkdir logs

REM Display startup information
echo ======================================
echo    Starting RiskShield API...
echo ======================================
echo Host: %HOST%
echo Port: %PORT%
echo Workers: %WORKERS%
echo.
echo API Documentation:
echo   - Swagger UI: http://localhost:%PORT%/docs
echo   - ReDoc: http://localhost:%PORT%/redoc
echo.
echo Available Endpoints:
echo   - Health Check: GET /api/health
echo   - Register: POST /api/register
echo   - Login: POST /api/login
echo   - Predict: POST /api/predict
echo   - Transactions: GET /api/transactions/{email}
echo   - Analytics: GET /api/analytics
echo   - Metrics: GET /api/metrics
echo.
echo ======================================
echo Press Ctrl+C to stop the server
echo ======================================
echo.

REM Start the application
uvicorn main:app --host %HOST% --port %PORT% --reload

pause