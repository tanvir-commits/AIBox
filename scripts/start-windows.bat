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
  echo.
  echo Pull failed - GHCR packages may be private. Building locally instead (slower)...
  echo Fix: GitHub -^> Packages -^> aibox-backend / aibox-web -^> Public
  echo.
  docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d --build
  if errorlevel 1 (
    echo docker compose build failed.
    pause
    exit /b 1
  )
  goto opened
)

echo Starting stack...
docker compose up -d
if errorlevel 1 (
  echo docker compose failed.
  pause
  exit /b 1
)

:opened

echo Opening http://localhost:3000
start "" http://localhost:3000
echo Sign in: admin@example.com / changeme
echo Stop: docker compose down
pause
