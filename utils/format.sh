#!/usr/bin/env bash
# Run the pre-commit checks right now


echo "Sorting python imports with isort."
isort .

echo "Auto-formatting python code with black."
black .
