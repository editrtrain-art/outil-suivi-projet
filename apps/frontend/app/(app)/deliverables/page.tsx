import { DeliverableCard } from "@/components/deliverables/DeliverableCard";
import { Button } from "@/components/ui/button";
import { Plus, Filter, LayoutGrid, List } from "lucide-react";

const mockDeliverables = [
  { id: "1", name: "Geotechnical Survey Report", task: "Site Investigation", dueDate: "2026-06-15", status: 'approved', owner: "A. El Fassi" },
  { id: "2", name: "Structural Design V1", task: "Detailed Design", dueDate: "2026-07-10", status: 'in_review', owner: "S. Bennani" },
  { id: "3", name: "Procurement Plan", task: "Project Setup", dueDate: "2026-06-20", status: 'submitted', owner: "M. Alami" },
  { id: "4", name: "Safety Audit Protocol", task: "Health & Safety", dueDate: "2026-08-05", status: 'draft', owner: "L. Rouissi" },
  { id: "5", name: "Foundation Blueprints", task: "Execution Drawing", dueDate: "2026-07-25", status: 'rejected', owner: "S. Bennani" },
] as const;

export default function DeliverablesPage() {
  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-slate-100">Deliverables</h1>
          <p className="text-slate-400 mt-1">Track document lifecycle and validation workflow.</p>
        </div>
        <div className="flex gap-3">
          <div className="flex bg-slate-900 border border-slate-800 rounded-lg p-1">
            <button className="p-1.5 bg-slate-800 text-blue-400 rounded-md"><LayoutGrid className="h-4 w-4" /></button>
            <button className="p-1.5 text-slate-500 hover:text-slate-300"><List className="h-4 w-4" /></button>
          </div>
          <Button size="sm" className="bg-blue-600 hover:bg-blue-500">
            <Plus className="mr-2 h-4 w-4" /> New Deliverable
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-6">
        {mockDeliverables.map(item => (
          <DeliverableCard key={item.id} item={item} />
        ))}
      </div>

      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
        <h3 className="text-lg font-semibold text-slate-200 mb-6">Deliverable Status Analytics</h3>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
           <div className="h-32 border border-dashed border-slate-800 rounded-lg flex items-center justify-center text-slate-500 text-xs">Pie Chart: Completion</div>
           <div className="h-32 border border-dashed border-slate-800 rounded-lg flex items-center justify-center text-slate-500 text-xs">Stat: Overdue Items</div>
           <div className="h-32 border border-dashed border-slate-800 rounded-lg flex items-center justify-center text-slate-500 text-xs">Stat: Approval Cycle Time</div>
           <div className="h-32 border border-dashed border-slate-800 rounded-lg flex items-center justify-center text-slate-500 text-xs">Stat: Rejection Rate</div>
        </div>
      </div>
    </div>
  );
}
