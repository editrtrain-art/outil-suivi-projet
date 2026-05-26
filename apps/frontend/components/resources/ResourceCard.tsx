"use client";

import { cn } from "@/lib/utils";
import { User, Mail, DollarSign, Activity } from "lucide-react";

interface ResourceCardProps {
  resource: {
    id: string;
    name: string;
    role: string;
    email: string;
    rate: number;
    allocation: number;
    status: 'active' | 'inactive';
  };
}

export function ResourceCard({ resource }: ResourceCardProps) {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 hover:border-slate-700 transition-all">
      <div className="flex items-center gap-4 mb-4">
        <div className="h-12 w-12 rounded-full bg-blue-500/10 border border-blue-500/20 flex items-center justify-center text-blue-400">
          <User className="h-6 w-6" />
        </div>
        <div>
          <h3 className="text-slate-100 font-semibold">{resource.name}</h3>
          <p className="text-slate-500 text-xs">{resource.role}</p>
        </div>
      </div>
      
      <div className="space-y-3">
        <div className="flex justify-between text-xs">
          <span className="text-slate-500 flex items-center gap-1.5"><Mail className="h-3 w-3" /> Email</span>
          <span className="text-slate-300">{resource.email}</span>
        </div>
        <div className="flex justify-between text-xs">
          <span className="text-slate-500 flex items-center gap-1.5"><DollarSign className="h-3 w-3" /> Hourly Rate</span>
          <span className="text-slate-300">{resource.rate} DH/h</span>
        </div>
        <div className="pt-2 border-t border-slate-800">
          <div className="flex justify-between text-xs mb-1.5">
            <span className="text-slate-500 flex items-center gap-1.5"><Activity className="h-3 w-3" /> Current Load</span>
            <span className={cn(
              "font-bold",
              resource.allocation > 100 ? "text-rose-500" : resource.allocation > 80 ? "text-amber-500" : "text-emerald-500"
            )}>{resource.allocation}%</span>
          </div>
          <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
            <div 
              className={cn(
                "h-full transition-all",
                resource.allocation > 100 ? "bg-rose-500" : resource.allocation > 80 ? "bg-amber-500" : "bg-emerald-500"
              )} 
              style={{ width: `${Math.min(resource.allocation, 100)}%` }}
            ></div>
          </div>
        </div>
      </div>
    </div>
  );
}
