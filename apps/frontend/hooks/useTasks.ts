"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useAuth } from "@clerk/nextjs";
import { apiRequest } from "@/lib/api";
import { Task } from "@/types";

export interface TaskCreateInput {
  phaseId: string;
  name: string;
  description?: string;
  durationDays: number;
  parentTaskId?: string | null;
  weightPercent?: number;
  priority?: number;
  isMilestone?: boolean;
}

export interface TaskUpdateInput {
  name?: string;
  description?: string;
  durationDays?: number;
  status?: "not_started" | "in_progress" | "completed" | "blocked" | "cancelled";
  weightPercent?: number;
  priority?: number;
  startDateScheduled?: string;
  endDateScheduled?: string;
}

export interface DependencyCreateInput {
  predecessorId: string;
  depType?: "FS" | "SS" | "FF" | "SF";
  lagDays?: number;
}

export function useTasks(projectId: string | null) {
  const { getToken } = useAuth();
  return useQuery<Task[]>({
    queryKey: ["tasks", projectId],
    queryFn: async () => {
      const token = await getToken();
      const data = await apiRequest<any[]>(`/tasks/project/${projectId}`, {}, token ?? undefined);
      return data.map((t) => ({
        id: t.id,
        projectId: projectId!,
        name: t.name,
        description: t.description,
        startDate: t.start_date_scheduled || t.early_start || "",
        endDate: t.end_date_scheduled || t.early_finish || "",
        durationDays: t.duration_days,
        status: t.status.toUpperCase() as any,
        progressPercent: t.progress_percent || 0,
        actualCost: t.actual_cost || 0,
        plannedValue: t.planned_value || 0,
        earnedValue: t.earned_value || 0,
        earlyStart: t.early_start,
        earlyFinish: t.early_finish,
        lateStart: t.late_start,
        lateFinish: t.late_finish,
        floatDays: t.total_float,
        isCritical: t.is_critical,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        phaseId: t.phase_id,
        parentTaskId: t.parent_task_id,
        wbs: t.wbs_code,
      } as any));
    },
    enabled: !!projectId,
  });
}

export function useCreateTask() {
  const { getToken } = useAuth();
  const queryClient = useQueryClient();
  return useMutation<Task, Error, { projectId: string; task: TaskCreateInput }>({
    mutationFn: async ({ task }) => {
      const token = await getToken();
      const payload = {
        phase_id: task.phaseId,
        name: task.name,
        description: task.description,
        duration_days: task.durationDays,
        parent_task_id: task.parentTaskId || null,
        weight_percent: task.weightPercent || 0.0,
        priority: task.priority || 3,
        is_milestone: task.isMilestone || false,
      };
      const t = await apiRequest<any>(
        "/tasks/",
        {
          method: "POST",
          body: JSON.stringify(payload),
        },
        token ?? undefined
      );
      return {
        id: t.id,
        name: t.name,
      } as any;
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ["tasks", variables.projectId] });
    },
  });
}

export function useUpdateTask() {
  const { getToken } = useAuth();
  const queryClient = useQueryClient();
  return useMutation<Task, Error, { taskId: string; projectId: string; updates: TaskUpdateInput }>({
    mutationFn: async ({ taskId, updates }) => {
      const token = await getToken();
      const payload = {
        name: updates.name,
        description: updates.description,
        duration_days: updates.durationDays,
        status: updates.status,
        weight_percent: updates.weightPercent,
        priority: updates.priority,
        start_date_scheduled: updates.startDateScheduled,
        end_date_scheduled: updates.endDateScheduled,
      };
      const t = await apiRequest<any>(
        `/tasks/${taskId}`,
        {
          method: "PATCH",
          body: JSON.stringify(payload),
        },
        token ?? undefined
      );
      return t;
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ["tasks", variables.projectId] });
      queryClient.invalidateQueries({ queryKey: ["evm", variables.projectId] });
    },
  });
}

export function useDeleteTask() {
  const { getToken } = useAuth();
  const queryClient = useQueryClient();
  return useMutation<void, Error, { taskId: string; projectId: string }>({
    mutationFn: async ({ taskId }) => {
      const token = await getToken();
      await apiRequest<void>(
        `/tasks/${taskId}`,
        {
          method: "DELETE",
        },
        token ?? undefined
      );
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ["tasks", variables.projectId] });
      queryClient.invalidateQueries({ queryKey: ["evm", variables.projectId] });
    },
  });
}

export function useAddDependency() {
  const { getToken } = useAuth();
  const queryClient = useQueryClient();
  return useMutation<any, Error, { taskId: string; projectId: string; dependency: DependencyCreateInput }>({
    mutationFn: async ({ taskId, dependency }) => {
      const token = await getToken();
      const payload = {
        predecessor_id: dependency.predecessorId,
        dep_type: dependency.depType || "FS",
        lag_days: dependency.lagDays || 0,
      };
      return apiRequest<any>(
        `/tasks/${taskId}/dependencies`,
        {
          method: "POST",
          body: JSON.stringify(payload),
        },
        token ?? undefined
      );
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ["tasks", variables.projectId] });
    },
  });
}

export function useRunCpm() {
  const { getToken } = useAuth();
  const queryClient = useQueryClient();
  return useMutation<any, Error, string>({
    mutationFn: async (projectId) => {
      const token = await getToken();
      return apiRequest<any>(
        `/tasks/project/${projectId}/run-cpm`,
        {
          method: "POST",
        },
        token ?? undefined
      );
    },
    onSuccess: (data, projectId) => {
      queryClient.invalidateQueries({ queryKey: ["tasks", projectId] });
    },
  });
}
