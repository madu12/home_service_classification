#!/bin/bash

echo "Running tests..."
pytest tests/

if [ $? -ne 0 ]; then
    echo "Tests failed. Aborting pipeline."
    exit 1
fi
