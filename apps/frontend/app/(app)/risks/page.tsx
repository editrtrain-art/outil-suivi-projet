import { Button } from "@/components/ui/button";
import { 
  ShieldAlert, 
  Search, 
  Plus, 
  ArrowUpRight, 
  AlertTriangle 
} from "lucide-react";

export default function RisksPage() {
  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-slate-100">Risk Register</h1>
          <p className="text-slate-400 mt-1">Identification, scoring, and automated contingency management.</p>
        </div>
        <Button size="sm" className="bg-blue-600 hover:bg-blue-500">
          <Plus className="mr-2 h-4 w-4" /> Identify Risk
        </Button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 bg-slate-900 border border-slate-800 rounded-xl p-6">
          <h3 className="text-lg font-semibold text-slate-200 mb-6 flex items-center gap-2">
            <ShieldAlert className="h-5 w-5 text-blue-500" />
            Probability / Impact Matrix
          </h3>
          <div className="grid grid-cols-5 gap-1 aspect-square max-w-md mx-auto">
             {Array.from({ length: 25 }).map((_, i) => {
               const row = Math.floor(i / 5);
               const col = i % 5;
               const score = (5 - row) * (col + 1);
               let color = "bg-emerald-500/10 hover:bg-emerald-500/20";
               if (score >= 15) color = "bg-rose-500/40 hover:bg-rose-500/50";
               else if (score >= 8) color = "bg-amber-500/20 hover:bg-amber-500/30";
               
               return (
                 <div key={i} className={`rounded-sm border border-slate-800 transition-colors flex items-center justify-center text-[10px] text-slate-600 ${color}`}>
                   {score}
                 </div>
               );
             })}
          </div>
          <div className="flex justify-between mt-4 text-[10px] uppercase font-bold text-slate-500 px-4">
            <span>Low Impact</span>
            <span>High Impact</span>
          </div>
        </div>

        <div className="space-y-6">
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
             <h3 className="text-sm font-bold text-slate-400 uppercase tracking-widest mb-4">Contingency Impact</h3>
             <div className="text-3xl font-bold text-slate-100">+4.5 Days</div>
             <p className="text-xs text-slate-500 mt-1">Automatically added to critical path duration based on active risk scores.</p>
          </div>
          
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
             <h3 className="text-sm font-bold text-slate-400 uppercase tracking-widest mb-4">Top Threats</h3>
             <div className="space-y-4">
               {[
                 { title: "Supply chain delay (Steel)", score: 20 },
                 { title: "Key resource unavailability", score: 16 },
                 { title: "Regulatory approval lag", score: 12 },
               ].map((risk, i) => (
                 <div key={i} className="flex items-center justify-between p-2 bg-slate-800/30 rounded border border-slate-800/50">
                    <span className="text-xs text-slate-300 truncate mr-4">{risk.title}</span>
                    <span className="text-xs font-bold text-rose-500">{risk.score}</span>
                 </div>
               ))}
             </div>
          </div>
        </div>
      </div>
    </div>
  );
}
