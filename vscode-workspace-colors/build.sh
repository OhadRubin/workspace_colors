#!/bin/bash
set -e

# Build and publish VS Code extension
cd "$(dirname "$0")"

# Copy README from root
cp ../README.md .

# Compile TypeScript
npm run compile

# Package extension
npx vsce package

# Get version from package.json
VERSION=$(node -p "require('./package.json').version")
VSIX="workspace-colors-${VERSION}.vsix"

echo "Built: $VSIX"

# Publish if --publish flag is passed
if [[ "$1" == "--publish" ]]; then
    if [[ -z "$OVSX_PAT" ]]; then
        echo "Error: OVSX_PAT environment variable not set"
        exit 1
    fi
    npx ovsx publish "$VSIX"
    echo "Published v${VERSION} to Open VSX"
fi
