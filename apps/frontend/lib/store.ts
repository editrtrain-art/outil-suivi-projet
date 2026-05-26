import { create } from "zustand";
import { persist } from "zustand/middleware";

interface NexusState {
  activeWorkspaceId: string | null;
  activeProjectId: string | null;
  setActiveWorkspaceId: (id: string | null) => void;
  setActiveProjectId: (id: string | null) => void;
}

/**
 * Global Zustand store for managing active context (workspace and project).
 * Persists the selections to localStorage so page refreshes maintain context.
 */
export const useNexusStore = create<NexusState>()(
  persist(
    (set) => ({
      activeWorkspaceId: null,
      activeProjectId: null,
      setActiveWorkspaceId: (id) => set({ activeWorkspaceId: id, activeProjectId: null }), // Clear project when switching workspace
      setActiveProjectId: (id) => set({ activeProjectId: id }),
    }),
    {
      name: "nexus-context-storage",
    }
  )
);
