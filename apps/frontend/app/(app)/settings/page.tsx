import { Button } from "@/components/ui/button";
import { 
  Settings as SettingsIcon, 
  Database, 
  Lock, 
  Users, 
  Zap, 
  BellRing 
} from "lucide-react";

export default function SettingsPage() {
  const sections = [
    { title: "General", icon: SettingsIcon, desc: "Workspace name, branding, and global settings." },
    { title: "Team & Permissions", icon: Users, desc: "Invite members and manage RBAC roles." },
    { title: "Integrations", icon: Zap, desc: "Connect Clerk, Vercel, and External AI providers." },
    { title: "Notifications", icon: BellRing, desc: "Configure alert thresholds and email reports." },
    { title: "Database & Baselines", icon: Database, desc: "Manage project snapshots and data retention." },
    { title: "Security & Audit", icon: Lock, desc: "View system audit logs and session history." },
  ];

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-slate-100">Settings</h1>
        <p className="text-slate-400 mt-1">Configure your NEXUS workspace and system preferences.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {sections.map((section, i) => (
          <div key={i} className="bg-slate-900 border border-slate-800 rounded-xl p-6 hover:border-blue-500/30 transition-all group cursor-pointer">
            <div className="flex items-start gap-4">
              <div className="p-3 bg-slate-800 rounded-lg group-hover:bg-blue-600/10 group-hover:text-blue-400 text-slate-400 transition-colors">
                <section.icon className="h-6 w-6" />
              </div>
              <div className="flex-1">
                <h3 className="text-lg font-semibold text-slate-200 group-hover:text-blue-400 transition-colors">{section.title}</h3>
                <p className="text-sm text-slate-500 mt-1">{section.desc}</p>
              </div>
            </div>
          </div>
        ))}
      </div>
      
      <div className="pt-8 border-t border-slate-800 flex justify-end">
        <Button variant="destructive" className="bg-rose-600/10 text-rose-500 border border-rose-500/20 hover:bg-rose-500 hover:text-white transition-all">
          Delete Workspace
        </Button>
      </div>
    </div>
  );
}
