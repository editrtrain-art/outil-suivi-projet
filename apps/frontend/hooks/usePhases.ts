"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useAuth } from "@clerk/nextjs";
import { apiRequest } from "@/lib/api";

export interface PhaseCreateInput {
  projectId: string;
  name: string;
  weightPercent?: number;
}

export interface PhaseUpdateInput {
  name?: string;
  weightPercent?: number;
  plannedStart?: string;
  plannedFinish?: string;
}

export interface Phase {
  id: string;
  projectId: string;
  name: string;
  wbsCode: string;
  orderIndex: number;
  weightPercent: number;
  plannedStart?: string;
  plannedFinish?: string;
}

export function usePhases(projectId: string | null) {
  const { getToken } = useAuth();
  return useQuery<Phase[]>({
    queryKey: ["phases", projectId],
    queryFn: async () => {
      const token = await getToken();
      const data = await apiRequest<any[]>(`/phases/project/${projectId}`, {}, token ?? undefined);
      return data.map((ph) => ({
        id: ph.id,
        projectId: ph.project_id,
        name: ph.name,
        wbsCode: ph.wbs_code,
        orderIndex: ph.order_index,
        weightPercent: ph.weight_percent,
        plannedStart: ph.planned_start,
        plannedFinish: ph.planned_finish,
      }));
    },
    enabled: !!projectId,
  });
}

export function useCreatePhase() {
  const { getToken } = useAuth();
  const queryClient = useQueryClient();
  return useMutation<Phase, Error, PhaseCreateInput>({
    mutationFn: async (data) => {
      const token = await getToken();
      const payload = {
        project_id: data.projectId,
        name: data.name,
        weight_percent: data.weightPercent || 0.0,
      };
      const ph = await apiRequest<any>(
        "/phases/",
        {
          method: "POST",
          body: JSON.stringify(payload),
        },
        token ?? undefined
      );
      return {
        id: ph.id,
        projectId: ph.project_id,
        name: ph.name,
        wbsCode: ph.wbs_code,
        orderIndex: ph.order_index,
        weightPercent: ph.weight_percent,
        plannedStart: ph.planned_start,
        plannedFinish: ph.planned_finish,
      };
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ["phases", variables.projectId] });
    },
  });
}

export function useUpdatePhase() {
  const { getToken } = useAuth();
  const queryClient = useQueryClient();
  return useMutation<Phase, Error, { phaseId: string; projectId: string; updates: PhaseUpdateInput }>({
    mutationFn: async ({ phaseId, updates }) => {
      const token = await getToken();
      const payload = {
        name: updates.name,
        weight_percent: updates.weightPercent,
        planned_start: updates.plannedStart,
        planned_finish: updates.plannedFinish,
      };
      const ph = await apiRequest<any>(
        `/phases/${phaseId}`,
        {
          method: "PATCH",
          body: JSON.stringify(payload),
        },
        token ?? undefined
      );
      return {
        id: ph.id,
        projectId: ph.project_id,
        name: ph.name,
        wbsCode: ph.wbs_code,
        orderIndex: ph.order_index,
        weightPercent: ph.weight_percent,
        plannedStart: ph.planned_start,
        plannedFinish: ph.planned_finish,
      };
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ["phases", variables.projectId] });
    },
  });
}

export function useDeletePhase() {
  const { getToken } = useAuth();
  const queryClient = useQueryClient();
  return useMutation<void, Error, { phaseId: string; projectId: string }>({
    mutationFn: async ({ phaseId }) => {
      const token = await getToken();
      await apiRequest<void>(
        `/phases/${phaseId}`,
        {
          method: "DELETE",
        },
        token ?? undefined
      );
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ["phases", variables.projectId] });
      queryClient.invalidateQueries({ queryKey: ["tasks", variables.projectId] });
    },
  });
}
