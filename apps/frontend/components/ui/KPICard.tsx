"use client";

import { cn } from "@/lib/utils";
import { TrendingUp, TrendingDown, Minus } from "lucide-react";

interface KPICardProps {
  title: string;
  value: string | number;
  trend?: number;
  unit?: string;
  description?: string;
  status?: 'success' | 'warning' | 'danger' | 'info';
}

export function KPICard({ title, value, trend, unit, description, status = 'info' }: KPICardProps) {
  const statusColors = {
    success: "text-emerald-400 bg-emerald-500/10 border-emerald-500/20",
    warning: "text-amber-400 bg-amber-500/10 border-amber-500/20",
    danger: "text-rose-400 bg-rose-500/10 border-rose-500/20",
    info: "text-blue-400 bg-blue-500/10 border-blue-500/20",
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 hover:border-slate-700 transition-all shadow-lg shadow-black/20">
      <div className="flex justify-between items-start mb-2">
        <h3 className="text-slate-400 text-sm font-medium">{title}</h3>
        {status && (
          <span className={cn("px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider border", statusColors[status])}>
            {status}
          </span>
        )}
      </div>
      
      <div className="flex items-baseline gap-1">
        <span className="text-2xl font-bold text-slate-100">{value}</span>
        {unit && <span className="text-slate-500 text-xs font-medium uppercase">{unit}</span>}
      </div>

      <div className="mt-4 flex items-center justify-between">
        {description && <p className="text-xs text-slate-500 line-clamp-1">{description}</p>}
        {trend !== undefined && (
          <div className={cn(
            "flex items-center text-xs font-bold",
            trend > 0 ? "text-emerald-400" : trend < 0 ? "text-rose-400" : "text-slate-500"
          )}>
            {trend > 0 ? <TrendingUp className="h-3 w-3 mr-1" /> : trend < 0 ? <TrendingDown className="h-3 w-3 mr-1" /> : <Minus className="h-3 w-3 mr-1" />}
            {Math.abs(trend)}%
          </div>
        )}
      </div>
    </div>
  );
}
