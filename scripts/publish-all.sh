#!/bin/bash
# OverseeX SDK Publishing Script
# Run this after logging into npm and PyPI

set -e  # Exit on error

echo "🚀 OverseeX SDK Publishing Script"
echo "=================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check npm login
echo "Checking npm authentication..."
if npm whoami > /dev/null 2>&1; then
    echo -e "${GREEN}✓ npm authenticated as $(npm whoami)${NC}"
else
    echo -e "${RED}✗ Not logged into npm${NC}"
    echo "Run: npm login"
    exit 1
fi

# Check PyPI credentials
echo "Checking PyPI credentials..."
if [ -f ~/.pypirc ]; then
    echo -e "${GREEN}✓ PyPI credentials found${NC}"
else
    echo -e "${YELLOW}⚠ No ~/.pypirc found - you'll need to enter credentials${NC}"
fi

echo ""
echo "=================================="
echo "Publishing Packages"
echo "=================================="
echo ""

# 1. TypeScript SDK
echo "📦 1/7: Publishing TypeScript SDK (overseex@0.2.0)..."
cd sdks/typescript
npm run build
npm publish
echo -e "${GREEN}✓ TypeScript SDK published${NC}"
echo ""

# 2. Vercel AI Integration
echo "📦 2/7: Publishing Vercel AI Integration (@overseex/vercel-ai@0.1.0)..."
cd ../../integrations/vercel-ai
npm run build
npm publish --access public
echo -e "${GREEN}✓ Vercel AI Integration published${NC}"
echo ""

# 3. n8n Node
echo "📦 3/7: Publishing n8n Node (n8n-nodes-overseex@0.1.0)..."
cd ../n8n-node
npm run build
npm publish
echo -e "${GREEN}✓ n8n Node published${NC}"
echo ""

# 4. CrewAI Integration
echo "📦 4/7: Publishing CrewAI Integration (overseex-crewai@0.1.0)..."
cd ../crewai
python -m build
python -m twine upload dist/* --skip-existing
echo -e "${GREEN}✓ CrewAI Integration published${NC}"
echo ""

# 5. LangChain Integration
echo "📦 5/7: Publishing LangChain Integration (overseex-langchain@0.1.0)..."
cd ../langchain
python -m build
python -m twine upload dist/* --skip-existing
echo -e "${GREEN}✓ LangChain Integration published${NC}"
echo ""

# 6. AutoGen Integration
echo "📦 6/7: Publishing AutoGen Integration (overseex-autogen@0.1.0)..."
cd ../autogen
python -m build
python -m twine upload dist/* --skip-existing
echo -e "${GREEN}✓ AutoGen Integration published${NC}"
echo ""

# 7. Python SDK (if not already published)
echo "📦 7/7: Publishing Python SDK (overseex@0.2.0)..."
cd ../../sdks/python
python -m build
python -m twine upload dist/* --skip-existing
echo -e "${GREEN}✓ Python SDK published${NC}"
echo ""

echo "=================================="
echo -e "${GREEN}✅ All packages published successfully!${NC}"
echo "=================================="
echo ""
echo "Next steps:"
echo "1. Test installations:"
echo "   pip install overseex overseex-crewai overseex-langchain overseex-autogen"
echo "   npm install overseex @overseex/vercel-ai"
echo ""
echo "2. Update documentation if needed"
echo "3. Announce on social media"
echo "4. Monitor for issues"
echo ""
