@echo off
echo Generating gRPC code for notification service...

python -m pip install grpcio-tools

python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. app/protos/notification.proto

echo Done!