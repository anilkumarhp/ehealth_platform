@echo off
echo Running script to fix null organization IDs...
cd services\user-management
python -m app.scripts.fix_null_organization_ids
pause