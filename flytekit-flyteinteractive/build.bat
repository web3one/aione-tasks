@echo off
REM Shell script to build aione.flyteinteractive Docker image
REM Usage: build.bat [version]
REM If no version is provided, defaults to v1.0.0

REM Set default version
set DEFAULT_VERSION=v1.0.0
if "%1"=="" (
    set VERSION=%DEFAULT_VERSION%
) else (
    set VERSION=%1
)

REM Remove 'v' prefix if present for Docker build arg
set BUILD_VERSION=%VERSION:v=%

REM Image name
set IMAGE_NAME=aione.flyteinteractive

echo Building Docker image: %IMAGE_NAME%:%VERSION%
echo Using build version: %BUILD_VERSION%

REM Build the Docker image
docker build --build-arg VERSION=%BUILD_VERSION% --build-arg TARGETARCH=amd64 -t %IMAGE_NAME%:%VERSION% -t %IMAGE_NAME%:latest .

if %ERRORLEVEL% equ 0 (
    echo Successfully built %IMAGE_NAME%:%VERSION%
    echo Also tagged as %IMAGE_NAME%:latest
) else (
    echo Failed to build Docker image
    exit /b 1
)