# Quick Test Guide - DODO Payment Integration

## 🚀 Quick Start (5 minutes)

### 1. Start Backend
```bash
cd backend
# Make sure .env has DODO_API_KEY set
python -m uvicorn main:app --reload
```

### 2. Start Frontend
```bash
cd apps/web
npm run dev
```

### 3. Test Pricing Page
1. Open: http://localhost:3000/pricing
2. You should see 6 plans (3 monthly + 3 annual)
3. Toggle between Monthly and Annual
4. Click "Get Started" on any plan

### 4. Test Checkout
When you click "Get Started", you'll be redirected to:
```
https://test.checkout.dodopayments.com/buy/pdt_0NWy2Alvj6LyAQ2yxnPEX?quantity=1&return_url=...
```

Use DODO test card:
- Card: 4242 4242 4242 4242
- Expiry: Any future date
- CVV: Any 3 digits
- Name: Test User

### 5. Verify Success
After payment, you'll be redirected to:
```
http://localhost:3000/payment/success
```

Check backend logs for webhook:
```
POST /v1/webhooks/dodo
```

---

## 🔍 Verify Installation

### Check Backend:
```bash
cd backend
python -c "from app.services.dodo_payments import SUBSCRIPTION_PLANS; print('Plans:', len(SUBSCRIPTION_PLANS))"
# Should output: Plans: 7

python -c "from app.api.v1.endpoints import billing; print('Billing: OK')"
# Should output: Billing: OK
```

### Check Frontend:
```bash
cd apps/web
# Files should exist:
ls src/app/pricing/page.tsx
ls src/app/payment/success/page.tsx
ls src/app/api/billing/plans/route.ts
ls src/app/api/billing/subscription/route.ts
```

---

## 🐛 Common Issues

### Issue: "Plans not loading"
**Fix:** Make sure backend is running and NEXT_PUBLIC_API_URL is set

### Issue: "Checkout URL not working"
**Fix:** Verify product IDs in dodo_payments.py match DODO dashboard

### Issue: "Webhook not received"
**Fix:** 
1. Check DODO dashboard has webhook URL configured
2. Use ngrok or similar for local testing: `ngrok http 8000`
3. Update webhook URL in DODO to: `https://your-ngrok-url.ngrok.io/v1/webhooks/dodo`

### Issue: "Payment not updating user"
**Fix:** Check backend logs for webhook errors. Verify signature with DODO_WEBHOOK_SECRET

---

## 📊 Expected Behavior

### Pricing Page:
✅ Shows 6 paid plans
✅ Monthly/Annual toggle works
✅ Plan features displayed
✅ Checkout buttons work

### Checkout Flow:
✅ Redirects to DODO checkout
✅ Email pre-filled
✅ Payment processes
✅ Redirects to success page

### Success Page:
✅ Shows loading spinner
✅ Verifies payment
✅ Shows success message
✅ Redirects to dashboard

### Backend:
✅ Receives webhook
✅ Verifies signature
✅ Updates user metadata
✅ Subscription active

---

## 🔐 Security Checklist

Before deploying to production:

- [ ] Change DODO_API_KEY to production key
- [ ] Set DODO_SECRET_KEY
- [ ] Set DODO_WEBHOOK_SECRET
- [ ] Update checkout URLs to production (remove 'test.')
- [ ] Configure production webhook in DODO dashboard
- [ ] Set APP_URL to production domain
- [ ] Set CORS_ORIGINS to production domain
- [ ] Enable HTTPS
- [ ] Test with real payment method

---

## 📞 Need Help?

### DODO Support:
- Docs: https://docs.dodopayments.com
- Discord: https://discord.gg/bYqAp4ayYh
- Email: support@dodopayments.com

### Files to Check:
- Backend: `/backend/app/services/dodo_payments.py`
- Billing API: `/backend/app/api/v1/endpoints/billing.py`
- Webhooks: `/backend/app/api/v1/endpoints/dodo_webhooks.py`
- Pricing Page: `/apps/web/src/app/pricing/page.tsx`
- Success Page: `/apps/web/src/app/payment/success/page.tsx`

---

## ✅ Quick Verification Commands

```bash
# Test backend imports
cd backend
python -c "from app.services.dodo_payments import SUBSCRIPTION_PLANS, get_checkout_url; print('✅ All imports OK')"

# Test checkout URL generation
python -c "from app.services.dodo_payments import get_checkout_url; url = get_checkout_url('pro_monthly', 'test@example.com', '123', 'http://localhost:3000/payment/success'); print('✅ Checkout URL:', url[:80])"

# Test billing endpoint
python -c "from app.api.v1.endpoints import billing; print('✅ Billing endpoints OK')"

# Check all routes registered
python -c "from app.api.v1 import router; print('✅ Routes registered:', len([r for r in router.api_router.routes]))"
```

Expected output:
```
✅ All imports OK
✅ Checkout URL: https://test.checkout.dodopayments.com/buy/pdt_0NWy2Alvj6LyAQ2yxnPEX?q...
✅ Billing endpoints OK
✅ Routes registered: 88
```

---

**Ready to test!** 🚀

Just run the backend and frontend, then visit `/pricing` to see your payment integration in action.
