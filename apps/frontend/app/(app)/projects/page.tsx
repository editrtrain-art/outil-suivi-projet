"use client";

import { useNexusStore } from "@/lib/store";
import { useProjects, useCreateProject } from "@/hooks";
import { Button } from "@/components/ui/button";
import { Plus, Calendar, Coins, FolderOpen, Target, CheckCircle } from "lucide-react";
import { useState } from "react";
import { format } from "date-fns";

export default function ProjectsPage() {
  const activeWorkspaceId = useNexusStore((state) => state.activeWorkspaceId);
  const activeProjectId = useNexusStore((state) => state.activeProjectId);
  const setActiveProjectId = useNexusStore((state) => state.setActiveProjectId);

  const { data: projects, isLoading } = useProjects(activeWorkspaceId);
  const createProjectMutation = useCreateProject();

  const [isModalOpen, setIsModalOpen] = useState(false);
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [budget, setBudget] = useState("0");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!activeWorkspaceId) return;

    // Past date check
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    const selectedDate = new Date(startDate);
    if (selectedDate < today) {
      const confirmPast = window.confirm("La date de début du projet est dans le passé. Voulez-vous valider cette date ?");
      if (!confirmPast) return;
    }

    try {
      await createProjectMutation.mutateAsync({
        workspaceId: activeWorkspaceId,
        name,
        description,
        startDate,
        endDate,
        budgetTotal: 0, // Budget is removed, default to 0
      });
      setIsModalOpen(false);
      setName("");
      setDescription("");
      setStartDate("");
      setEndDate("");
      setBudget("0");
    } catch (err) {
      console.error("Failed to create project:", err);
    }
  };

  if (!activeWorkspaceId) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] text-center space-y-4">
        <FolderOpen className="h-16 w-16 text-slate-600 animate-pulse" />
        <h2 className="text-xl font-semibold text-slate-300">No Active Workspace</h2>
        <p className="text-slate-500 max-w-sm">
          Please select or create a workspace using the organization switcher at the top to manage projects.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-slate-100">Projects</h1>
          <p className="text-slate-400 mt-1">Manage project portfolios, status baselines, and select the active project.</p>
        </div>
        <Button onClick={() => setIsModalOpen(true)} className="bg-blue-600 hover:bg-blue-500">
          <Plus className="mr-2 h-4 w-4" /> New Project
        </Button>
      </div>

      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 animate-pulse">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-44 bg-slate-900 border border-slate-800 rounded-xl"></div>
          ))}
        </div>
      ) : !projects || projects.length === 0 ? (
        <div className="flex flex-col items-center justify-center min-h-[40vh] border border-dashed border-slate-800 rounded-2xl bg-slate-900/10 p-8 text-center space-y-4">
          <FolderOpen className="h-12 w-12 text-slate-700" />
          <h2 className="text-lg font-semibold text-slate-300">No projects found</h2>
          <p className="text-slate-500 max-w-xs">
            Get started by creating your first project in this workspace.
          </p>
          <Button onClick={() => setIsModalOpen(true)} className="bg-blue-600 hover:bg-blue-500">
            Create Project
          </Button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {projects.map((project) => {
            const isActive = activeProjectId === project.id;
            return (
              <div
                key={project.id}
                onClick={() => setActiveProjectId(project.id)}
                className={`relative flex flex-col justify-between p-6 bg-slate-900/50 backdrop-blur-sm border rounded-xl cursor-pointer hover:bg-slate-800/30 transition-all duration-300 group ${
                  isActive
                    ? "border-blue-500 ring-1 ring-blue-500/30 shadow-lg shadow-blue-500/5 bg-slate-900/80"
                    : "border-slate-800"
                }`}
              >
                {isActive && (
                  <span className="absolute top-4 right-4 flex items-center gap-1 text-[11px] font-bold text-blue-400 bg-blue-500/10 border border-blue-500/20 px-2 py-0.5 rounded-full">
                    <CheckCircle className="h-3.5 w-3.5 fill-blue-500/10 text-blue-400" /> Active Context
                  </span>
                )}

                <div className="space-y-4">
                  <div>
                    <h3 className="text-lg font-semibold text-slate-200 group-hover:text-blue-400 transition-colors">
                      {project.name}
                    </h3>
                    <p className="text-xs text-slate-500 mt-1 line-clamp-2">
                      {project.description || "No description provided."}
                    </p>
                  </div>

                  <div className="grid grid-cols-1 gap-4 text-xs text-slate-400">
                    <div className="flex items-center gap-1.5">
                      <Calendar className="h-4 w-4 text-slate-500" />
                      <span>
                        {format(new Date(project.startDate), "MMM dd, yyyy")}
                      </span>
                    </div>
                  </div>
                </div>

                <div className="mt-6 pt-4 border-t border-slate-800/50 flex items-center justify-between">
                  <span
                    className={`text-[10px] font-bold uppercase tracking-wider px-2.5 py-1 rounded-md ${
                      project.status === "ACTIVE"
                        ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
                        : "bg-amber-500/10 text-amber-400 border border-amber-500/20"
                    }`}
                  >
                    {project.status}
                  </span>
                  <span className="text-xs text-blue-400 group-hover:translate-x-1 transition-transform">
                    {isActive ? "Viewing" : "Click to select"} →
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Modal Dialog */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/80 backdrop-blur-sm p-4">
          <div className="w-full max-w-md bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-2xl p-6 space-y-6">
            <div>
              <h3 className="text-lg font-semibold text-slate-200">Create New Project</h3>
              <p className="text-xs text-slate-400">Initialize a project scheduling container.</p>
            </div>

            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-slate-400">Project Name</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Concrete Building Construction"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg py-2 px-3 text-sm focus:outline-none focus:ring-1 focus:ring-blue-500/50"
                />
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-slate-400">Description</label>
                <textarea
                  placeholder="Project scope and details..."
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg py-2 px-3 text-sm h-20 focus:outline-none focus:ring-1 focus:ring-blue-500/50 resize-none"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-1.5">
                  <label className="text-xs font-semibold text-slate-400">Start Date</label>
                  <input
                    type="date"
                    required
                    value={startDate}
                    onChange={(e) => setStartDate(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg py-2 px-3 text-sm focus:outline-none focus:ring-1 focus:ring-blue-500/50"
                  />
                </div>
                <div className="space-y-1.5">
                  <label className="text-xs font-semibold text-slate-400">End Date</label>
                  <input
                    type="date"
                    required
                    value={endDate}
                    onChange={(e) => setEndDate(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg py-2 px-3 text-sm focus:outline-none focus:ring-1 focus:ring-blue-500/50"
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
                  disabled={createProjectMutation.isPending}
                  className="bg-blue-600 hover:bg-blue-500"
                >
                  {createProjectMutation.isPending ? "Creating..." : "Create Project"}
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
