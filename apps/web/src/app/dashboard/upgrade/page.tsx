'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Check, Loader2 } from 'lucide-react';
import { cn } from '@/lib/utils';

interface PlanFeatures {
  traces_per_month: number;
  max_agents: number;
  max_tests: number;
  api_calls_per_minute: number;
  health_checks_per_agent: number;
  trace_retention_days: number;
  support: string;
  advanced_analytics: boolean;
  multi_agent_analysis: boolean;
  custom_integrations: boolean;
  pii_redaction?: boolean;
  sso?: boolean;
  dedicated_support?: boolean;
  custom_sla?: boolean;
}

interface Plan {
  id: string;
  name: string;
  billing_cycle: string;
  amount: number;
  currency: string;
  features: PlanFeatures;
  savings?: number;
  checkout_url: string;
  dodo_product_id: string;
}

// Default plans in case API fails
const defaultPlans = [
  {
    name: 'Free (OSS & experiments)',
    monthlyPrice: 0,
    annualPrice: 0,
    description: 'For open source & experimentation',
    features: [
      '50 analyzed traces/month',
      '7-day retention',
      'Basic test generation',
      'Agent graph visualization',
      'Community support',
    ],
    cta: 'Current Plan',
    popular: false,
    disabled: true,
    checkoutUrl: null
  },
  {
    name: 'Starter',
    monthlyPrice: 24,
    annualPrice: 19,
    description: 'For individual developers',
    features: [
      '200 analyzed traces/month',
      '14-day retention',
      'Auto test generation',
      'Tool mocking (5 tools)',
      'Agent graph visualization',
      'Regression detection',
      'Basic coordination view',
      'Email support',
    ],
    cta: 'Upgrade',
    popular: false,
    disabled: false,
    checkoutUrl: null
  },
  {
    name: 'Pro',
    monthlyPrice: 99,
    annualPrice: 79,
    description: 'For professional developers',
    features: [
      '1,000 analyzed traces/month',
      '30-day retention',
      'Unlimited test generation',
      'Tool mocking (20 tools)',
      'Coordination analysis',
      'Framework integrations',
      'Corrective suggestions',
      'Health monitoring',
      'Webhooks & alerts',
    ],
    cta: 'Upgrade',
    popular: true,
    disabled: false,
    checkoutUrl: null
  },
  {
    name: 'Team',
    monthlyPrice: 449,
    annualPrice: 349,
    description: 'For teams building agents',
    features: [
      '10,000 traces/month',
      '60-day retention',
      'Everything in Pro',
      'Advanced coordination',
      'Corrective intelligence',
      'Up to 10 team members',
      'Slack & PagerDuty',
      'Priority support',
    ],
    cta: 'Upgrade',
    popular: false,
    disabled: false,
    checkoutUrl: null
  },
  {
    name: 'Enterprise',
    monthlyPrice: null,
    annualPrice: null,
    description: 'For large-scale deployments',
    features: [
      'Unlimited traces',
      '1-year retention',
      'Full corrective AI',
      'Custom AI training',
      'PII auto-redaction',
      'SSO/SAML',
      'On-premise option',
      'Custom integrations',
      'Dedicated support',
    ],
    cta: 'Contact Sales',
    popular: false,
    disabled: false,
    checkoutUrl: null
  }
];

export default function UpgradePage() {
  const [isAnnual, setIsAnnual] = useState(true);
  const [apiPlans, setApiPlans] = useState<Plan[]>([]);
  const [loading, setLoading] = useState(true);
  const [processingPlan, setProcessingPlan] = useState<string | null>(null);

  useEffect(() => {
    fetchPlans();
  }, []);

  const fetchPlans = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || ''}/api/v1/billing/plans`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setApiPlans(data);
      }
    } catch (error) {
      console.error('Failed to fetch plans:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCheckout = async (planName: string, checkoutUrl: string | null) => {
    if (planName === 'Enterprise') {
      window.location.href = '/contact';
      return;
    }

    if (checkoutUrl) {
      // Direct checkout URL from API
      window.location.href = checkoutUrl;
      return;
    }

    // Try to create checkout session via API
    setProcessingPlan(planName);
    try {
      const token = localStorage.getItem('token');
      const billingCycle = isAnnual ? 'annual' : 'monthly';

      // Find matching plan from API
      const matchingPlan = apiPlans.find(
        p => p.name.toLowerCase() === planName.toLowerCase() && p.billing_cycle === billingCycle
      );

      if (matchingPlan?.checkout_url) {
        window.location.href = matchingPlan.checkout_url;
        return;
      }

      // Fallback: create checkout session
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || ''}/api/v1/billing/create-checkout`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          plan_name: planName.toLowerCase(),
          billing_cycle: billingCycle
        })
      });

      if (response.ok) {
        const data = await response.json();
        if (data.checkout_url) {
          window.location.href = data.checkout_url;
        }
      } else {
        console.error('Failed to create checkout session');
      }
    } catch (error) {
      console.error('Checkout error:', error);
    } finally {
      setProcessingPlan(null);
    }
  };

  // Map API plans to checkout URLs
  const getCheckoutUrl = (planName: string) => {
    const billingCycle = isAnnual ? 'annual' : 'monthly';
    const matchingPlan = apiPlans.find(
      p => p.name.toLowerCase() === planName.toLowerCase().replace(' / oss', '') &&
           p.billing_cycle === billingCycle
    );
    return matchingPlan?.checkout_url || null;
  };

  const plans = defaultPlans.map(plan => ({
    ...plan,
    checkoutUrl: getCheckoutUrl(plan.name)
  }));

  if (loading) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 rounded-full border-4 border-violet-500/20 border-t-violet-500 animate-spin mx-auto mb-4" />
          <p className="text-gray-400">Loading plans...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-black py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-12">
          <h2 className="text-4xl md:text-5xl font-medium mb-4">
            <span
              style={{
                backgroundImage: 'linear-gradient(90deg, rgb(255, 255, 255) 0%, rgba(255, 255, 255, 0.3) 350%)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                backgroundClip: 'text'
              }}
            >
              Upgrade Your Plan
            </span>
          </h2>
          <p
            className="text-lg max-w-2xl mx-auto mb-8"
            style={{
              backgroundImage: 'linear-gradient(90deg, rgb(255, 255, 255) 0%, rgba(255, 255, 255, 0.3) 350%)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              backgroundClip: 'text'
            }}
          >
            Scale your AI agent monitoring as you grow. No hidden fees.
          </p>
          <p className="text-gray-400 text-sm">
            Designed for solo builders → production teams → enterprise scale.
          </p>

          {/* Monthly/Annual Toggle */}
          <div className="flex items-center justify-center gap-4">
            <span className={cn(
              "text-sm font-medium transition-colors w-16 text-right",
              !isAnnual ? "text-white" : "text-gray-500"
            )}>
              Monthly
            </span>
            <button
              onClick={() => setIsAnnual(!isAnnual)}
              className="relative w-14 h-7 rounded-full transition-all duration-300 flex-shrink-0"
              style={isAnnual ? {
                background: 'linear-gradient(180deg, rgb(79, 26, 214) 0%, rgb(128, 89, 227) 100%)'
              } : {
                backgroundColor: 'rgba(255, 255, 255, 0.2)'
              }}
            >
              <motion.div
                animate={{ left: isAnnual ? '32px' : '4px' }}
                transition={{ type: 'spring', stiffness: 500, damping: 30 }}
                className="absolute top-1 w-5 h-5 bg-white rounded-full shadow-lg"
              />
            </button>
            <div className="flex items-center gap-2">
              <span className={cn(
                "text-sm font-medium transition-colors w-16",
                isAnnual ? "text-white" : "text-gray-500"
              )}>
                Annual
              </span>
              <span className={cn(
                "px-2 py-1 bg-emerald-500/20 text-emerald-400 text-xs font-medium rounded-full transition-opacity duration-300 whitespace-nowrap",
                isAnnual ? "opacity-100" : "opacity-0"
              )}>
                Save 20%
              </span>
            </div>
          </div>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-5 gap-4">
          {plans.map((plan) => {
            const price = isAnnual ? plan.annualPrice : plan.monthlyPrice;
            const isProcessing = processingPlan === plan.name;

            return (
              <motion.div
                key={plan.name}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className={cn(
                  "relative p-5 rounded-2xl border transition-all flex flex-col",
                  plan.popular
                    ? "bg-white/5 hover:border-purple-500/50"
                    : "bg-white/5 border-white/10 hover:border-white/20"
                )}
                style={plan.popular ? {
                  borderColor: 'rgb(128, 89, 227)'
                } : {}}
              >
                {plan.popular && (
                  <div
                    className="absolute -top-3 left-1/2 -translate-x-1/2 px-3 py-1 text-white text-xs font-medium rounded-full"
                    style={{
                      background: 'linear-gradient(180deg, rgb(79, 26, 214) 0%, rgb(128, 89, 227) 100%)'
                    }}
                  >
                    Most Popular
                  </div>
                )}
                <h3 className="text-xl font-medium text-white mb-2">{plan.name}</h3>
                <div className="mb-4">
                  {price !== null ? (
                    <>
                      <span className="text-4xl font-medium text-white">${price}</span>
                      <span className="text-gray-400">/month</span>
                      {isAnnual && price > 0 && (
                        <div className="text-xs text-gray-500 mt-1">(billed annually)</div>
                      )}
                    </>
                  ) : (
                    <span className="text-4xl font-medium text-white">Custom</span>
                  )}
                </div>
                <p className="text-sm text-gray-400 mb-6">{plan.description}</p>
                <ul className="space-y-3 mb-8 flex-grow min-h-[180px]">
                  {plan.features.map((feature) => (
                    <li key={feature} className="flex items-center gap-2 text-sm text-white">
                      <Check className="w-4 h-4 text-white flex-shrink-0" />
                      {feature}
                    </li>
                  ))}
                </ul>
                {plan.disabled ? (
                  <button
                    disabled
                    className="block w-full py-3 rounded-[10px] font-medium text-center transition-all mt-auto bg-white/10 text-gray-500 cursor-not-allowed"
                  >
                    {plan.cta}
                  </button>
                ) : (
                  <button
                    onClick={() => handleCheckout(plan.name, plan.checkoutUrl)}
                    disabled={isProcessing}
                    className="block w-full py-3 rounded-[10px] font-medium text-center transition-all mt-auto disabled:opacity-50 disabled:cursor-wait"
                    style={plan.popular ? {
                      background: 'linear-gradient(180deg, rgb(79, 26, 214) 0%, rgb(128, 89, 227) 100%)',
                      color: 'white'
                    } : {
                      backgroundColor: 'rgba(255, 255, 255, 0.15)',
                      color: 'white'
                    }}
                  >
                    {isProcessing ? (
                      <span className="flex items-center justify-center gap-2">
                        <Loader2 className="w-4 h-4 animate-spin" />
                        Processing...
                      </span>
                    ) : plan.cta}
                  </button>
                )}
              </motion.div>
            );
          })}
        </div>

        {/* Secure Payments Badge */}
        <div className="flex justify-center items-center gap-2 mt-12">
          <span className="text-gray-400 text-sm">Secure Payments By</span>
          <img src="/dodo.svg" alt="DODO Payments" className="h-6" />
        </div>

        {/* FAQ or additional info */}
        <div className="text-center text-gray-400 mt-8">
          <p className="mb-4">All plans include a 14-day free trial. No credit card required.</p>
          <p>Need help choosing? <a href="mailto:overseexcorporation@gmail.com" className="text-purple-400 hover:text-purple-300">Contact sales</a></p>
        </div>
      </div>
    </div>
  );
}
