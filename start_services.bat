@echo off
setlocal EnableExtensions

REM ==========================================================
REM Start all services in separate CMD windows (non-blocking)
REM ==========================================================

REM Change to the directory where this .bat file lives
pushd "%~dp0"

REM Optional: if you use a venv, uncomment and point to it
REM call ".venv\Scripts\activate.bat"

REM Start services (each in a new CMD window)
start "API Gateway (8000)" cmd /k uvicorn api_gateway.main:app --reload --port 8000
start "Order Service (8001)" cmd /k uvicorn order_service.main:app --reload --port 8001
start "Payment Service (8002)" cmd /k uvicorn payment_service.main:app --reload --port 8002
start "Inventory Service (8003)" cmd /k uvicorn inventory_service.main:app --reload --port 8003
start "Notification Service (8004)" cmd /k uvicorn notification_service.main:app --reload --port 8004
start "Locust Console" cmd /k locust -f load_tests/locustfile.py

popd

echo All services launched in separate CMD windows.
exit /b 0
