@echo off
cd /d "%~dp0.."
set REPO=https://api.nuget.org/v3-flatcontainer/

echo ===== 1. All parameters are correct =====
python src\main.py --package Serilog --repo %REPO% --version 3.1.1

echo ===== 2. Test mode =====
python src\main.py --package A --repo test_repos\simple.txt --test-mode --version 1.0

echo ===== 3. Errors in all parameters =====
python src\main.py --package "bad name" --repo ftp://x --version abc --max-depth 0
echo exit code: %ERRORLEVEL%

echo ===== 4. Test repository file not found =====
python src\main.py --package A --repo nope.txt --test-mode --version 1.0

echo ===== 5. Depth is not a number =====
python src\main.py --package A --repo %REPO% --version 1.0 --max-depth abc 2>&1 | findstr error

echo ===== 6. Required parameter is missing =====
python src\main.py --package A 2>&1 | findstr error
