"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useAuth } from "@clerk/nextjs";
import { apiRequest } from "@/lib/api";
import { Resource } from "@/types";

export interface ResourceCreateInput {
  workspaceId: string;
  name: string;
  role: string;
  hourlyRateDh: number;
}

export function useResources(workspaceId: string | null) {
  const { getToken } = useAuth();
  return useQuery<Resource[]>({
    queryKey: ["resources", workspaceId],
    queryFn: async () => {
      const token = await getToken();
      const data = await apiRequest<any[]>(`/resources/workspace/${workspaceId}`, {}, token ?? undefined);
      return data.map((r) => ({
        id: r.id,
        workspaceId: workspaceId!,
        name: r.name,
        type: "HUMAN",
        costRate: r.hourly_rate_dh || 0,
        costUnit: "HOUR",
        capacityPercent: 100,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        role: r.role,
      }));
    },
    enabled: !!workspaceId,
  });
}

export function useCreateResource() {
  const { getToken } = useAuth();
  const queryClient = useQueryClient();
  return useMutation<Resource, Error, ResourceCreateInput>({
    mutationFn: async (data) => {
      const token = await getToken();
      const payload = {
        workspace_id: data.workspaceId,
        name: data.name,
        role: data.role,
        hourly_rate_dh: data.hourlyRateDh,
      };
      const r = await apiRequest<any>(
        "/resources/",
        {
          method: "POST",
          body: JSON.stringify(payload),
        },
        token ?? undefined
      );
      return {
        id: r.id,
        workspaceId: r.workspace_id,
        name: r.name,
        type: "HUMAN",
        costRate: r.hourly_rate_dh || 0,
        costUnit: "HOUR",
        capacityPercent: 100,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        role: r.role,
      };
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ["resources", variables.workspaceId] });
    },
  });
}
