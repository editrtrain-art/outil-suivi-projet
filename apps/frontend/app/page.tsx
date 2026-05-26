"use client";

import { 
  Show,
  SignInButton, 
  SignUpButton 
} from "@clerk/nextjs";
import { 
  Activity, 
  ArrowRight, 
  BarChart3, 
  Brain, 
  Calendar, 
  Layers, 
  Shield, 
  Users 
} from "lucide-react";
import Link from "next/link";

export default function Home() {
  return (
    <div className="flex flex-col min-h-screen bg-slate-950 font-sans selection:bg-purple-500 selection:text-white overflow-x-hidden">
      {/* Background radial glow */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full max-w-7xl h-[600px] bg-[radial-gradient(ellipse_at_top,rgba(99,102,241,0.15),transparent_50%)] pointer-events-none" />

      {/* Header */}
      <header className="glass-panel sticky top-0 z-50 w-full border-b border-slate-900 bg-slate-950/80">
        <div className="container mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="h-9 w-9 rounded-lg bg-gradient-to-tr from-violet-600 to-indigo-600 flex items-center justify-center shadow-lg shadow-indigo-500/20">
              <Activity className="h-5 w-5 text-white" />
            </div>
            <span className="font-bold text-xl tracking-tight bg-gradient-to-r from-white via-slate-200 to-slate-400 bg-clip-text text-transparent">
              NEXUS
            </span>
          </div>

          <nav className="hidden md:flex items-center gap-8 text-sm font-medium text-slate-400">
            <a href="#features" className="hover:text-white transition-colors">Features</a>
            <a href="#engine" className="hover:text-white transition-colors">CPM & Leveling</a>
            <a href="#evm" className="hover:text-white transition-colors">EVM Metrics</a>
          </nav>

          <div className="flex items-center gap-4">
            <Show when="signed-out">
              <SignInButton mode="modal">
                <button className="text-slate-400 hover:text-white transition-colors text-sm font-medium px-4 py-2">
                  Sign In
                </button>
              </SignInButton>
              <SignUpButton mode="modal">
                <button className="bg-white hover:bg-slate-200 text-slate-950 font-semibold px-4 py-2 rounded-lg text-sm transition-all shadow-sm">
                  Get Started
                </button>
              </SignUpButton>
            </Show>
            <Show when="signed-in">
              <Link 
                href="/dashboard"
                className="bg-indigo-600 hover:bg-indigo-500 text-white font-medium px-4 py-2 rounded-lg text-sm transition-all flex items-center gap-2 shadow-lg shadow-indigo-600/25"
              >
                Go to Dashboard
                <ArrowRight className="h-4 w-4" />
              </Link>
            </Show>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="container mx-auto px-6 pt-24 pb-16 text-center relative z-10">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-indigo-500/30 bg-indigo-500/10 text-indigo-400 text-xs font-semibold mb-8 animate-pulse">
          <Brain className="h-3.5 w-3.5" />
          <span>NEXUS v3.0 Powered with AI & CPM Engine</span>
        </div>

        <h1 className="text-4xl md:text-6xl font-black tracking-tight max-w-4xl mx-auto leading-tight md:leading-none mb-6">
          Enterprise-Grade{" "}
          <span className="bg-gradient-to-r from-indigo-400 via-violet-400 to-fuchsia-400 bg-clip-text text-transparent">
            Project Control
          </span>{" "}
          & EVM Engine.
        </h1>

        <p className="text-slate-400 text-lg md:text-xl max-w-2xl mx-auto mb-10 leading-relaxed">
          Unlock maximum predictability. Harness structural critical path scheduling, multi-baseline comparison, resource smoothing, and real-time EVM forecasting in one seamless cockpit.
        </p>

        <div className="flex flex-col sm:flex-row justify-center items-center gap-4">
          <Show when="signed-out">
            <SignUpButton mode="modal">
              <button className="w-full sm:w-auto bg-indigo-600 hover:bg-indigo-500 text-white font-semibold px-8 py-3.5 rounded-xl transition-all shadow-lg shadow-indigo-600/30 flex items-center justify-center gap-2">
                Start Free Trial
                <ArrowRight className="h-4 w-4" />
              </button>
            </SignUpButton>
          </Show>
          <Show when="signed-in">
            <Link 
              href="/dashboard"
              className="w-full sm:w-auto bg-indigo-600 hover:bg-indigo-500 text-white font-semibold px-8 py-3.5 rounded-xl transition-all shadow-lg shadow-indigo-600/30 flex items-center justify-center gap-2"
            >
              Open Dashboard
              <ArrowRight className="h-4 w-4" />
            </Link>
          </Show>
          <a 
            href="#features" 
            className="w-full sm:w-auto glass-card hover:bg-slate-900/60 text-slate-300 hover:text-white font-semibold px-8 py-3.5 rounded-xl transition-all flex items-center justify-center"
          >
            Explore Features
          </a>
        </div>
      </section>

      {/* Features Grid */}
      <section id="features" className="container mx-auto px-6 py-20 relative z-10 border-t border-slate-900">
        <div className="text-center mb-16">
          <h2 className="text-3xl font-bold text-white mb-4">Engineered for High-Stake Projects</h2>
          <p className="text-slate-400 max-w-lg mx-auto">
            NEXUS replaces complex, disconnected schedules and spreadsheets with integrated project controls.
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-8">
          {/* Card 1 */}
          <div className="glass-card p-8 rounded-2xl hover:border-indigo-500/30 transition-all group">
            <div className="h-12 w-12 rounded-xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
              <Calendar className="h-6 w-6 text-indigo-400" />
            </div>
            <h3 className="text-xl font-semibold text-white mb-3">CPM Scheduling Engine</h3>
            <p className="text-slate-400 text-sm leading-relaxed">
              Iterative, recursion-free calculation of Early/Late dates, Slack times, and Critical Path detection. Handles complex dependency matrices natively.
            </p>
          </div>

          {/* Card 2 */}
          <div className="glass-card p-8 rounded-2xl hover:border-violet-500/30 transition-all group">
            <div className="h-12 w-12 rounded-xl bg-violet-500/10 border border-violet-500/20 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
              <BarChart3 className="h-6 w-6 text-violet-400" />
            </div>
            <h3 className="text-xl font-semibold text-white mb-3">Earned Value (EVM) Controls</h3>
            <p className="text-slate-400 text-sm leading-relaxed">
              Track physical progress against baselines. Instantly compute PV, EV, AC, Schedule Variance (SV), Cost Variance (CV), CPI, and SPI.
            </p>
          </div>

          {/* Card 3 */}
          <div className="glass-card p-8 rounded-2xl hover:border-fuchsia-500/30 transition-all group">
            <div className="h-12 w-12 rounded-xl bg-fuchsia-500/10 border border-fuchsia-500/20 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
              <Users className="h-6 w-6 text-fuchsia-400" />
            </div>
            <h3 className="text-xl font-semibold text-white mb-3">Resource Leveling & Smoothing</h3>
            <p className="text-slate-400 text-sm leading-relaxed">
              Detect and resolve over-allocations of shared resources across concurrent projects using advanced heuristic leveling and smoothing algorithms.
            </p>
          </div>

          {/* Card 4 */}
          <div className="glass-card p-8 rounded-2xl hover:border-pink-500/30 transition-all group">
            <div className="h-12 w-12 rounded-xl bg-pink-500/10 border border-pink-500/20 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
              <Layers className="h-6 w-6 text-pink-400" />
            </div>
            <h3 className="text-xl font-semibold text-white mb-3">Multi-Baseline Versioning</h3>
            <p className="text-slate-400 text-sm leading-relaxed">
              Store snapshots of your schedules. Easily trace deviations and variances, analyze delays, and prove target slippage using comparative metrics.
            </p>
          </div>

          {/* Card 5 */}
          <div className="glass-card p-8 rounded-2xl hover:border-cyan-500/30 transition-all group">
            <div className="h-12 w-12 rounded-xl bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
              <Brain className="h-6 w-6 text-cyan-400" />
            </div>
            <h3 className="text-xl font-semibold text-white mb-3">AI-Predictive Engine</h3>
            <p className="text-slate-400 text-sm leading-relaxed">
              Agnostic LLM engine supporting local Ollama or cloud models to forecast potential risk, critical delays, and optimize task structures.
            </p>
          </div>

          {/* Card 6 */}
          <div className="glass-card p-8 rounded-2xl hover:border-emerald-500/30 transition-all group">
            <div className="h-12 w-12 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
              <Shield className="h-6 w-6 text-emerald-400" />
            </div>
            <h3 className="text-xl font-semibold text-white mb-3">Enterprise Grade RLS</h3>
            <p className="text-slate-400 text-sm leading-relaxed">
              Multi-tenant architecture powered by PostgreSQL Row-Level Security, Supabase, and role-based permissions (RBAC) to keep project data secure.
            </p>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="mt-auto border-t border-slate-900 py-8 bg-slate-950/60 relative z-10 text-center text-slate-500 text-xs">
        <p>© 2026 NEXUS — SNTE. All rights reserved.</p>
      </footer>
    </div>
  );
}
