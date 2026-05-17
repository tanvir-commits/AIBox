@echo off
REM Fallback if you don't have PrivateAIBox.exe — same idea, requires Docker Desktop.
setlocal
cd /d "%~dp0.."

where docker >nul 2>&1
if errorlevel 1 (
  echo Docker not found. Install Docker Desktop for Windows first.
  echo https://docs.docker.com/desktop/setup/install/windows-install/
  pause
  exit /b 1
)

docker info >nul 2>&1
if errorlevel 1 (
  echo Docker is not running. Start Docker Desktop, then try again.
  pause
  exit /b 1
)

if not exist .env if exist .env.example copy .env.example .env

echo Pulling images (first run may take several minutes)...
docker compose pull
if errorlevel 1 (
  echo docker compose pull failed.
  pause
  exit /b 1
)

echo Starting stack...
docker compose up -d
if errorlevel 1 (
  echo docker compose failed.
  pause
  exit /b 1
)

echo Opening http://localhost:3000
start "" http://localhost:3000
echo Sign in: admin@example.com / changeme
echo Stop: docker compose down
pause
