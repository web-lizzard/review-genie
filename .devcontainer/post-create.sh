#!/bin/bash

sudo apt-get update
sudo apt-get install -y parallel

# Install backend dependencies
pushd backend
uv sync
popd

# Install frontend dependencies
# pushd frontend
# pnpm install
# popd
