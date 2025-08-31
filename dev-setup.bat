@echo off
REM Licensed under the Apache License, Version 2.0 (the "License");
REM you may not use this file except in compliance with the License.

echo 🚀 Setting up Songo BI Development Environment...
echo.

REM Create virtual environment
echo 📦 Creating Python virtual environment...
python -m venv venv
if %errorlevel% neq 0 (
    echo ❌ Failed to create virtual environment
    pause
    exit /b 1
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo 📚 Installing Python dependencies...
pip install --upgrade pip
pip install -r requirements\development.txt

if %errorlevel% neq 0 (
    echo ❌ Failed to install dependencies
    pause
    exit /b 1
)

REM Install the application
echo 🔨 Installing Songo BI application...
pip install -e .

REM Create environment file
if not exist ".env" (
    echo 📝 Creating environment configuration...
    copy ".env.example" ".env"
)

echo.
echo ✅ Development environment setup complete!
echo.
echo 🎯 Next steps:
echo   1. Edit .env file with your API keys
echo   2. Run: python run.py
echo   3. Open: http://localhost:8088
echo.
echo 💡 For full features, you'll need:
echo   - OpenAI API key for chatbot
echo   - NetSuite credentials for integration
echo   - PostgreSQL database (or use SQLite for testing)
echo.

pause
