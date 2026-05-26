"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useAuth } from "@clerk/nextjs";
import { apiRequest } from "@/lib/api";
import { Workspace } from "@/types";

export function useWorkspaces() {
  const { getToken } = useAuth();
  return useQuery<Workspace[]>({
    queryKey: ["workspaces"],
    queryFn: async () => {
      const token = await getToken();
      return apiRequest<Workspace[]>("/workspaces", {}, token ?? undefined);
    },
  });
}

export function useCreateWorkspace() {
  const { getToken } = useAuth();
  const queryClient = useQueryClient();
  return useMutation<Workspace, Error, { name: string; slug: string }>({
    mutationFn: async (data) => {
      const token = await getToken();
      return apiRequest<Workspace>(
        "/workspaces",
        {
          method: "POST",
          body: JSON.stringify(data),
        },
        token ?? undefined
      );
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["workspaces"] });
    },
  });
}
