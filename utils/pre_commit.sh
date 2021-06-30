#!/usr/bin/env bash
# Run the pre-commit checks right now

pre-commit install
pre-commit run --all-files
