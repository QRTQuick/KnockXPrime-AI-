#!/bin/bash

# Build script for Render deployment
echo "🚀 Starting KnockXPrime AI build..."

# Upgrade pip first
pip install --upgrade pip

# Try main requirements first
echo "📦 Installing main requirements..."
if pip install -r requirements.txt; then
    echo "✅ Main requirements installed successfully"
else
    echo "❌ Main requirements failed, trying minimal..."
    if pip install -r requirements-minimal.txt; then
        echo "✅ Minimal requirements installed successfully"
    else
        echo "❌ All requirements failed"
        exit 1
    fi
fi

echo "🎉 Build completed successfully!"