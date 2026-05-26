"use client";

import React, { useState } from "react";
import { Button } from "@/components/ui/button";

interface PhaseModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: { name: string; weightPercent: number }) => Promise<void>;
  isPending: boolean;
}

export function PhaseModal({
  isOpen,
  onClose,
  onSubmit,
  isPending,
}: PhaseModalProps) {
  const [phaseName, setPhaseName] = useState("");
  const [phaseWeight, setPhaseWeight] = useState("0");

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await onSubmit({
      name: phaseName,
      weightPercent: parseFloat(phaseWeight) || 0.0,
    });
    setPhaseName("");
    setPhaseWeight("0");
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/85 backdrop-blur-sm p-4 animate-in fade-in duration-200">
      <div className="w-full max-w-md bg-slate-900 border border-slate-800 rounded-xl p-6 space-y-6 shadow-2xl scale-in-95 duration-200">
        <div>
          <h3 className="text-lg font-semibold text-slate-200">Add Phase</h3>
          <p className="text-xs text-slate-400">Initialize a new WBS level 1 phase container.</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-1.5">
            <label className="text-xs font-semibold text-slate-400">Phase Name</label>
            <input
              type="text"
              required
              placeholder="e.g. Detailed Design Stage"
              value={phaseName}
              onChange={(e) => setPhaseName(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-lg py-2 px-3 text-sm text-slate-200 focus:outline-none focus:ring-1 focus:ring-blue-500/50"
            />
          </div>

          <div className="space-y-1.5">
            <label className="text-xs font-semibold text-slate-400">Weight Percent (%)</label>
            <input
              type="number"
              step="0.1"
              min="0"
              max="100"
              required
              value={phaseWeight}
              onChange={(e) => setPhaseWeight(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-lg py-2 px-3 text-sm text-slate-200 focus:outline-none focus:ring-1 focus:ring-blue-500/50"
            />
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
              {isPending ? "Adding..." : "Add Phase"}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}
