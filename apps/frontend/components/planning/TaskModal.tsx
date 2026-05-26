"use client";

import React, { useState } from "react";
import { Button } from "@/components/ui/button";
import { Task } from "@/types";
import { Phase } from "@/hooks";

interface TaskModalProps {
  isOpen: boolean;
  onClose: () => void;
  phases: Phase[] | undefined;
  tasks: Task[] | undefined;
  onSubmit: (data: {
    phaseId: string;
    name: string;
    durationDays: number;
    parentTaskId: string | null;
    weightPercent: number;
    priority: number;
    isMilestone: boolean;
  }) => Promise<void>;
  isPending: boolean;
}

export function TaskModal({
  isOpen,
  onClose,
  phases,
  tasks,
  onSubmit,
  isPending,
}: TaskModalProps) {
  const [taskName, setTaskName] = useState("");
  const [taskPhaseId, setTaskPhaseId] = useState(phases?.[0]?.id || "");
  const [taskDuration, setTaskDuration] = useState("5");
  const [taskWeight, setTaskWeight] = useState("0");
  const [taskPriority, setTaskPriority] = useState("3");
  const [taskIsMilestone, setTaskIsMilestone] = useState(false);
  const [taskParentId, setTaskParentId] = useState("");

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await onSubmit({
      phaseId: taskPhaseId || phases?.[0]?.id || "",
      name: taskName,
      durationDays: parseInt(taskDuration) || 0,
      parentTaskId: taskParentId || null,
      weightPercent: parseFloat(taskWeight) || 0,
      priority: parseInt(taskPriority) || 3,
      isMilestone: taskIsMilestone,
    });
    setTaskName("");
    setTaskDuration("5");
    setTaskWeight("0");
    setTaskIsMilestone(false);
    setTaskParentId("");
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/85 backdrop-blur-sm p-4 animate-in fade-in duration-200">
      <div className="w-full max-w-md bg-slate-900 border border-slate-800 rounded-xl p-6 space-y-6 shadow-2xl scale-in-95 duration-200">
        <div>
          <h3 className="text-lg font-semibold text-slate-200">Add Task</h3>
          <p className="text-xs text-slate-400">Insert task under selected phase.</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-1.5">
            <label className="text-xs font-semibold text-slate-400">Target Phase</label>
            <select
              value={taskPhaseId}
              onChange={(e) => setTaskPhaseId(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-lg py-2 px-3 text-sm text-slate-200 focus:outline-none focus:ring-1 focus:ring-blue-500/50"
            >
              <option value="">Select Phase...</option>
              {phases?.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.wbsCode} — {p.name}
                </option>
              ))}
            </select>
          </div>

          <div className="space-y-1.5">
            <label className="text-xs font-semibold text-slate-400">Task Name</label>
            <input
              type="text"
              required
              placeholder="e.g. Masonry Walls Construction"
              value={taskName}
              onChange={(e) => setTaskName(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-lg py-2 px-3 text-sm text-slate-200 focus:outline-none focus:ring-1 focus:ring-blue-500/50"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-slate-400">Duration (Days)</label>
              <input
                type="number"
                min="0"
                required
                value={taskDuration}
                onChange={(e) => setTaskDuration(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg py-2 px-3 text-sm text-slate-200 focus:outline-none focus:ring-1 focus:ring-blue-500/50"
              />
            </div>
            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-slate-400">Parent Task (WBS)</label>
              <select
                value={taskParentId}
                onChange={(e) => setTaskParentId(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg py-2 px-3 text-sm text-slate-200 focus:outline-none focus:ring-1 focus:ring-blue-500/50"
              >
                <option value="">None (Root Task)</option>
                {tasks
                  ?.filter((t) => !t.isMilestone)
                  .map((t) => (
                    <option key={t.id} value={t.id}>
                      {t.wbs} — {t.name}
                    </option>
                  ))}
              </select>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-slate-400">Weight Percent (%)</label>
              <input
                type="number"
                step="0.1"
                min="0"
                max="100"
                required
                value={taskWeight}
                onChange={(e) => setTaskWeight(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg py-2 px-3 text-sm text-slate-200 focus:outline-none focus:ring-1 focus:ring-blue-500/50"
              />
            </div>
            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-slate-400">Priority</label>
              <select
                value={taskPriority}
                onChange={(e) => setTaskPriority(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg py-2 px-3 text-sm text-slate-200 focus:outline-none focus:ring-1 focus:ring-blue-500/50"
              >
                <option value="1">1 — Highest</option>
                <option value="2">2 — High</option>
                <option value="3">3 — Medium</option>
                <option value="4">4 — Low</option>
                <option value="5">5 — Lowest</option>
              </select>
            </div>
          </div>

          <div className="flex items-center gap-2 py-2">
            <input
              type="checkbox"
              id="isMilestone"
              checked={taskIsMilestone}
              onChange={(e) => setTaskIsMilestone(e.target.checked)}
              className="rounded border-slate-800 bg-slate-950 text-blue-500 focus:ring-0 focus:ring-offset-0"
            />
            <label htmlFor="isMilestone" className="text-xs font-semibold text-slate-400 cursor-pointer select-none">
              Is Milestone (Duration = 0)
            </label>
          </div>

          <div className="flex justify-end gap-3 pt-4 border-t border-slate-800/80">
            <Button
              type="button"
              variant="outline"
              onClick={onClose}
              className="bg-slate-900 border-slate-800 text-slate-400 hover:bg-slate-800 hover:text-slate-200"
            >
              Cancel
            </Button>
            <Button
              type="submit"
              disabled={isPending}
              className="bg-blue-600 hover:bg-blue-500 text-white font-medium"
            >
              {isPending ? "Adding..." : "Add Task"}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}
