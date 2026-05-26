"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { 
  LayoutDashboard, 
  Briefcase, 
  Users, 
  FileCheck, 
  AlertTriangle, 
  Settings,
  Calendar,
  Layers
} from "lucide-react";
import { cn } from "@/lib/utils";

const navigation = [
  { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
  { name: 'Projects', href: '/projects', icon: Briefcase },
  { name: 'WBS & Planning', href: '/planning', icon: Layers },
  { name: 'Resources', href: '/resources', icon: Users },
  { name: 'Deliverables', href: '/deliverables', icon: FileCheck },
  { name: 'Risk Register', href: '/risks', icon: AlertTriangle },
  { name: 'Calendar', href: '/calendar', icon: Calendar },
  { name: 'Settings', href: '/settings', icon: Settings },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <div className="flex h-full w-64 flex-col bg-slate-900 border-r border-slate-800">
      <div className="flex h-16 items-center px-6">
        <span className="text-xl font-bold tracking-tighter text-blue-500">NEXUS V3</span>
      </div>
      <nav className="flex-1 space-y-1 px-4 py-4">
        {navigation.map((item) => {
          const isActive = pathname.startsWith(item.href);
          return (
            <Link
              key={item.name}
              href={item.href}
              className={cn(
                "group flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors",
                isActive 
                  ? "bg-blue-600/10 text-blue-400" 
                  : "text-slate-400 hover:bg-slate-800 hover:text-slate-200"
              )}
            >
              <item.icon className={cn(
                "mr-3 h-5 w-5 flex-shrink-0",
                isActive ? "text-blue-400" : "text-slate-500 group-hover:text-slate-300"
              )} />
              {item.name}
            </Link>
          );
        })}
      </nav>
      <div className="p-4 border-t border-slate-800">
        <div className="bg-slate-800/50 rounded-lg p-3">
          <p className="text-xs text-slate-500 mb-1">Active Baseline</p>
          <p className="text-sm font-medium text-slate-300 truncate">B0_Initial_Setup</p>
        </div>
      </div>
    </div>
  );
}
