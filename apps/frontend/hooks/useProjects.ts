"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useAuth } from "@clerk/nextjs";
import { apiRequest } from "@/lib/api";
import { Project } from "@/types";

export interface ProjectCreateInput {
  workspaceId: string;
  name: string;
  description?: string;
  startDate: string;
  endDate: string;
  budgetTotal: number;
}

export function useProjects(workspaceId: string | null) {
  const { getToken } = useAuth();
  return useQuery<Project[]>({
    queryKey: ["projects", workspaceId],
    queryFn: async () => {
      const token = await getToken();
      const data = await apiRequest<any[]>(
        `/projects/workspace/${workspaceId}`,
        {},
        token ?? undefined
      );
      return data.map((p) => ({
        id: p.id,
        workspaceId: workspaceId!,
        name: p.name,
        description: p.description,
        startDate: p.start_date,
        endDate: p.end_date,
        status: p.status.toUpperCase() as any,
        budget: p.budget_total || 0,
        currency: "DH",
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      }));
    },
    enabled: !!workspaceId,
  });
}

export function useProject(projectId: string | null) {
  const { getToken } = useAuth();
  return useQuery<Project>({
    queryKey: ["project", projectId],
    queryFn: async () => {
      const token = await getToken();
      const p = await apiRequest<any>(`/projects/${projectId}`, {}, token ?? undefined);
      return {
        id: p.id,
        workspaceId: p.workspace_id,
        name: p.name,
        description: p.description,
        startDate: p.start_date,
        endDate: p.end_date,
        status: p.status.toUpperCase() as any,
        budget: p.budget_total || 0,
        currency: "DH",
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      };
    },
    enabled: !!projectId,
  });
}

export function useCreateProject() {
  const { getToken } = useAuth();
  const queryClient = useQueryClient();
  return useMutation<Project, Error, ProjectCreateInput>({
    mutationFn: async (data) => {
      const token = await getToken();
      const payload = {
        workspace_id: data.workspaceId,
        name: data.name,
        description: data.description,
        start_date: data.startDate,
        end_date: data.endDate,
        budget_total: data.budgetTotal,
      };
      const p = await apiRequest<any>(
        "/projects",
        {
          method: "POST",
          body: JSON.stringify(payload),
        },
        token ?? undefined
      );
      return {
        id: p.id,
        workspaceId: p.workspace_id,
        name: p.name,
        description: p.description,
        startDate: p.start_date,
        endDate: p.end_date,
        status: p.status.toUpperCase() as any,
        budget: p.budget_total || 0,
        currency: "DH",
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      };
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ["projects", variables.workspaceId] });
    },
  });
}

export function useDeleteProject() {
  const { getToken } = useAuth();
  const queryClient = useQueryClient();
  return useMutation<void, Error, { projectId: string; workspaceId: string }>({
    mutationFn: async ({ projectId }) => {
      const token = await getToken();
      await apiRequest<void>(
        `/projects/${projectId}`,
        { method: "DELETE" },
        token ?? undefined
      );
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ["projects", variables.workspaceId] });
    },
  });
}
