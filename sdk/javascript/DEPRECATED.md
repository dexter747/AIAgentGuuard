# ⚠️ DEPRECATED: This SDK is no longer maintained

**Date:** January 28, 2026

This JavaScript SDK (`@overseex/sdk`) is **deprecated** and will not receive further updates.

## Migration Guide

Please migrate to the new **TypeScript SDK** which supports both JavaScript and TypeScript:

### Old Package (Deprecated)
```bash
npm install @overseex/sdk  # ❌ DO NOT USE
```

### New Package (Recommended)
```bash
npm install overseex  # ✅ USE THIS
```

### Code Changes

**Before (Old SDK)**:
```typescript
import { OverseeX } from '@overseex/sdk';

const client = new OverseeX({ apiKey: 'your-key' });
```

**After (New SDK)**:
```typescript
import { OverseeX } from 'overseex';

const client = new OverseeX({ apiKey: 'your-key' });
```

## Why the Change?

The new TypeScript SDK (`sdks/typescript`) offers:
- ✅ **Phase 2 Features**: Multi-agent coordination intelligence
- ✅ **Better TypeScript Support**: Full type safety
- ✅ **Coordination API**: Issues, suggestions, patterns, handoffs
- ✅ **Modern Build System**: Using tsup for smaller bundles
- ✅ **Active Development**: All new features go here

## New Features Available

The new SDK includes:
- Coordination intelligence client
- Agent handoff tracking
- ML-powered corrective suggestions
- Learned pattern management
- Enhanced span API
- Better error handling

## Documentation

- **New SDK Docs**: https://docs.overseex.com (JavaScript/TypeScript tab)
- **GitHub**: https://github.com/overseex/overseex-js
- **npm**: https://www.npmjs.com/package/overseex

## Support

If you need help migrating, please:
- Check our [migration guide](https://docs.overseex.com/migration)
- Email support@overseex.com
- Join our [Discord community](https://discord.gg/overseex)

---

**Location of New SDK**: `/sdks/typescript` in this repo

**This directory will be removed in a future release.**
