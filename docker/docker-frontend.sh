#!/bin/bash
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.

set -e

# Frontend development server bootstrap script

echo "Starting Songo BI Frontend development server..."

# Change to frontend directory
cd /app/songo-bi-frontend

# Install dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
    echo "Installing Node.js dependencies..."
    npm ci
fi

# Start development server
echo "Starting webpack dev server..."
exec npm run dev-server
