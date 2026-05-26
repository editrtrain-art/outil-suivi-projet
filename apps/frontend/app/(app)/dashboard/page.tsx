"use client";

import { useNexusStore } from "@/lib/store";
import { 
  useProject, 
  useEvm, 
  useTasks,
  useProjectAudit,
  useTriggerProjectAudit,
  downloadProjectPdf,
  downloadProjectExcel
} from "@/hooks";
import { KPICard } from "@/components/ui/KPICard";
import { Button } from "@/components/ui/button";
import { AlertCircle, BarChart3, HelpCircle, TrendingDown, TrendingUp, Download, Sparkles, RefreshCw } from "lucide-react";
import { 
  ResponsiveContainer, 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend 
} from "recharts";
import { useAuth } from "@clerk/nextjs";
import { useEffect, useState } from "react";
import { apiRequest } from "@/lib/api";
import { format } from "date-fns";

export default function DashboardPage() {
  const activeProjectId = useNexusStore((state) => state.activeProjectId);
  const { data: project } = useProject(activeProjectId);
  const { data: evm, isLoading: isEvmLoading } = useEvm(activeProjectId);
  const { data: tasks } = useTasks(activeProjectId);
  const { getToken } = useAuth();

  const { data: auditReport, isLoading: isAuditLoading, refetch: refetchAudit } = useProjectAudit(activeProjectId);
  const triggerAuditMutation = useTriggerProjectAudit();

  const handleDownloadPdf = async () => {
    if (!activeProjectId) return;
    try {
      const token = await getToken();
      const blob = await downloadProjectPdf(activeProjectId, token ?? undefined);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `project_${project?.name || activeProjectId}_status.pdf`;
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error(err);
      alert("Failed to export PDF status report.");
    }
  };

  const handleDownloadExcel = async () => {
    if (!activeProjectId) return;
    try {
      const token = await getToken();
      const blob = await downloadProjectExcel(activeProjectId, token ?? undefined);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `project_${project?.name || activeProjectId}_planning.xlsx`;
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error(err);
      alert("Failed to export Excel schedule sheet.");
    }
  };

  const handleTriggerAudit = async () => {
    if (!activeProjectId) return;
    try {
      await triggerAuditMutation.mutateAsync(activeProjectId);
      refetchAudit();
    } catch (err) {
      console.error(err);
      alert("Failed to compile AI risk audit.");
    }
  };

  const [sCurveData, setSCurveData] = useState<any[]>([]);
  const [isChartLoading, setIsChartLoading] = useState(false);

  // Fetch S-Curve timeline data in parallel using milestones
  useEffect(() => {
    if (!project || !activeProjectId) return;

    const fetchSCurve = async () => {
      setIsChartLoading(true);
      const token = await getToken();

      const start = new Date(project.startDate);
      const end = new Date(project.endDate);
      const diffTime = Math.abs(end.getTime() - start.getTime());
      const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24)) || 1;

      const intervals = 5;
      const step = diffDays / (intervals - 1);

      const dates: string[] = [];
      for (let i = 0; i < intervals; i++) {
        const d = new Date(start.getTime() + i * step * 24 * 60 * 60 * 1000);
        dates.push(format(d, "yyyy-MM-dd"));
      }

      try {
        const results = await Promise.all(
          dates.map(async (d) => {
            try {
              const res = await apiRequest<any>(
                `/evm/project/${activeProjectId}?as_of_date=${d}`,
                {},
                token ?? undefined
              );
              return {
                date: format(new Date(d), "MMM dd"),
                PV: res.pv,
                EV: res.ev,
                AC: res.ac,
              };
            } catch {
              return { date: format(new Date(d), "MMM dd"), PV: 0, EV: 0, AC: 0 };
            }
          })
        );
        setSCurveData(results);
      } catch (err) {
        console.error("Failed to fetch S-Curve data:", err);
      } finally {
        setIsChartLoading(false);
      }
    };

    fetchSCurve();
  }, [project, activeProjectId, getToken]);

  if (!activeProjectId) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] text-center space-y-4">
        <BarChart3 className="h-16 w-16 text-slate-600 animate-pulse" />
        <h2 className="text-xl font-semibold text-slate-300">No Project Selected</h2>
        <p className="text-slate-500 max-w-sm">
          Please select a project context from the Projects list to view the real-time control dashboard.
        </p>
      </div>
    );
  }

  // Derive alert signals from real data
  const alerts: { title: string; type: string; severity: "Low" | "Medium" | "High" | "Critical" }[] = [];
  if (evm) {
    if (evm.spi < 1.0) {
      alerts.push({
        title: `Project schedule is running behind plan (SPI = ${evm.spi.toFixed(2)})`,
        type: "Schedule Delay",
        severity: evm.spi < 0.8 ? "Critical" : "High",
      });
    }
    if (evm.cpi < 1.0) {
      alerts.push({
        title: `Project costs exceed budgeted earned value (CPI = ${evm.cpi.toFixed(2)})`,
        type: "Cost Overrun",
        severity: evm.cpi < 0.9 ? "Critical" : "High",
      });
    }
  }

  if (tasks) {
    const delayedCriticalTasks = tasks.filter(
      (t) => t.isCritical && t.status !== "COMPLETED" && new Date(t.endDate) < new Date()
    );
    delayedCriticalTasks.forEach((task) => {
      alerts.push({
        title: `Critical path task '${task.name}' is overdue`,
        type: "Critical Path",
        severity: "Critical",
      });
    });
  }

  if (alerts.length === 0) {
    alerts.push({
      title: "No critical performance alerts. Project indicators stable.",
      type: "System Health",
      severity: "Low",
    });
  }

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between flex-wrap gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-slate-100">
            Dashboard — {project?.name || "Loading..."}
          </h1>
          <p className="text-slate-400 mt-1">Real-time Earned Value Management (EVM) control panel.</p>
        </div>
        <div className="flex items-center gap-3">
          <Button
            onClick={handleDownloadPdf}
            variant="outline"
            size="sm"
            className="bg-slate-900 border-slate-800 text-slate-300 hover:bg-slate-800 text-xs"
          >
            <Download className="mr-1.5 h-3.5 w-3.5 text-red-400" /> Export PDF
          </Button>
          <Button
            onClick={handleDownloadExcel}
            variant="outline"
            size="sm"
            className="bg-slate-900 border-slate-800 text-slate-300 hover:bg-slate-800 text-xs"
          >
            <Download className="mr-1.5 h-3.5 w-3.5 text-emerald-400" /> Export Excel
          </Button>
        </div>
      </div>

      {isEvmLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 animate-pulse">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="h-28 bg-slate-900 border border-slate-800 rounded-xl"></div>
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <KPICard
            title="Schedule Performance (SPI)"
            value={evm?.spi.toFixed(2) || "1.00"}
            status={evm && evm.spi < 0.9 ? "danger" : evm && evm.spi < 1.0 ? "warning" : "success"}
            description="EV / PV ratio"
          />
          <KPICard
            title="Cost Performance (CPI)"
            value={evm?.cpi.toFixed(2) || "1.00"}
            status={evm && evm.cpi < 0.9 ? "danger" : evm && evm.cpi < 1.0 ? "warning" : "success"}
            description="EV / AC ratio"
          />
          <KPICard
            title="Estimate at Completion"
            value={evm?.eac.toLocaleString() || "0"}
            unit="DH"
            status="info"
            description="Projected Total Cost"
          />
          <KPICard
            title="Variance at Completion"
            value={evm?.cv.toLocaleString() || "0"}
            unit="DH"
            status={evm && evm.cv < 0 ? "danger" : "success"}
            description="Budget vs Forecast"
          />
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 bg-slate-900 border border-slate-800 rounded-xl p-6 flex flex-col justify-between min-h-[450px]">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h3 className="text-lg font-semibold text-slate-200">Earned Value S-Curve</h3>
              <p className="text-xs text-slate-500 mt-1">Planned Value, Earned Value, and Actual Cost trends.</p>
            </div>
          </div>

          <div className="flex-1 h-64 min-h-[280px]">
            {isChartLoading ? (
              <div className="w-full h-full flex items-center justify-center border border-dashed border-slate-800 rounded-lg animate-pulse bg-slate-900/10">
                <p className="text-slate-500 text-sm">Calculating S-Curve data points...</p>
              </div>
            ) : (
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={sCurveData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                  <XAxis dataKey="date" stroke="#64748b" fontSize={11} />
                  <YAxis stroke="#64748b" fontSize={11} />
                  <Tooltip
                    contentStyle={{ backgroundColor: "#0f172a", borderColor: "#334155", color: "#f8fafc" }}
                  />
                  <Legend verticalAlign="top" height={36} iconType="circle" fontSize={12} />
                  <Line type="monotone" dataKey="PV" name="Planned Value (PV)" stroke="#3b82f6" strokeWidth={2.5} dot={{ r: 4 }} activeDot={{ r: 6 }} />
                  <Line type="monotone" dataKey="EV" name="Earned Value (EV)" stroke="#10b981" strokeWidth={2.5} dot={{ r: 4 }} activeDot={{ r: 6 }} />
                  <Line type="monotone" dataKey="AC" name="Actual Cost (AC)" stroke="#f43f5e" strokeWidth={2.5} dot={{ r: 4 }} activeDot={{ r: 6 }} />
                </LineChart>
              </ResponsiveContainer>
            )}
          </div>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
          <h3 className="text-lg font-semibold text-slate-200 mb-6 flex items-center gap-2">
            <AlertCircle className={`h-5 w-5 ${alerts.some(a => a.severity === "Critical" || a.severity === "High") ? "text-rose-500" : "text-emerald-500"}`} />
            Performance Alerts
          </h3>
          <div className="space-y-4">
            {alerts.map((alert, i) => (
              <div
                key={i}
                className={`p-4 bg-slate-950/40 rounded-lg border-l-2 ${
                  alert.severity === "Critical"
                    ? "border-rose-500"
                    : alert.severity === "High"
                    ? "border-amber-500"
                    : "border-emerald-500"
                }`}
              >
                <p className="text-sm font-medium text-slate-200">{alert.title}</p>
                <div className="flex justify-between mt-3 text-[10px] font-bold uppercase tracking-wider">
                  <span className="text-slate-500">{alert.type}</span>
                  <span
                    className={
                      alert.severity === "Critical"
                        ? "text-rose-400"
                        : alert.severity === "High"
                        ? "text-amber-400"
                        : "text-emerald-400"
                    }
                  >
                    {alert.severity}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* AI Risk Auditor Section */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl space-y-6">
        <div className="flex items-center justify-between flex-wrap gap-4">
          <div className="flex items-center gap-2">
            <Sparkles className="h-5 w-5 text-indigo-400" />
            <h3 className="text-lg font-semibold text-slate-200">AI Risk & Performance Auditor</h3>
          </div>
          <Button
            onClick={handleTriggerAudit}
            disabled={triggerAuditMutation.isPending || isAuditLoading}
            variant="outline"
            size="sm"
            className="bg-slate-950 border-slate-800 text-slate-300 hover:bg-slate-800 text-xs gap-1.5"
          >
            <RefreshCw className={`h-3 w-3 ${(triggerAuditMutation.isPending || isAuditLoading) ? "animate-spin" : ""}`} />
            {triggerAuditMutation.isPending ? "Generating Audit..." : "Request New Audit"}
          </Button>
        </div>

        {isAuditLoading ? (
          <div className="h-40 flex items-center justify-center border border-dashed border-slate-800 rounded-lg animate-pulse bg-slate-950/10">
            <p className="text-slate-500 text-sm">Reviewing project WBS, risks, and EVM metrics to draft report...</p>
          </div>
        ) : auditReport ? (
          <div className="bg-slate-950/40 p-6 rounded-lg border border-slate-800 shadow-inner">
            <MarkdownPreview text={auditReport.insight_text} />
          </div>
        ) : (
          <div className="h-40 flex flex-col items-center justify-center border border-dashed border-slate-800 rounded-lg bg-slate-950/10 gap-3">
            <p className="text-slate-500 text-sm">No predictive risk report has been generated yet for this project.</p>
            <Button
              onClick={handleTriggerAudit}
              disabled={triggerAuditMutation.isPending}
              size="sm"
              className="bg-indigo-600 hover:bg-indigo-500 text-xs text-white"
            >
              Analyze Project with AI
            </Button>
          </div>
        )}
      </div>
    </div>
  );
}

interface MarkdownPreviewProps {
  text: string;
}

function MarkdownPreview({ text }: MarkdownPreviewProps) {
  if (!text) return null;
  const lines = text.split("\n");
  return (
    <div className="space-y-3 font-sans text-sm text-slate-300 leading-relaxed max-h-[500px] overflow-y-auto pr-2 custom-scrollbar">
      {lines.map((line, idx) => {
        if (line.startsWith("# ")) {
          return <h1 key={idx} className="text-xl font-bold text-slate-100 border-b border-slate-800 pb-1.5 mt-4">{line.substring(2)}</h1>;
        }
        if (line.startsWith("## ")) {
          return <h2 key={idx} className="text-lg font-semibold text-slate-100 mt-4">{line.substring(3)}</h2>;
        }
        if (line.startsWith("### ")) {
          return <h3 key={idx} className="text-base font-semibold text-slate-200 mt-3">{line.substring(4)}</h3>;
        }
        if (line.startsWith("- ")) {
          const parts = line.substring(2).split("**");
          return (
            <li key={idx} className="ml-4 list-disc text-slate-300">
              {parts.map((part, i) => i % 2 === 1 ? <strong key={i} className="text-slate-100 font-bold">{part}</strong> : part)}
            </li>
          );
        }
        if (line.startsWith("> [!")) {
          return null;
        }
        if (line.startsWith("> ")) {
          return <blockquote key={idx} className="border-l-2 border-blue-500 pl-3 py-1 my-2 bg-blue-500/5 text-slate-300 italic">{line.substring(2)}</blockquote>;
        }
        if (line.trim() === "") {
          return <div key={idx} className="h-2" />;
        }
        if (line.includes("**")) {
          const parts = line.split("**");
          return (
            <p key={idx}>
              {parts.map((part, i) => i % 2 === 1 ? <strong key={i} className="text-slate-100 font-bold">{part}</strong> : part)}
            </p>
          );
        }
        return <p key={idx}>{line}</p>;
      })}
    </div>
  );
}
