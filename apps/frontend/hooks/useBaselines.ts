"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useAuth } from "@clerk/nextjs";
import { apiRequest } from "@/lib/api";

export interface BaselineBackendResponse {
  id: string;
  project_id: string;
  version_code: string;
  description?: string;
  snapshot: any;
  locked_by?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface VarianceItem {
  task_id: string;
  wbs_code: string;
  name: string;
  is_new: boolean;
  start_variance_days: number;
  finish_variance_days: number;
  duration_variance_days: number;
  slip_status: "new" | "on_track" | "delayed" | "ahead";
}

export interface BaselineCompareResponse {
  baseline_id: string;
  version_code: string;
  created_at: string;
  variances: VarianceItem[];
}

export function useBaselines(projectId: string | null) {
  const { getToken } = useAuth();
  return useQuery<BaselineBackendResponse[]>({
    queryKey: ["baselines", projectId],
    queryFn: async () => {
      const token = await getToken();
      return apiRequest<BaselineBackendResponse[]>(`/baselines/project/${projectId}`, {}, token ?? undefined);
    },
    enabled: !!projectId,
  });
}

export function useCreateBaseline() {
  const { getToken } = useAuth();
  const queryClient = useQueryClient();
  return useMutation<
    BaselineBackendResponse,
    Error,
    { projectId: string; versionCode: string; description?: string; isActive?: boolean }
  >({
    mutationFn: async (data) => {
      const token = await getToken();
      const payload = {
        project_id: data.projectId,
        version_code: data.versionCode,
        description: data.description || "",
        is_active: data.isActive ?? false,
      };
      return apiRequest<BaselineBackendResponse>(
        "/baselines/",
        {
          method: "POST",
          body: JSON.stringify(payload),
        },
        token ?? undefined
      );
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ["baselines", variables.projectId] });
    },
  });
}

export function useCompareBaseline(baselineId: string | null) {
  const { getToken } = useAuth();
  return useQuery<BaselineCompareResponse>({
    queryKey: ["baseline-comparison", baselineId],
    queryFn: async () => {
      const token = await getToken();
      return apiRequest<BaselineCompareResponse>(`/baselines/${baselineId}/compare`, {}, token ?? undefined);
    },
    enabled: !!baselineId,
  });
}
