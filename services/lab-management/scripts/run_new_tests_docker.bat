@echo off

REM Run new feature tests in Docker environment

echo 🚀 Running new feature tests in Docker...

REM Ensure services are running
echo Starting required services...
docker-compose up -d db redis

REM Wait for services to be ready
echo Waiting for services to be ready...
timeout /t 10 /nobreak > nul

REM Run the new feature tests
echo Running new feature tests...
docker-compose run --rm test python scripts/run_new_tests.py

REM Capture exit code
set TEST_EXIT_CODE=%ERRORLEVEL%

REM Show test results
if %TEST_EXIT_CODE% equ 0 (
    echo ✅ All new feature tests passed!
) else (
    echo ❌ Some tests failed. Check output above.
)

REM Optional: Run specific test categories individually for better debugging
echo.
echo Running individual test categories for detailed results...

echo 📁 File Management Tests...
docker-compose run --rm test python -m pytest tests/api/v1/test_files_integration.py -v

echo 📊 Analytics Tests...
docker-compose run --rm test python -m pytest tests/api/v1/test_analytics_integration.py -v

echo 🔍 Search Tests...
docker-compose run --rm test python -m pytest tests/api/v1/test_search_integration.py -v

echo ❤️ Health Check Tests...
docker-compose run --rm test python -m pytest tests/api/v1/test_health_integration.py -v

echo ⚡ Cache Tests...
docker-compose run --rm test python -m pytest tests/unit/test_cache_service.py -v

echo 🚦 Rate Limiter Tests...
docker-compose run --rm test python -m pytest tests/unit/test_rate_limiter.py -v

echo 📝 Audit Tests...
docker-compose run --rm test python -m pytest tests/unit/test_audit_service.py -v

echo 🔄 Celery Tests...
docker-compose run --rm test python -m pytest tests/unit/test_celery_tasks.py -v

echo ⚠️ Exception Tests...
docker-compose run --rm test python -m pytest tests/unit/test_exceptions.py -v

echo.
echo 🏁 All new feature tests completed!

exit /b %TEST_EXIT_CODE%