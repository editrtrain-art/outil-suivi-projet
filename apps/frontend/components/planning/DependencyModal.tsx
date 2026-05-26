"use client";

import React, { useState } from "react";
import { Button } from "@/components/ui/button";
import { Task } from "@/types";

interface DependencyModalProps {
  isOpen: boolean;
  onClose: () => void;
  tasks: Task[] | undefined;
  onSubmit: (data: {
    taskId: string;
    predecessorId: string;
    depType: "FS" | "SS" | "FF" | "SF";
    lagDays: number;
  }) => Promise<void>;
  isPending: boolean;
}

export function DependencyModal({
  isOpen,
  onClose,
  tasks,
  onSubmit,
  isPending,
}: DependencyModalProps) {
  const [depTaskId, setDepTaskId] = useState("");
  const [depPredecessorId, setDepPredecessorId] = useState("");
  const [depType, setDepType] = useState<"FS" | "SS" | "FF" | "SF">("FS");
  const [depLag, setDepLag] = useState("0");

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!depTaskId || !depPredecessorId) {
      alert("Please select both successor and predecessor tasks.");
      return;
    }
    await onSubmit({
      taskId: depTaskId,
      predecessorId: depPredecessorId,
      depType,
      lagDays: parseInt(depLag) || 0,
    });
    setDepTaskId("");
    setDepPredecessorId("");
    setDepLag("0");
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/85 backdrop-blur-sm p-4 animate-in fade-in duration-200">
      <div className="w-full max-w-md bg-slate-900 border border-slate-800 rounded-xl p-6 space-y-6 shadow-2xl scale-in-95 duration-200">
        <div>
          <h3 className="text-lg font-semibold text-slate-200">Link Predecessor Task</h3>
          <p className="text-xs text-slate-400">Establish a scheduling dependency link.</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-1.5">
            <label className="text-xs font-semibold text-slate-400">Successor Task</label>
            <select
              value={depTaskId}
              onChange={(e) => setDepTaskId(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-lg py-2 px-3 text-sm text-slate-200 focus:outline-none focus:ring-1 focus:ring-blue-500/50"
            >
              <option value="">Select Task...</option>
              {tasks?.map((t) => (
                <option key={t.id} value={t.id}>
                  {t.wbs} — {t.name}
                </option>
              ))}
            </select>
          </div>

          <div className="space-y-1.5">
            <label className="text-xs font-semibold text-slate-400">Predecessor Task</label>
            <select
              value={depPredecessorId}
              onChange={(e) => setDepPredecessorId(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-lg py-2 px-3 text-sm text-slate-200 focus:outline-none focus:ring-1 focus:ring-blue-500/50"
            >
              <option value="">Select Predecessor...</option>
              {tasks
                ?.filter((t) => t.id !== depTaskId)
                .map((t) => (
                  <option key={t.id} value={t.id}>
                    {t.wbs} — {t.name}
                  </option>
                ))}
            </select>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-slate-400">Link Type</label>
              <select
                value={depType}
                onChange={(e) => setDepType(e.target.value as any)}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg py-2 px-3 text-sm text-slate-200 focus:outline-none focus:ring-1 focus:ring-blue-500/50"
              >
                <option value="FS">Finish-to-Start (FS)</option>
                <option value="SS">Start-to-Start (SS)</option>
                <option value="FF">Finish-to-Finish (FF)</option>
                <option value="SF">Start-to-Finish (SF)</option>
              </select>
            </div>
            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-slate-400">Lag (Days)</label>
              <input
                type="number"
                min="0"
                required
                value={depLag}
                onChange={(e) => setDepLag(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg py-2 px-3 text-sm text-slate-200 focus:outline-none focus:ring-1 focus:ring-blue-500/50"
              />
            </div>
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
              {isPending ? "Linking..." : "Link Tasks"}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}
