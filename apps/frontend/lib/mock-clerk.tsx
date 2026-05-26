"use client";

import React from "react";

// Mock ClerkProvider: simply renders its children
export function ClerkProvider({ children }: { children: React.ReactNode }) {
  return <>{children}</>;
}

// Mock Show: conditionally renders children based on auth status
export function Show({ when, children }: { when: "signed-in" | "signed-out"; children: React.ReactNode }) {
  // In sandbox mock mode, we are always considered "signed in"
  if (when === "signed-in") {
    return <>{children}</>;
  }
  return null;
}

// Mock SignInButton: redirects to dashboard on click
export function SignInButton({ children }: { children?: React.ReactNode }) {
  if (React.isValidElement(children)) {
    return React.cloneElement(children as any, {
      onClick: (e: React.MouseEvent) => {
        if ((children.props as any).onClick) (children.props as any).onClick(e);
        window.location.href = "/dashboard";
      }
    });
  }
  return (
    <button 
      onClick={() => window.location.href = "/dashboard"}
      className="text-slate-400 hover:text-white transition-colors text-sm font-medium px-4 py-2"
    >
      {children || "Sign In"}
    </button>
  );
}

// Mock SignUpButton: redirects to dashboard on click
export function SignUpButton({ children }: { children?: React.ReactNode }) {
  if (React.isValidElement(children)) {
    return React.cloneElement(children as any, {
      onClick: (e: React.MouseEvent) => {
        if ((children.props as any).onClick) (children.props as any).onClick(e);
        window.location.href = "/dashboard";
      }
    });
  }
  return (
    <button 
      onClick={() => window.location.href = "/dashboard"}
      className="bg-white hover:bg-slate-200 text-slate-950 font-semibold px-4 py-2 rounded-lg text-sm transition-all shadow-sm"
    >
      {children || "Get Started"}
    </button>
  );
}

// Mock UserButton: displays a premium sandbox user badge
export function UserButton() {
  return (
    <div className="flex items-center gap-2 bg-slate-800/80 backdrop-blur-md text-slate-200 px-3 py-1.5 rounded-lg border border-slate-700/60 text-xs shadow-sm hover:bg-slate-700/80 transition-all select-none">
      <div className="h-5 w-5 rounded-full bg-gradient-to-tr from-violet-600 to-indigo-600 flex items-center justify-center font-bold text-[10px] text-white shadow-md">
        S
      </div>
      <span className="font-semibold text-slate-300">Sandbox Admin</span>
    </div>
  );
}

// Mock OrganizationSwitcher: displays the active workspace indicator
export function OrganizationSwitcher() {
  return (
    <div className="bg-slate-800/80 backdrop-blur-md text-slate-200 px-3.5 py-1.5 rounded-lg border border-slate-700/60 text-xs font-semibold shadow-sm flex items-center gap-2 select-none hover:bg-slate-700/80 transition-all">
      <span className="text-indigo-400">💼</span>
      <span>Default Workspace</span>
    </div>
  );
}

// Mock useAuth hook: returns dummy user/org context and mock token generator
export function useAuth() {
  return {
    orgId: "00000000-0000-0000-0000-000000000001",
    userId: "00000000-0000-0000-0000-000000000002",
    getToken: async () => {
      // Deterministic mock token format parsed by apps/backend/app/core/dependencies.py
      return "mock_admin_user123_admin@nexus.local";
    },
  };
}

// Mock SignIn Component: a beautiful glassmorphic card for passwordless entry
export function SignIn() {
  return (
    <div className="w-full max-w-md p-8 bg-slate-900/60 backdrop-blur-xl border border-slate-800/80 rounded-2xl shadow-2xl text-center space-y-6">
      <div className="space-y-2">
        <h2 className="text-2xl font-bold text-white tracking-tight">Accès Sandbox</h2>
        <p className="text-sm text-slate-400">L'authentification est désactivée. Vous êtes connecté sous le profil Administrateur.</p>
      </div>

      <div className="p-4 bg-slate-950/40 rounded-xl border border-slate-800/60 text-left space-y-3">
        <div className="flex justify-between text-xs border-b border-slate-900 pb-2">
          <span className="text-slate-500">Rôle :</span>
          <span className="text-indigo-400 font-bold">Chef de Projet (Admin)</span>
        </div>
        <div className="flex justify-between text-xs border-b border-slate-900 pb-2">
          <span className="text-slate-500">Email :</span>
          <span className="text-slate-300">admin@nexus.local</span>
        </div>
        <div className="flex justify-between text-xs">
          <span className="text-slate-500">Mode Base de Données :</span>
          <span className="text-emerald-400 font-medium">SQLite Autonome</span>
        </div>
      </div>

      <button
        onClick={() => window.location.href = "/dashboard"}
        className="w-full bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-500 hover:to-indigo-500 text-white font-semibold py-3 px-4 rounded-xl shadow-lg shadow-indigo-600/20 transition-all flex items-center justify-center gap-2 group"
      >
        Entrer dans le Dashboard
        <span className="group-hover:translate-x-1 transition-transform">→</span>
      </button>
    </div>
  );
}

// Mock SignUp Component: identical to SignIn for seamless sandbox entry
export function SignUp() {
  return <SignIn />;
}
