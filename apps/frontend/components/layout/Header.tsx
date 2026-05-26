"use client";

import { UserButton, OrganizationSwitcher, useAuth } from "@clerk/nextjs";
import { Bell, Search, Info } from "lucide-react";
import { dark } from "@clerk/themes";
import { useEffect } from "react";
import { useNexusStore } from "@/lib/store";

export function Header() {
  const { orgId, userId } = useAuth();
  const setActiveWorkspaceId = useNexusStore((state) => state.setActiveWorkspaceId);

  useEffect(() => {
    const activeId = orgId || userId || null;
    setActiveWorkspaceId(activeId);
  }, [orgId, userId, setActiveWorkspaceId]);
  return (
    <header className="h-16 border-b border-slate-800 bg-slate-900/50 backdrop-blur-md px-8 flex items-center justify-between sticky top-0 z-30">
      <div className="flex items-center gap-8 flex-1">
        <div className="hidden md:flex">
          <OrganizationSwitcher 
            appearance={{ 
              baseTheme: dark,
              elements: {
                organizationSwitcherTrigger: "bg-slate-800 hover:bg-slate-700 text-slate-200 px-3 py-1.5 rounded-md border border-slate-700 transition-colors"
              }
            }} 
          />
        </div>
        
        <div className="max-w-md w-full relative group">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-500 group-focus-within:text-blue-400 transition-colors" />
          <input 
            type="text" 
            placeholder="Search projects, tasks, or resources..." 
            className="w-full bg-slate-950/50 border border-slate-800 rounded-full py-1.5 pl-10 pr-4 text-sm focus:outline-none focus:ring-1 focus:ring-blue-500/50 focus:border-blue-500/50 transition-all"
          />
        </div>
      </div>

      <div className="flex items-center gap-4">
        <button className="p-2 text-slate-400 hover:text-slate-200 hover:bg-slate-800 rounded-full transition-all relative">
          <Bell className="h-5 w-5" />
          <span className="absolute top-2 right-2 h-2 w-2 bg-blue-500 rounded-full ring-2 ring-slate-900"></span>
        </button>
        
        <button className="p-2 text-slate-400 hover:text-slate-200 hover:bg-slate-800 rounded-full transition-all">
          <Info className="h-5 w-5" />
        </button>

        <div className="h-6 w-px bg-slate-800 mx-2"></div>

        <UserButton 
          appearance={{ baseTheme: dark }}
        />
      </div>
    </header>
  );
}
