import { useState } from "react";
import { Search, User, FlaskConical, Pill, AlertTriangle, ChevronRight, Loader2 } from "lucide-react";
import { Patient } from "@/data/mockPatients";
import { PatientSummary } from "@/components/PatientSummary";
import { AnimatePresence, motion } from "framer-motion";
import { cn } from "@/lib/utils";

interface PatientSearchViewProps {
  patients: Patient[];
  isLoading?: boolean;
}

export function PatientSearchView({ patients, isLoading }: PatientSearchViewProps) {
  const [query, setQuery] = useState("");
  const [selected, setSelected] = useState<Patient | null>(null);

  if (isLoading) {
    return (
      <div className="flex h-full items-center justify-center p-12">
        <Loader2 className="h-10 w-10 animate-spin text-primary opacity-50" />
      </div>
    );
  }

  const results = patients.filter((p) => {
    const q = query.toLowerCase();
    if (!q) return true;
    return (
      p.name.toLowerCase().includes(q) ||
      p.id.toLowerCase().includes(q) ||
      p.diagnoses.some((d) => d.toLowerCase().includes(q)) ||
      p.attendingDoctor.toLowerCase().includes(q)
    );
  });

  return (
    <div className="flex flex-col h-full min-h-0 p-5 gap-5">
      {/* Search bar */}
      <div>
        <h2 className="text-base font-semibold text-foreground mb-3">Patient Search</h2>
        <div className="relative">
          <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search by name, ID, diagnosis, or doctor..."
            className="w-full pl-10 pr-4 py-2.5 bg-card border border-border rounded-xl text-sm text-foreground placeholder:text-muted-foreground outline-none focus:border-primary focus:shadow-elevated transition-all"
          />
        </div>
      </div>

      <div className="flex-1 min-h-0 overflow-y-auto space-y-4">
        {/* Patient cards list */}
        <div className="grid gap-3">
          {results.map((p) => {
            const criticals = p.labResults.filter((l) => l.status === "critical").length;
            const warnings = p.labResults.filter((l) => l.status === "warning").length;
            return (
              <motion.div
                key={p.id}
                initial={{ opacity: 0, y: 6 }}
                animate={{ opacity: 1, y: 0 }}
                className={cn(
                  "bg-card border rounded-xl p-4 cursor-pointer transition-all hover:border-primary hover:shadow-elevated group",
                  selected?.id === p.id ? "border-primary shadow-elevated" : "border-border shadow-card"
                )}
                onClick={() => setSelected(selected?.id === p.id ? null : p)}
              >
                <div className="flex items-center justify-between gap-3">
                  <div className="flex items-center gap-3 min-w-0">
                    <div className="w-10 h-10 rounded-full bg-primary-light border border-primary-muted flex items-center justify-center flex-shrink-0">
                      <User className="w-5 h-5 text-primary" />
                    </div>
                    <div className="min-w-0">
                      <div className="flex items-center gap-2">
                        <p className="font-semibold text-sm text-foreground">{p.name}</p>
                        <span className="text-xs px-2 py-0.5 bg-secondary text-secondary-foreground rounded-full">{p.id}</span>
                      </div>
                      <p className="text-xs text-muted-foreground mt-0.5">{p.age}y · {p.gender} · {p.ward}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2 flex-shrink-0">
                    {criticals > 0 && (
                      <span className="flex items-center gap-1 text-xs px-2 py-0.5 bg-destructive-light text-destructive rounded-full border border-destructive/20">
                        <AlertTriangle className="w-3 h-3" />
                        {criticals}
                      </span>
                    )}
                    {warnings > 0 && (
                      <span className="flex items-center gap-1 text-xs px-2 py-0.5 bg-warning-light text-warning-foreground rounded-full border border-warning/20">
                        <AlertTriangle className="w-3 h-3" />
                        {warnings}
                      </span>
                    )}
                    <ChevronRight className={cn(
                      "w-4 h-4 text-muted-foreground transition-transform",
                      selected?.id === p.id ? "rotate-90 text-primary" : "group-hover:text-primary"
                    )} />
                  </div>
                </div>
                <div className="mt-3 flex flex-wrap gap-1.5">
                  {p.diagnoses.map((d) => (
                    <span key={d} className="text-xs px-2 py-0.5 bg-muted text-muted-foreground rounded-md">{d}</span>
                  ))}
                </div>
              </motion.div>
            );
          })}
        </div>

        {/* Expanded patient detail */}
        <AnimatePresence>
          {selected && (
            <PatientSummary key={selected.id} patient={selected} onClose={() => setSelected(null)} />
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
