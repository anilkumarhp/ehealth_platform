@echo off
echo Running database seed script...
cd services\user-management
python -m app.scripts.seed
pause