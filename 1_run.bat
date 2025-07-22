@echo off
REM Check and set SECRET_KEY if not already defined
if not defined SECRET_KEY (
    for /f "usebackq delims=" %%A in (`powershell -NoProfile -Command "[guid]::NewGuid().ToString()"`) do set "SECRET_KEY=%%A"
)
py app.py
