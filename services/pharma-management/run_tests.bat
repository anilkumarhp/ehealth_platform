@echo off
REM Simple script to run tests in Docker container

docker-compose exec app bash /app/run_tests.sh