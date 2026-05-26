"use client";

import { cn } from "@/lib/utils";
import { FileText, Clock, CheckCircle2, AlertCircle, ArrowRight } from "lucide-react";

interface DeliverableCardProps {
  item: {
    id: string;
    name: string;
    task: string;
    dueDate: string;
    status: 'draft' | 'submitted' | 'in_review' | 'approved' | 'rejected';
    owner: string;
  };
}

export function DeliverableCard({ item }: DeliverableCardProps) {
  const statusConfig = {
    draft: { color: "text-slate-400 bg-slate-500/10 border-slate-500/20", icon: Clock },
    submitted: { color: "text-blue-400 bg-blue-500/10 border-blue-500/20", icon: ArrowRight },
    in_review: { color: "text-amber-400 bg-amber-500/10 border-amber-500/20", icon: Activity },
    approved: { color: "text-emerald-400 bg-emerald-500/10 border-emerald-500/20", icon: CheckCircle2 },
    rejected: { color: "text-rose-400 bg-rose-500/10 border-rose-500/20", icon: AlertCircle },
  };

  const config = statusConfig[item.status] || statusConfig.draft;

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 hover:border-slate-700 transition-all flex flex-col justify-between">
      <div>
        <div className="flex justify-between items-start mb-4">
          <div className="p-2 bg-slate-800 rounded-lg">
            <FileText className="h-5 w-5 text-slate-400" />
          </div>
          <span className={cn("px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider border", config.color)}>
            {item.status.replace('_', ' ')}
          </span>
        </div>
        
        <h3 className="text-slate-100 font-semibold text-sm mb-1">{item.name}</h3>
        <p className="text-slate-500 text-[11px] mb-4">Task: {item.task}</p>
      </div>

      <div className="space-y-3">
        <div className="flex justify-between items-center text-[11px]">
          <span className="text-slate-500">Due Date</span>
          <span className="text-slate-300 font-mono">{item.dueDate}</span>
        </div>
        <div className="flex justify-between items-center text-[11px]">
          <span className="text-slate-500">Owner</span>
          <span className="text-slate-300">{item.owner}</span>
        </div>
      </div>
    </div>
  );
}

// Minimal Activity icon shim for statusConfig
function Activity(props: any) {
  return (
    <svg
      {...props}
      xmlns="http://www.w3.org/2000/svg"
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M22 12h-4l-3 9L9 3l-3 9H2" />
    </svg>
  )
}
