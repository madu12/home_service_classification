#!/bin/bash

echo "Setting up the environment..."
pip install -r requirements.txt

echo "Running data preprocessing..."
python scripts/data_preprocessing.py
