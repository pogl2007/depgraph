@echo off
cd /d "%~dp0.."
set REPO=https://api.nuget.org/v3-flatcontainer/

echo ===== 1. Serilog 3.1.1 =====
python src\main.py --package Serilog --repo %REPO% --version 3.1.1 --max-depth 1

echo ===== 2. Microsoft.Extensions.Logging 8.0.0 =====
python src\main.py --package Microsoft.Extensions.Logging --repo %REPO% --version 8.0.0 --max-depth 1

echo ===== 3. Newtonsoft.Json 13.0.3 =====
python src\main.py --package Newtonsoft.Json --repo %REPO% --version 13.0.3 --max-depth 1

echo ===== 4. Package without dependencies =====
python src\main.py --package Microsoft.NETCore.Platforms --repo %REPO% --version 1.1.0 --max-depth 1

echo ===== 5. Package not found =====
python src\main.py --package No.Such.Package.Xyz --repo %REPO% --version 1.0.0 --max-depth 1
echo exit code: %ERRORLEVEL%

echo ===== 6. Version not found =====
python src\main.py --package Serilog --repo %REPO% --version 99.0.0 --max-depth 1
echo exit code: %ERRORLEVEL%

echo ===== 7. Repository is unreachable =====
python src\main.py --package Serilog --repo https://no-such-host.invalid/ --version 3.1.1 --max-depth 1
echo exit code: %ERRORLEVEL%
