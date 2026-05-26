"use client";

import { cn } from "@/lib/utils";
import { ChevronRight, ChevronDown, Diamond, Clock } from "lucide-react";
import { useState } from "react";

interface TaskRowProps {
  task: {
    id: string;
    wbs: string;
    name: string;
    duration: number;
    start: string;
    finish: string;
    progress: number;
    isCritical: boolean;
    isMilestone: boolean;
    subtasks?: any[];
  };
  level: number;
}

export function TaskRow({ task, level }: TaskRowProps) {
  const [isExpanded, setIsExpanded] = useState(true);
  const hasSubtasks = task.subtasks && task.subtasks.length > 0;

  return (
    <>
      <div className={cn(
        "group flex items-center border-b border-slate-800 hover:bg-slate-800/30 py-2 transition-colors",
        task.isCritical && "bg-rose-500/5"
      )}>
        <div className="flex items-center px-4 min-w-[300px]" style={{ paddingLeft: `${level * 1.5 + 1}rem` }}>
          <div className="w-6 flex-shrink-0">
            {hasSubtasks ? (
              <button onClick={() => setIsExpanded(!isExpanded)} className="p-0.5 hover:bg-slate-700 rounded text-slate-500">
                {isExpanded ? <ChevronDown className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
              </button>
            ) : (
              <div className="w-4 h-4 flex items-center justify-center">
                {task.isMilestone ? <Diamond className="h-3 w-3 text-amber-500 fill-amber-500" /> : <div className="w-1.5 h-1.5 rounded-full bg-slate-700"></div>}
              </div>
            )}
          </div>
          <span className="text-[11px] font-mono text-slate-500 w-12 flex-shrink-0">{task.wbs}</span>
          <span className={cn(
            "text-sm truncate",
            hasSubtasks ? "font-semibold text-slate-200" : "text-slate-300",
            task.isCritical && "text-rose-400"
          )}>
            {task.name}
          </span>
        </div>

        <div className="flex-1 flex items-center gap-8 px-4 text-[12px] text-slate-400">
          <div className="w-20 text-center">{task.duration}d</div>
          <div className="w-28 text-center font-mono">{task.start}</div>
          <div className="w-28 text-center font-mono">{task.finish}</div>
          <div className="w-24">
            <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
              <div 
                className={cn("h-full transition-all", task.isCritical ? "bg-rose-500" : "bg-blue-500")} 
                style={{ width: `${task.progress}%` }}
              ></div>
            </div>
          </div>
          <div className="w-16 text-right font-medium">{task.progress}%</div>
        </div>
      </div>
      
      {isExpanded && hasSubtasks && (
        <div>
          {task.subtasks!.map((sub) => (
            <TaskRow key={sub.id} task={sub} level={level + 1} />
          ))}
        </div>
      )}
    </>
  );
}
