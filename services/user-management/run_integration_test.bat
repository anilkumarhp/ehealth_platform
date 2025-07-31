@echo off
echo Running notification integration test...

REM Generate gRPC code first
call generate_grpc.bat

REM Run the test
python test_notification_integration.py