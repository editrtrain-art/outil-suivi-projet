"use client";

import { useNexusStore } from "@/lib/store";
import {
  usePhases,
  useTasks,
  useCreateTask,
  useCreatePhase,
  useRunCpm,
  useAddDependency,
  useBaselines,
  useCreateBaseline,
  useLevelResources,
  useSmoothResources,
} from "@/hooks";
import { TaskRow } from "@/components/planning/WBSTree";
import { Button } from "@/components/ui/button";
import { Plus, Play, Calendar, Link2 } from "lucide-react";
import { useState } from "react";
import { format, differenceInDays } from "date-fns";

// Standalone extracted components
import { GanttChart } from "@/components/planning/GanttChart";
import { TaskModal } from "@/components/planning/TaskModal";
import { PhaseModal } from "@/components/planning/PhaseModal";
import { DependencyModal } from "@/components/planning/DependencyModal";
import { BaselineModal } from "@/components/planning/BaselineModal";

export default function PlanningPage() {
  const activeProjectId = useNexusStore((state) => state.activeProjectId);

  // Queries & Mutations
  const { data: phases, isLoading: isPhasesLoading } = usePhases(activeProjectId);
  const { data: tasks, isLoading: isTasksLoading } = useTasks(activeProjectId);
  const { data: baselines } = useBaselines(activeProjectId);

  const createTaskMutation = useCreateTask();
  const createPhaseMutation = useCreatePhase();
  const runCpmMutation = useRunCpm();
  const addDependencyMutation = useAddDependency();

  const createBaselineMutation = useCreateBaseline();
  const levelResourcesMutation = useLevelResources();
  const smoothResourcesMutation = useSmoothResources();

  // Modal display states
  const [isTaskModalOpen, setIsTaskModalOpen] = useState(false);
  const [isPhaseModalOpen, setIsPhaseModalOpen] = useState(false);
  const [isDepModalOpen, setIsDepModalOpen] = useState(false);
  const [isBaselineModalOpen, setIsBaselineModalOpen] = useState(false);

  // Selected baseline for comparison comparison
  const [selectedBaselineId, setSelectedBaselineId] = useState<string>("");

  if (!activeProjectId) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] text-center space-y-4">
        <Calendar className="h-16 w-16 text-slate-600 animate-pulse" />
        <h2 className="text-xl font-semibold text-slate-300">No Project Selected</h2>
        <p className="text-slate-500 max-w-sm">
          Please select a project context from the Projects list to view and manage its WBS scheduling.
        </p>
      </div>
    );
  }

  // Construct WBS tree hierarchy
  const buildIntegratedWbsTree = () => {
    if (!phases || !tasks) return [];

    const phaseNodes = phases.map((ph) => ({
      id: ph.id,
      wbs: ph.wbsCode,
      name: ph.name,
      duration: 0,
      start: ph.plannedStart ? format(new Date(ph.plannedStart), "yyyy-MM-dd") : "-",
      finish: ph.plannedFinish ? format(new Date(ph.plannedFinish), "yyyy-MM-dd") : "-",
      progress: ph.weightPercent || 0,
      isCritical: false,
      isMilestone: false,
      subtasks: [] as any[],
    }));

    const taskMap = new Map<string, any>();
    tasks.forEach((t) => {
      taskMap.set(t.id, {
        id: t.id,
        wbs: t.wbs,
        name: t.name,
        duration: t.durationDays,
        start: t.startDate ? format(new Date(t.startDate), "yyyy-MM-dd") : "-",
        finish: t.endDate ? format(new Date(t.endDate), "yyyy-MM-dd") : "-",
        progress: t.progressPercent || 0,
        isCritical: t.isCritical,
        isMilestone: t.isMilestone,
        subtasks: [],
      });
    });

    tasks.forEach((t) => {
      const mapped = taskMap.get(t.id);
      if (t.parentTaskId && taskMap.has(t.parentTaskId)) {
        taskMap.get(t.parentTaskId).subtasks.push(mapped);
      } else {
        const phaseNode = phaseNodes.find((ph) => ph.id === t.phaseId);
        if (phaseNode) {
          phaseNode.subtasks.push(mapped);
        }
      }
    });

    phaseNodes.forEach((ph) => {
      if (ph.subtasks.length > 0) {
        let minStart: Date | null = null;
        let maxEnd: Date | null = null;
        let totalDuration = 0;
        let critical = false;

        ph.subtasks.forEach((st) => {
          if (st.isCritical) critical = true;
          totalDuration += st.duration;

          if (st.start !== "-") {
            const startDate = new Date(st.start);
            if (!minStart || startDate < minStart) minStart = startDate;
          }
          if (st.finish !== "-") {
            const endDate = new Date(st.finish);
            if (!maxEnd || endDate > maxEnd) maxEnd = endDate;
          }
        });

        if (minStart) ph.start = format(minStart, "yyyy-MM-dd");
        if (maxEnd) ph.finish = format(maxEnd, "yyyy-MM-dd");
        ph.duration = totalDuration;
        ph.isCritical = critical;
      }
    });

    return phaseNodes;
  };

  const wbsTree = buildIntegratedWbsTree();

  // Gantt Chart boundaries logic
  let projectStartDate: Date | null = null;
  let projectEndDate: Date | null = null;

  if (tasks && tasks.length > 0) {
    for (const t of tasks) {
      if (t.startDate) {
        const sd = new Date(t.startDate);
        if (!projectStartDate || sd < projectStartDate) {
          projectStartDate = sd;
        }
      }
      if (t.endDate) {
        const ed = new Date(t.endDate);
        if (!projectEndDate || ed > projectEndDate) {
          projectEndDate = ed;
        }
      }
    }
  }

  const viewStart = projectStartDate
    ? new Date(projectStartDate.getTime() - 2 * 24 * 60 * 60 * 1000)
    : new Date();
  const viewEnd = projectEndDate
    ? new Date(projectEndDate.getTime() + 5 * 24 * 60 * 60 * 1000)
    : new Date(viewStart.getTime() + 30 * 24 * 60 * 60 * 1000);
  const totalViewDays = Math.max(differenceInDays(viewEnd, viewStart), 7);

  const selectedBaseline = baselines?.find((b) => b.id === selectedBaselineId);
  const baselineTasks = selectedBaseline?.snapshot?.tasks || [];
  const baselineTaskMap = new Map<string, { start: string; finish: string }>();
  baselineTasks.forEach((bt: any) => {
    if (bt.id && bt.start_date_scheduled && bt.end_date_scheduled) {
      baselineTaskMap.set(bt.id, {
        start: bt.start_date_scheduled,
        finish: bt.end_date_scheduled,
      });
    }
  });

  const handleRunCpm = async () => {
    try {
      await runCpmMutation.mutateAsync(activeProjectId);
    } catch (err) {
      console.error(err);
    }
  };

  const handleLevelResources = async () => {
    if (
      confirm(
        "Executing resource leveling may shift task dates past float thresholds to resolve capacity overloads. Continue?"
      )
    ) {
      try {
        await levelResourcesMutation.mutateAsync(activeProjectId);
      } catch (err) {
        console.error(err);
      }
    }
  };

  const handleSmoothResources = async () => {
    try {
      await smoothResourcesMutation.mutateAsync(activeProjectId);
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-slate-100">Planning & WBS</h1>
          <p className="text-slate-400 mt-1">Hierarchical task structure and critical path analysis.</p>
        </div>
        <div className="flex flex-wrap items-center gap-3">
          {/* Baseline comparison control */}
          <div className="flex items-center gap-2 bg-slate-900 border border-slate-800 rounded-lg px-3 py-1.5 shadow-md">
            <span className="text-xs font-semibold text-slate-400">Compare Baseline:</span>
            <select
              value={selectedBaselineId}
              onChange={(e) => setSelectedBaselineId(e.target.value)}
              className="bg-slate-950 border border-slate-800 text-slate-200 rounded px-2 py-0.5 text-xs focus:outline-none"
            >
              <option value="">None (Current Plan)</option>
              {baselines?.map((b) => (
                <option key={b.id} value={b.id}>
                  {b.version_code} ({format(new Date(b.created_at), "MMM dd")})
                </option>
              ))}
            </select>
            <Button
              onClick={() => setIsBaselineModalOpen(true)}
              variant="ghost"
              className="text-slate-400 hover:text-slate-200 h-6 px-2 text-[10px] font-semibold border border-slate-800 bg-slate-950 hover:bg-slate-800"
            >
              Snapshot
            </Button>
          </div>

          {/* Leveling & Smoothing */}
          <Button
            onClick={handleLevelResources}
            disabled={levelResourcesMutation.isPending}
            variant="outline"
            size="sm"
            className="bg-slate-900 border-emerald-500/20 text-emerald-400 hover:bg-emerald-500/10 text-xs"
          >
            Level Resources
          </Button>
          <Button
            onClick={handleSmoothResources}
            disabled={smoothResourcesMutation.isPending}
            variant="outline"
            size="sm"
            className="bg-slate-900 border-amber-500/20 text-amber-400 hover:bg-amber-500/10 text-xs"
          >
            Smooth
          </Button>

          {/* Schedule modifications */}
          <Button
            onClick={() => setIsDepModalOpen(true)}
            variant="outline"
            size="sm"
            className="bg-slate-900 border-slate-800 hover:bg-slate-800 text-slate-300 text-xs"
          >
            <Link2 className="mr-1.5 h-3.5 w-3.5" /> Link Tasks
          </Button>
          <Button
            onClick={() => setIsPhaseModalOpen(true)}
            variant="outline"
            size="sm"
            className="bg-slate-900 border-slate-800 hover:bg-slate-800 text-slate-300 text-xs"
          >
            <Plus className="mr-1.5 h-3.5 w-3.5" /> New Phase
          </Button>
          <Button
            onClick={handleRunCpm}
            disabled={runCpmMutation.isPending}
            variant="outline"
            size="sm"
            className="bg-slate-900 border-slate-700 hover:bg-slate-800 text-blue-400 border-blue-500/30 text-xs"
          >
            <Play className="mr-1.5 h-3.5 w-3.5" /> Run CPM
          </Button>
          <Button
            onClick={() => {
              if (phases && phases.length > 0) {
                setIsTaskModalOpen(true);
              } else {
                alert("Please create a project Phase first before adding tasks.");
              }
            }}
            size="sm"
            className="bg-blue-600 hover:bg-blue-500 text-xs"
          >
            <Plus className="mr-1.5 h-3.5 w-3.5" /> New Task
          </Button>
        </div>
      </div>

      {isPhasesLoading || isTasksLoading ? (
        <div className="h-64 bg-slate-900 border border-slate-800 rounded-xl animate-pulse flex items-center justify-center">
          <p className="text-slate-500">Loading WBS hierarchy...</p>
        </div>
      ) : (
        <>
          {/* Table display */}
          <div className="bg-slate-950 border border-slate-800 rounded-xl overflow-hidden shadow-2xl">
            <div className="flex bg-slate-900/80 border-b border-slate-800 py-3 text-[11px] font-bold uppercase tracking-widest text-slate-500">
              <div className="px-4 min-w-[300px]">Task Name / WBS</div>
              <div className="flex-1 flex items-center gap-8 px-4">
                <div className="w-20 text-center">Duration</div>
                <div className="w-28 text-center">Start Date</div>
                <div className="w-28 text-center">Finish Date</div>
                <div className="w-24">Progress</div>
                <div className="w-16 text-right">%</div>
              </div>
            </div>

            <div className="max-h-[600px] overflow-y-auto custom-scrollbar bg-slate-900/20">
              {wbsTree.map((node) => (
                <TaskRow key={node.id} task={node} level={0} />
              ))}
            </div>
          </div>

          {/* Standalone Gantt Chart Timeline */}
          <GanttChart
            tasks={tasks}
            viewStart={viewStart}
            viewEnd={viewEnd}
            totalViewDays={totalViewDays}
            baselineTaskMap={baselineTaskMap}
          />
        </>
      )}

      {/* Standalone Modals */}
      <TaskModal
        isOpen={isTaskModalOpen}
        onClose={() => setIsTaskModalOpen(false)}
        phases={phases}
        tasks={tasks}
        isPending={createTaskMutation.isPending}
        onSubmit={async (data) => {
          await createTaskMutation.mutateAsync({
            projectId: activeProjectId,
            task: data,
          });
          setIsTaskModalOpen(false);
        }}
      />

      <PhaseModal
        isOpen={isPhaseModalOpen}
        onClose={() => setIsPhaseModalOpen(false)}
        isPending={createPhaseMutation.isPending}
        onSubmit={async (data) => {
          await createPhaseMutation.mutateAsync({
            projectId: activeProjectId,
            name: data.name,
            weightPercent: data.weightPercent,
          });
          setIsPhaseModalOpen(false);
        }}
      />

      <DependencyModal
        isOpen={isDepModalOpen}
        onClose={() => setIsDepModalOpen(false)}
        tasks={tasks}
        isPending={addDependencyMutation.isPending}
        onSubmit={async (data) => {
          await addDependencyMutation.mutateAsync({
            taskId: data.taskId,
            projectId: activeProjectId,
            dependency: {
              predecessorId: data.predecessorId,
              depType: data.depType,
              lagDays: data.lagDays,
            },
          });
          setIsDepModalOpen(false);
        }}
      />

      <BaselineModal
        isOpen={isBaselineModalOpen}
        onClose={() => setIsBaselineModalOpen(false)}
        isPending={createBaselineMutation.isPending}
        defaultVersionCode={"B" + ((baselines?.length || 0) + 1)}
        onSubmit={async (data) => {
          await createBaselineMutation.mutateAsync({
            projectId: activeProjectId,
            versionCode: data.versionCode,
            description: data.description,
            isActive: true,
          });
          setIsBaselineModalOpen(false);
        }}
      />
    </div>
  );
}
