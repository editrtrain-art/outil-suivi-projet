"use client";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "";

export async function downloadProjectPdf(projectId: string, token?: string): Promise<Blob> {
  const url = `${API_BASE_URL}/api/v1/exports/project/${projectId}/pdf`;
  const response = await fetch(url, {
    headers: token ? { Authorization: `Bearer ${token}` } : {},
  });
  if (!response.ok) throw new Error("Failed to download PDF report");
  return response.blob();
}

export async function downloadProjectExcel(projectId: string, token?: string): Promise<Blob> {
  const url = `${API_BASE_URL}/api/v1/exports/project/${projectId}/excel`;
  const response = await fetch(url, {
    headers: token ? { Authorization: `Bearer ${token}` } : {},
  });
  if (!response.ok) throw new Error("Failed to download Excel schedule");
  return response.blob();
}
