/**
 * NEXUS V3 Types and Interfaces
 * Central definitions for entities shared across the Next.js application.
 */

export type UserRole = "ADMIN" | "PROJECT_CONTROLLER" | "MEMBER" | "VIEWER";

export interface User {
  id: string;
  email: string;
  firstName?: string;
  lastName?: string;
  imageUrl?: string;
}

export interface Workspace {
  id: string;
  name: string;
  slug: string;
  createdAt: string;
  updatedAt: string;
}

export interface WorkspaceMember {
  id: string;
  workspaceId: string;
  user: User;
  role: UserRole;
  createdAt: string;
}

export type ProjectStatus = "DRAFT" | "PLANNING" | "ACTIVE" | "COMPLETED" | "ON_HOLD";

export interface Project {
  id: string;
  workspaceId: string;
  name: string;
  description?: string;
  startDate: string;
  endDate: string;
  status: ProjectStatus;
  budget: number;
  currency: string;
  createdAt: string;
  updatedAt: string;
}

export type TaskStatus = "TODO" | "IN_PROGRESS" | "COMPLETED" | "BLOCKED";

export interface Task {
  id: string;
  projectId: string;
  name: string;
  description?: string;
  startDate: string;
  endDate: string;
  durationDays: number;
  status: TaskStatus;
  progressPercent: number; // 0 to 100
  actualCost: number;
  plannedValue: number; // BCWS
  earnedValue: number; // BCWP
  earlyStart?: string;
  earlyFinish?: string;
  lateStart?: string;
  lateFinish?: string;
  floatDays?: number;
  isCritical?: boolean;
  createdAt: string;
  updatedAt: string;
  wbs?: string;
  phaseId?: string;
  parentTaskId?: string | null;
  isMilestone?: boolean;
}

export interface TaskDependency {
  id: string;
  projectId: string;
  predecessorId: string;
  successorId: string;
  type: "FS" | "SS" | "FF" | "SF"; // Finish-to-Start, Start-to-Start, etc.
  lagDays: number;
}

export interface Baseline {
  id: string;
  projectId: string;
  name: string;
  description?: string;
  snapshotDate: string;
  isCurrent: boolean;
  data: {
    tasks: {
      id: string;
      name: string;
      startDate: string;
      endDate: string;
      plannedValue: number;
    }[];
    project: {
      budget: number;
      startDate: string;
      endDate: string;
    };
  };
  createdAt: string;
}

export interface Resource {
  id: string;
  workspaceId: string;
  name: string;
  type: "HUMAN" | "MATERIAL" | "EQUIPMENT";
  costRate: number; // cost per hour or day
  costUnit: "HOUR" | "DAY" | "FIXED";
  capacityPercent: number; // standard capacity (e.g. 100% = 8h/day)
  createdAt: string;
  updatedAt: string;
  role?: string;
}

export interface ResourceAllocation {
  id: string;
  taskId: string;
  resourceId: string;
  allocatedPercent: number; // e.g. 50% allocation to this task
  assignedHours?: number;
}

export interface EvmMetrics {
  pv: number; // Planned Value
  ev: number; // Earned Value
  ac: number; // Actual Cost
  cv: number; // Cost Variance (EV - AC)
  sv: number; // Schedule Variance (EV - PV)
  cpi: number; // Cost Performance Index (EV / AC)
  spi: number; // Schedule Performance Index (EV / PV)
  eac: number; // Estimate at Completion
  etc: number; // Estimate to Complete
  tcpi: number; // To Complete Performance Index
}

export interface ResourceHistogramBin {
  date: string;
  allocatedValue: number;
  capacityValue: number;
  isOverallocated: boolean;
}
