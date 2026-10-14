@echo off
REM ============================================================
REM  NutriAgent AI — Launch Script
REM  Nutrition Agentic AI Application using IBM Granite LLM
REM ============================================================

echo.
echo  ==========================================
echo   NutriAgent AI — IBM Granite Powered
echo  ==========================================
echo.

REM -- Check Python availability
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo  [ERROR] Python is not installed or not in PATH.
    echo  Please install Python 3.10+ from https://www.python.org/
    pause
    exit /b 1
)

REM -- Create virtual environment if it doesn't exist
IF NOT EXIST ".venv" (
    echo  [INFO] Creating virtual environment...
    python -m venv .venv
    echo  [INFO] Virtual environment created.
)

REM -- Activate virtual environment
echo  [INFO] Activating virtual environment...
call .venv\Scripts\activate.bat

REM -- Install / upgrade dependencies
echo  [INFO] Installing dependencies from requirements.txt...
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt

REM -- Check for .env file
IF NOT EXIST ".env" (
    echo.
    echo  [WARNING] .env file not found.
    echo  Creating a template .env file — please fill in your IBM credentials.
    echo.
    (
        echo IBM_API_KEY=your_ibm_api_key_here
        echo IBM_PROJECT_ID=your_watsonx_project_id_here
        echo IBM_URL=https://us-south.ml.cloud.ibm.com
    ) > .env
    echo  [INFO] .env template created. Edit it before running again.
    echo.
    echo  Press any key to launch anyway (app will show a credential warning)...
    pause >nul
)

REM -- Launch the Streamlit app
echo.
echo  [INFO] Launching NutriAgent AI on http://localhost:8501
echo  [INFO] Press Ctrl+C to stop the server.
echo.
streamlit run app.py --server.port 8501 --server.headless false

REM -- Deactivate on exit
call .venv\Scripts\deactivate.bat
echo.
echo  [INFO] Server stopped. Goodbye!
pause
