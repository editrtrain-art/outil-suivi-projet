"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useAuth } from "@clerk/nextjs";
import { apiRequest } from "@/lib/api";

export interface ResourceLoadDetails {
  name: string;
  role: string;
  capacity: number;
  daily_allocations: number[];
}

export interface DailyLoadResponse {
  timeline: string[];
  resources: Record<string, ResourceLoadDetails>;
}

export function useResourceLoad(projectId: string | null) {
  const { getToken } = useAuth();
  return useQuery<DailyLoadResponse>({
    queryKey: ["resource-load", projectId],
    queryFn: async () => {
      const token = await getToken();
      return apiRequest<DailyLoadResponse>(`/leveling/project/${projectId}/load`, {}, token ?? undefined);
    },
    enabled: !!projectId,
  });
}

export function useLevelResources() {
  const { getToken } = useAuth();
  const queryClient = useQueryClient();
  return useMutation<{ status: string; message: string }, Error, string>({
    mutationFn: async (projectId) => {
      const token = await getToken();
      return apiRequest<{ status: string; message: string }>(
        `/leveling/project/${projectId}/level`,
        { method: "POST" },
        token ?? undefined
      );
    },
    onSuccess: (_, projectId) => {
      queryClient.invalidateQueries({ queryKey: ["tasks", projectId] });
      queryClient.invalidateQueries({ queryKey: ["resource-load", projectId] });
    },
  });
}

export function useSmoothResources() {
  const { getToken } = useAuth();
  const queryClient = useQueryClient();
  return useMutation<{ status: string; message: string }, Error, string>({
    mutationFn: async (projectId) => {
      const token = await getToken();
      return apiRequest<{ status: string; message: string }>(
        `/leveling/project/${projectId}/smooth`,
        { method: "POST" },
        token ?? undefined
      );
    },
    onSuccess: (_, projectId) => {
      queryClient.invalidateQueries({ queryKey: ["tasks", projectId] });
      queryClient.invalidateQueries({ queryKey: ["resource-load", projectId] });
    },
  });
}
