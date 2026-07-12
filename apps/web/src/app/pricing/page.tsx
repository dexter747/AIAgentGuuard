'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Check, Zap, Users, Shield } from 'lucide-react';

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

export default function PricingPage() {
  const [billingCycle, setBillingCycle] = useState<'monthly' | 'annual'>('monthly');
  const [plans, setPlans] = useState<Plan[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchPlans();
  }, []);

  const fetchPlans = async () => {
    try {
      const response = await fetch('/api/billing/plans', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setPlans(data);
      }
    } catch (error) {
      console.error('Failed to fetch plans:', error);
    } finally {
      setLoading(false);
    }
  };

  const filteredPlans = plans.filter(plan => plan.billing_cycle === billingCycle);

  const handleCheckout = (checkoutUrl: string) => {
    // Redirect to DODO checkout
    window.location.href = checkoutUrl;
  };

  const getPlanIcon = (name: string) => {
    switch (name.toLowerCase()) {
      case 'starter': return Zap;
      case 'pro': return Users;
      case 'team': return Shield;
      default: return Check;
    }
  };

  const formatNumber = (num: number) => {
    if (num === -1) return 'Unlimited';
    return num.toLocaleString();
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-purple-500"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-medium text-white mb-4">
            Simple, Transparent Pricing
          </h1>
          <p className="text-xl text-gray-300 mb-8">
            Choose the perfect plan for your AI agent monitoring needs
          </p>

          {/* Billing Toggle */}
          <div className="inline-flex items-center bg-slate-800 rounded-lg p-1">
            <button
              onClick={() => setBillingCycle('monthly')}
              className={`px-6 py-2 rounded-md transition-all ${
                billingCycle === 'monthly'
                  ? 'bg-purple-600 text-white'
                  : 'text-gray-400 hover:text-white'
              }`}
            >
              Monthly
            </button>
            <button
              onClick={() => setBillingCycle('annual')}
              className={`px-6 py-2 rounded-md transition-all relative ${
                billingCycle === 'annual'
                  ? 'bg-purple-600 text-white'
                  : 'text-gray-400 hover:text-white'
              }`}
            >
              Annual
              <span className="absolute -top-2 -right-2 bg-green-500 text-white text-xs px-2 py-0.5 rounded-full">
                Save 20%
              </span>
            </button>
          </div>
        </div>

        {/* Pricing Cards */}
        <div className="grid md:grid-cols-3 gap-8 mb-12">
          {filteredPlans.map((plan, index) => {
            const Icon = getPlanIcon(plan.name);
            const isPopular = plan.name === 'Pro';

            return (
              <motion.div
                key={plan.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className={`relative bg-slate-800 rounded-2xl p-8 ${
                  isPopular ? 'ring-2 ring-purple-500 shadow-2xl shadow-purple-500/20' : ''
                }`}
              >
                {isPopular && (
                  <div className="absolute -top-4 left-1/2 -translate-x-1/2 bg-purple-500 text-white px-4 py-1 rounded-full text-sm font-medium">
                    Most Popular
                  </div>
                )}

                <div className="mb-6">
                  <div className="flex items-center gap-3 mb-4">
                    <div className={`p-3 rounded-lg ${
                      isPopular ? 'bg-purple-600' : 'bg-slate-700'
                    }`}>
                      <Icon className="w-6 h-6 text-white" />
                    </div>
                    <h3 className="text-2xl font-medium text-white">{plan.name}</h3>
                  </div>

                  <div className="flex items-baseline gap-2">
                    <span className="text-4xl font-medium text-white">${plan.amount}</span>
                    <span className="text-gray-400">
                      /{billingCycle === 'monthly' ? 'month' : 'year'}
                    </span>
                  </div>

                  {plan.savings && (
                    <p className="text-green-400 text-sm mt-2">
                      Save ${plan.savings} per year
                    </p>
                  )}
                </div>

                <button
                  onClick={() => handleCheckout(plan.checkout_url)}
                  className={`w-full py-3 rounded-lg font-medium transition-all mb-6 ${
                    isPopular
                      ? 'bg-purple-600 hover:bg-purple-700 text-white'
                      : 'bg-slate-700 hover:bg-slate-600 text-white'
                  }`}
                >
                  Get Started
                </button>

                <div className="space-y-3">
                  <div className="flex items-center gap-2 text-sm">
                    <Check className="w-4 h-4 text-green-400 flex-shrink-0" />
                    <span className="text-gray-300">
                      <strong>{formatNumber(plan.features.traces_per_month)}</strong> traces/month
                    </span>
                  </div>
                  <div className="flex items-center gap-2 text-sm">
                    <Check className="w-4 h-4 text-green-400 flex-shrink-0" />
                    <span className="text-gray-300">
                      <strong>{formatNumber(plan.features.max_agents)}</strong> agents max
                    </span>
                  </div>
                  <div className="flex items-center gap-2 text-sm">
                    <Check className="w-4 h-4 text-green-400 flex-shrink-0" />
                    <span className="text-gray-300">
                      <strong>{plan.features.trace_retention_days}</strong> days retention
                    </span>
                  </div>
                  <div className="flex items-center gap-2 text-sm">
                    <Check className="w-4 h-4 text-green-400 flex-shrink-0" />
                    <span className="text-gray-300">
                      <strong>{formatNumber(plan.features.api_calls_per_minute)}</strong> API calls/min
                    </span>
                  </div>
                  <div className="flex items-center gap-2 text-sm">
                    <Check className="w-4 h-4 text-green-400 flex-shrink-0" />
                    <span className="text-gray-300">
                      <strong>{plan.features.support}</strong> support
                    </span>
                  </div>

                  {plan.features.advanced_analytics && (
                    <div className="flex items-center gap-2 text-sm">
                      <Check className="w-4 h-4 text-green-400 flex-shrink-0" />
                      <span className="text-gray-300">Advanced analytics</span>
                    </div>
                  )}

                  {plan.features.multi_agent_analysis && (
                    <div className="flex items-center gap-2 text-sm">
                      <Check className="w-4 h-4 text-green-400 flex-shrink-0" />
                      <span className="text-gray-300">Multi-agent analysis</span>
                    </div>
                  )}

                  {plan.features.pii_redaction && (
                    <div className="flex items-center gap-2 text-sm">
                      <Check className="w-4 h-4 text-green-400 flex-shrink-0" />
                      <span className="text-gray-300">PII redaction</span>
                    </div>
                  )}

                  {plan.features.custom_integrations && (
                    <div className="flex items-center gap-2 text-sm">
                      <Check className="w-4 h-4 text-green-400 flex-shrink-0" />
                      <span className="text-gray-300">Custom integrations</span>
                    </div>
                  )}

                  {plan.features.sso && (
                    <div className="flex items-center gap-2 text-sm">
                      <Check className="w-4 h-4 text-green-400 flex-shrink-0" />
                      <span className="text-gray-300">SSO support</span>
                    </div>
                  )}

                  {plan.features.dedicated_support && (
                    <div className="flex items-center gap-2 text-sm">
                      <Check className="w-4 h-4 text-green-400 flex-shrink-0" />
                      <span className="text-gray-300">Dedicated support team</span>
                    </div>
                  )}

                  {plan.features.custom_sla && (
                    <div className="flex items-center gap-2 text-sm">
                      <Check className="w-4 h-4 text-green-400 flex-shrink-0" />
                      <span className="text-gray-300">Custom SLA</span>
                    </div>
                  )}
                </div>
              </motion.div>
            );
          })}
        </div>

        {/* Secure Payments Badge */}
        <div className="flex justify-center items-center gap-2 mt-12 mb-6">
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
