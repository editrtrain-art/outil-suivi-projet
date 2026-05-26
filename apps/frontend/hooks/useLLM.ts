"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useAuth } from "@clerk/nextjs";
import { apiRequest } from "@/lib/api";

export interface ProjectAuditResponse {
  id: string;
  project_id: string;
  insight_text: string;
  generated_at: string;
  triggered_by?: string;
}

export function useProjectAudit(projectId: string | null, forceRefresh = false) {
  const { getToken } = useAuth();
  return useQuery<ProjectAuditResponse>({
    queryKey: ["project-audit", projectId, forceRefresh],
    queryFn: async () => {
      const token = await getToken();
      const query = forceRefresh ? "?force_refresh=true" : "";
      return apiRequest<ProjectAuditResponse>(`/llm/project/${projectId}/audit${query}`, {}, token ?? undefined);
    },
    enabled: !!projectId,
  });
}

export function useTriggerProjectAudit() {
  const { getToken } = useAuth();
  const queryClient = useQueryClient();
  return useMutation<ProjectAuditResponse, Error, string>({
    mutationFn: async (projectId) => {
      const token = await getToken();
      return apiRequest<ProjectAuditResponse>(
        `/llm/project/${projectId}/audit?force_refresh=true`,
        {},
        token ?? undefined
      );
    },
    onSuccess: (data, projectId) => {
      queryClient.invalidateQueries({ queryKey: ["project-audit", projectId] });
    },
  });
}
