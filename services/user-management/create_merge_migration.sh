#!/bin/bash

# Create a merge migration
cd /app
alembic merge heads -m "merge_multiple_heads"