"use client";

import React from "react";
import { format, differenceInDays } from "date-fns";
import { Task } from "@/types";

interface GanttChartProps {
  tasks: Task[] | undefined;
  viewStart: Date;
  viewEnd: Date;
  totalViewDays: number;
  baselineTaskMap: Map<string, { start: string; finish: string }>;
}

export function GanttChart({
  tasks,
  viewStart,
  totalViewDays,
  baselineTaskMap,
}: GanttChartProps) {
  return (
    <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-6 min-h-[300px] space-y-4 shadow-xl backdrop-blur-sm">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-slate-200 tracking-wide">Gantt Timeline</h3>
        <div className="flex items-center gap-4">
          <span className="flex items-center gap-2 text-xs text-rose-400">
            <span className="w-3 h-3 bg-rose-500 rounded-sm shadow-sm shadow-rose-500/20"></span>
            Critical Path
          </span>
          <span className="flex items-center gap-2 text-xs text-blue-400">
            <span className="w-3 h-3 bg-blue-500 rounded-sm shadow-sm shadow-blue-500/20"></span>
            Standard Task
          </span>
          <span className="flex items-center gap-2 text-xs text-amber-500">
            <span className="w-3.5 h-3.5 rotate-45 bg-amber-500 border border-slate-950"></span>
            Milestone
          </span>
        </div>
      </div>

      <div className="overflow-x-auto custom-scrollbar rounded-lg border border-slate-800/40">
        <svg
          width="100%"
          height={Math.max((tasks?.length || 0) * 45 + 50, 200)}
          className="min-w-[800px] bg-slate-950/40 p-4 font-mono text-[10px]"
        >
          {/* Timeline scale header */}
          <line x1="0" y1="30" x2="100%" y2="30" stroke="#1e293b" />
          {Array.from({ length: 6 }).map((_, i) => {
            const dayOffset = (totalViewDays / 5) * i;
            const d = new Date(viewStart.getTime() + dayOffset * 24 * 60 * 60 * 1000);
            const xPct = `${(dayOffset / totalViewDays) * 80 + 15}%`;
            return (
              <g key={i}>
                <text x={xPct} y="20" fill="#64748b" textAnchor="middle" className="font-semibold">
                  {format(d, "MMM dd")}
                </text>
                <line x1={xPct} y1="30" x2={xPct} y2="100%" stroke="#1e293b" strokeDasharray="3 3" />
              </g>
            );
          })}

          {/* Draw task rows */}
          {tasks?.map((task, index) => {
            const startOffset = task.startDate ? differenceInDays(new Date(task.startDate), viewStart) : 0;
            const duration = task.durationDays || 1;
            const x = `${(startOffset / totalViewDays) * 80 + 15}%`;
            const width = `${(duration / totalViewDays) * 80}%`;
            const y = index * 40 + 50;

            const bTask = baselineTaskMap.get(task.id);
            const bStartOffset = bTask ? differenceInDays(new Date(bTask.start), viewStart) : 0;
            const bDuration = bTask ? differenceInDays(new Date(bTask.finish), new Date(bTask.start)) + 1 : 1;
            const bX = `${(bStartOffset / totalViewDays) * 80 + 15}%`;
            const bWidth = `${(bDuration / totalViewDays) * 80}%`;

            return (
              <g key={task.id} className="group">
                {/* Row background */}
                <rect
                  x="0"
                  y={y - 8}
                  width="100%"
                  height="32"
                  fill="transparent"
                  className="group-hover:fill-slate-900/40 transition-colors duration-150"
                />

                {/* Task text label */}
                <text x="2%" y={y + 12} fill="#94a3b8" className="font-semibold select-none">
                  {task.wbs} {task.name.substring(0, 18)}
                </text>

                {/* Gantt block */}
                {task.isMilestone ? (
                  <>
                    <rect
                      x={x}
                      y={y + 4}
                      width="12"
                      height="12"
                      transform={`rotate(45, ${parseFloat(x) || 0}, ${y + 10})`}
                      fill="#f59e0b"
                      className="transition-transform duration-200 group-hover:scale-110 origin-center"
                    />
                    {bTask && (
                      <rect
                        x={bX}
                        y={y + 14}
                        width="8"
                        height="8"
                        transform={`rotate(45, ${parseFloat(bX) || 0}, ${y + 18})`}
                        fill="none"
                        stroke="#64748b"
                        strokeWidth="1"
                        strokeDasharray="2 2"
                      />
                    )}
                  </>
                ) : (
                  <>
                    <rect
                      x={x}
                      y={y + 1}
                      width={width}
                      height="12"
                      rx="3"
                      fill={task.isCritical ? "#f43f5e" : "#3b82f6"}
                      opacity="0.85"
                      className="transition-all duration-200 group-hover:opacity-100 hover:brightness-110 shadow-sm"
                    />
                    {bTask && (
                      <rect
                        x={bX}
                        y={y + 15}
                        width={bWidth}
                        height="4"
                        rx="1.5"
                        fill="none"
                        stroke="#64748b"
                        strokeWidth="1"
                        strokeDasharray="2 2"
                        opacity="0.75"
                      />
                    )}
                  </>
                )}
              </g>
            );
          })}
        </svg>
      </div>
    </div>
  );
}
