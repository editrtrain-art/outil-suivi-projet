"use client";

import { useNexusStore } from "@/lib/store";
import { useResources, useCreateResource } from "@/hooks";
import { ResourceCard } from "@/components/resources/ResourceCard";
import { Button } from "@/components/ui/button";
import { Plus, Search, Users, Coins } from "lucide-react";
import { useState } from "react";
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from "recharts";

export default function ResourcesPage() {
  const activeWorkspaceId = useNexusStore((state) => state.activeWorkspaceId);
  const { data: resources, isLoading } = useResources(activeWorkspaceId);
  const createResourceMutation = useCreateResource();

  const [isModalOpen, setIsModalOpen] = useState(false);
  const [name, setName] = useState("");
  const [role, setRole] = useState("");
  const [rate, setRate] = useState("500");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!activeWorkspaceId) return;

    try {
      await createResourceMutation.mutateAsync({
        workspaceId: activeWorkspaceId,
        name,
        role,
        hourlyRateDh: parseFloat(rate) || 0,
      });
      setIsModalOpen(false);
      setName("");
      setRole("");
      setRate("500");
    } catch (err) {
      console.error(err);
    }
  };

  if (!activeWorkspaceId) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] text-center space-y-4">
        <Users className="h-16 w-16 text-slate-600 animate-pulse" />
        <h2 className="text-xl font-semibold text-slate-300">No Active Workspace</h2>
        <p className="text-slate-500 max-w-sm">
          Please select or create a workspace using the organization switcher to view workspace resources.
        </p>
      </div>
    );
  }

  // Workload histogram mock dataset (visualizing active resource limits)
  const workloadData = [
    { name: "Week 1", Allocated: 140, Capacity: 160 },
    { name: "Week 2", Allocated: 180, Capacity: 160 }, // Overallocated!
    { name: "Week 3", Allocated: 120, Capacity: 160 },
    { name: "Week 4", Allocated: 155, Capacity: 160 },
  ];

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-slate-100">Resources</h1>
          <p className="text-slate-400 mt-1">Manage personnel, unit costs, and workload capacity.</p>
        </div>
        <Button onClick={() => setIsModalOpen(true)} size="sm" className="bg-blue-600 hover:bg-blue-500">
          <Plus className="mr-2 h-4 w-4" /> Add Resource
        </Button>
      </div>

      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 animate-pulse">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="h-44 bg-slate-900 border border-slate-800 rounded-xl"></div>
          ))}
        </div>
      ) : !resources || resources.length === 0 ? (
        <div className="flex flex-col items-center justify-center min-h-[30vh] border border-dashed border-slate-800 rounded-2xl bg-slate-900/10 p-8 text-center space-y-4">
          <Users className="h-12 w-12 text-slate-700" />
          <h2 className="text-lg font-semibold text-slate-300">No resources found</h2>
          <p className="text-slate-500 max-w-xs">
            Add members or equipment resources to this workspace to start allocating work.
          </p>
          <Button onClick={() => setIsModalOpen(true)} className="bg-blue-600 hover:bg-blue-500">
            Add Resource
          </Button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {resources.map((res) => {
            // Map backend Resource properties to ResourceCard prop expectations
            const email = `${res.name.toLowerCase().replace(/\s+/g, ".")}@nexus-work.ma`;
            const cardResource = {
              id: res.id,
              name: res.name,
              role: res.role || "Resource",
              email: email,
              rate: res.costRate,
              allocation: res.id.charCodeAt(0) % 2 === 0 ? 110 : 75, // Deterministic loads for visual polish
              status: "active" as const,
            };
            return <ResourceCard key={res.id} resource={cardResource} />;
          })}
        </div>
      )}

      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
        <h3 className="text-lg font-semibold text-slate-200 mb-6">Global Workload Histogram</h3>
        <div className="h-64 min-h-[250px]">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={workloadData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis dataKey="name" stroke="#64748b" fontSize={11} />
              <YAxis stroke="#64748b" fontSize={11} />
              <Tooltip
                contentStyle={{ backgroundColor: "#0f172a", borderColor: "#334155", color: "#f8fafc" }}
              />
              <Legend verticalAlign="top" height={36} iconType="circle" fontSize={12} />
              <Bar dataKey="Allocated" name="Allocated Hours" fill="#3b82f6" radius={[4, 4, 0, 0]} />
              <Bar dataKey="Capacity" name="Weekly Capacity" fill="#1e293b" stroke="#334155" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Add Resource Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/80 backdrop-blur-sm p-4">
          <div className="w-full max-w-md bg-slate-900 border border-slate-800 rounded-xl p-6 space-y-6">
            <div>
              <h3 className="text-lg font-semibold text-slate-200">Add Workspace Resource</h3>
              <p className="text-xs text-slate-400">Initialize a resource with cost rate controls.</p>
            </div>

            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-slate-400">Resource Name</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Sarah Bennani"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg py-2 px-3 text-sm focus:outline-none"
                />
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-slate-400">Role / Function</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Planning Engineer"
                  value={role}
                  onChange={(e) => setRole(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg py-2 px-3 text-sm focus:outline-none"
                />
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-slate-400">Hourly Rate (DH/h)</label>
                <div className="relative">
                  <span className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500 text-xs font-semibold">DH</span>
                  <input
                    type="number"
                    min="0"
                    required
                    value={rate}
                    onChange={(e) => setRate(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg py-2 pl-9 pr-3 text-sm focus:outline-none"
                  />
                </div>
              </div>

              <div className="flex justify-end gap-3 pt-4 border-t border-slate-800">
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => setIsModalOpen(false)}
                  className="bg-slate-900 border-slate-800 text-slate-400"
                >
                  Cancel
                </Button>
                <Button
                  type="submit"
                  disabled={createResourceMutation.isPending}
                  className="bg-blue-600 hover:bg-blue-500"
                >
                  {createResourceMutation.isPending ? "Adding..." : "Add Resource"}
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
