@echo off
REM Pull compose images one at a time (less likely to freeze Windows than one big pull).
setlocal
cd /d "%~dp0.."

docker info >nul 2>&1
if errorlevel 1 (
  echo Docker is not running. Start Docker Desktop first.
  exit /b 1
)

echo Pulling images one at a time - need ~8 GB RAM for Docker and ~10 GB disk.
echo.

for %%s in (postgres qdrant backend web) do (
  echo -- pull %%s --
  docker compose pull %%s
  echo.
)

echo Done. Next: docker compose up -d
exit /b 0
