#!/bin/bash

# generate_grpc.sh (Updated to automatically fix imports)

echo "--- Starting gRPC code generation ---"

OUTPUT_DIR="app/generated"
GRPC_FILE="$OUTPUT_DIR/user_service_pb2_grpc.py"

# Ensure the output directory exists
mkdir -p "$OUTPUT_DIR"
touch "$OUTPUT_DIR/__init__.py"

# Run the Python gRPC tools
python -m grpc_tools.protoc \
    -Iprotos \
    --python_out="$OUTPUT_DIR" \
    --grpc_python_out="$OUTPUT_DIR" \
    protos/user_service.proto

echo "gRPC files generated."

# --- THIS IS THE FIX ---
# Automatically patch the generated file to use a relative import.
# This is necessary for Python's package system to work correctly.
if [ -f "$GRPC_FILE" ]; then
    echo "Patching generated gRPC file for correct relative import..."
    # Use sed to replace the incorrect import with the correct one.
    # This works on both Linux and macOS.
    sed -i.bak 's/^import user_service_pb2/from . import user_service_pb2/' "$GRPC_FILE"
    echo "Patching complete."
else
    echo "ERROR: Generated gRPC file not found at $GRPC_FILE. Cannot apply patch."
    exit 1
fi
# --- END OF FIX ---


echo "SUCCESS: gRPC code generation and patching finished."
echo "Please check your local 'app/generated' directory."
