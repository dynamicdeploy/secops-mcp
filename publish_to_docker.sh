#!/bin/bash
# Build and publish secops-mcp Docker image

set -e  # Exit on error

# Check if --no-cache flag is passed
NO_CACHE=""
if [[ "$1" == "--no-cache" ]]; then
    NO_CACHE="--no-cache"
    echo "⚠️  Building without cache (this will take longer)..."
fi

echo "🔨 Building Docker image..."
echo "   This may take several minutes if building from scratch..."
echo "   (Docker will use cache for unchanged layers if available)"
echo ""

# Build with progress output
docker build $NO_CACHE -t secops-mcp:latest . --progress=plain

echo ""
echo "🏷️  Tagging image..."
docker tag secops-mcp:latest hackerdogs/secops-mcp:latest

echo "📤 Pushing to Docker Hub..."
echo "   This may take a few minutes depending on image size..."
docker push hackerdogs/secops-mcp:latest

echo ""
echo "✅ Successfully built and published hackerdogs/secops-mcp:latest"
echo ""
echo "💡 Tip: Use './publish_to_docker.sh --no-cache' to force a full rebuild"