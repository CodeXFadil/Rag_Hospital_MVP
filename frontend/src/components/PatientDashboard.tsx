import { mockPatients } from "@/data/mockPatients";
import { motion } from "framer-motion";
import {
  Users, AlertTriangle, Activity, TrendingUp, FlaskConical,
  CheckCircle, ArrowUp, ArrowDown,
} from "lucide-react";
import { cn } from "@/lib/utils";

export function PatientDashboard() {
  const patients = Object.values(mockPatients);
  const totalPatients = patients.length;
  const criticalPatients = patients.filter((p) =>
    p.labResults.some((l) => l.status === "critical")
  ).length;
  const stablePatients = patients.filter((p) =>
    p.labResults.every((l) => l.status === "normal")
  ).length;
  const warningPatients = totalPatients - criticalPatients - stablePatients;

  const stats = [
    {
      label: "Total Patients",
      value: totalPatients,
      icon: Users,
      color: "text-primary",
      bg: "bg-primary-light",
      change: "+2 this week",
      up: true,
    },
    {
      label: "Critical Cases",
      value: criticalPatients,
      icon: AlertTriangle,
      color: "text-destructive",
      bg: "bg-destructive-light",
      change: "Requires attention",
      up: false,
    },
    {
      label: "Monitoring",
      value: warningPatients,
      icon: Activity,
      color: "text-warning",
      bg: "bg-warning-light",
      change: "Elevated values",
      up: false,
    },
    {
      label: "Stable",
      value: stablePatients,
      icon: CheckCircle,
      color: "text-success",
      bg: "bg-success-light",
      change: "All values normal",
      up: true,
    },
  ];

  return (
    <div className="p-5 space-y-6 overflow-y-auto h-full">
      <div>
        <h2 className="text-base font-semibold text-foreground">Patient Dashboard</h2>
        <p className="text-xs text-muted-foreground mt-0.5">Overview of current patient records and clinical indicators</p>
      </div>

      {/* Stats grid */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        {stats.map((s, i) => {
          const Icon = s.icon;
          return (
            <motion.div
              key={s.label}
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.08 }}
              className="bg-card border border-border rounded-xl p-4 shadow-card"
            >
              <div className="flex items-center justify-between mb-3">
                <div className={cn("w-9 h-9 rounded-lg flex items-center justify-center", s.bg)}>
                  <Icon className={cn("w-4 h-4", s.color)} />
                </div>
                <span className={cn(
                  "flex items-center gap-0.5 text-xs",
                  s.up ? "text-success" : "text-muted-foreground"
                )}>
                  {s.up ? <ArrowUp className="w-3 h-3" /> : null}
                </span>
              </div>
              <p className="text-2xl font-bold text-foreground">{s.value}</p>
              <p className="text-xs font-medium text-foreground mt-0.5">{s.label}</p>
              <p className="text-xs text-muted-foreground mt-0.5">{s.change}</p>
            </motion.div>
          );
        })}
      </div>

      {/* Patients overview table */}
      <div className="bg-card border border-border rounded-xl shadow-card overflow-hidden">
        <div className="px-5 py-3.5 border-b border-border flex items-center justify-between">
          <h3 className="text-sm font-semibold text-foreground">All Patients</h3>
          <span className="text-xs text-muted-foreground">{totalPatients} records</span>
        </div>
        <div className="divide-y divide-border">
          {patients.map((p, i) => {
            const critical = p.labResults.some((l) => l.status === "critical");
            const warning = !critical && p.labResults.some((l) => l.status === "warning");
            const stable = !critical && !warning;
            return (
              <motion.div
                key={p.id}
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.2 + i * 0.06 }}
                className="px-5 py-4 flex items-center gap-4 hover:bg-muted/30 transition-colors"
              >
                <div className="w-9 h-9 rounded-full bg-primary-light border border-primary-muted flex items-center justify-center flex-shrink-0">
                  <span className="text-xs font-semibold text-primary">
                    {p.name.split(" ").map((n) => n[0]).join("").slice(0, 2)}
                  </span>
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <p className="text-sm font-medium text-foreground">{p.name}</p>
                    <span className="text-xs text-muted-foreground">{p.id}</span>
                  </div>
                  <p className="text-xs text-muted-foreground truncate">{p.diagnoses[0]}{p.diagnoses.length > 1 ? ` +${p.diagnoses.length - 1} more` : ""}</p>
                </div>
                <div className="hidden md:flex items-center gap-2 text-xs text-muted-foreground">
                  <FlaskConical className="w-3.5 h-3.5" />
                  {p.labResults.length} tests
                </div>
                <div className="hidden md:block text-xs text-muted-foreground">{p.lastVisit}</div>
                <div>
                  {critical && (
                    <span className="flex items-center gap-1 text-xs px-2.5 py-1 bg-destructive-light text-destructive rounded-full border border-destructive/20 font-medium">
                      <span className="w-1.5 h-1.5 rounded-full bg-destructive" />
                      Critical
                    </span>
                  )}
                  {warning && (
                    <span className="flex items-center gap-1 text-xs px-2.5 py-1 bg-warning-light text-warning-foreground rounded-full border border-warning/20 font-medium">
                      <span className="w-1.5 h-1.5 rounded-full bg-warning" />
                      Monitor
                    </span>
                  )}
                  {stable && (
                    <span className="flex items-center gap-1 text-xs px-2.5 py-1 bg-success-light text-success rounded-full border border-success/20 font-medium">
                      <span className="w-1.5 h-1.5 rounded-full bg-success" />
                      Stable
                    </span>
                  )}
                </div>
              </motion.div>
            );
          })}
        </div>
      </div>

      {/* Lab results heatmap */}
      <div className="bg-card border border-border rounded-xl shadow-card overflow-hidden">
        <div className="px-5 py-3.5 border-b border-border">
          <h3 className="text-sm font-semibold text-foreground">Lab Results Overview</h3>
          <p className="text-xs text-muted-foreground">Abnormal values across all patients</p>
        </div>
        <div className="p-5 overflow-x-auto">
          <table className="w-full text-xs">
            <thead>
              <tr>
                <th className="text-left text-muted-foreground font-medium pb-3 pr-4 min-w-[120px]">Patient</th>
                {["HbA1c", "Blood Pressure", "Hemoglobin", "Creatinine", "Cholesterol"].map((h) => (
                  <th key={h} className="text-center text-muted-foreground font-medium pb-3 px-2 min-w-[90px]">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {patients.map((p) => (
                <tr key={p.id}>
                  <td className="py-2 pr-4">
                    <div>
                      <p className="font-medium text-foreground">{p.name}</p>
                      <p className="text-muted-foreground">{p.id}</p>
                    </div>
                  </td>
                  {["HbA1c", "Blood Pressure", "Hemoglobin", "Creatinine", "Total Cholesterol"].map((labName) => {
                    const lab = p.labResults.find(
                      (l) => l.name === labName || (labName === "Blood Pressure" && l.name === "Blood Pressure")
                    );
                    if (!lab) {
                      return (
                        <td key={labName} className="py-2 px-2 text-center">
                          <span className="text-muted-foreground/40">—</span>
                        </td>
                      );
                    }
                    return (
                      <td key={labName} className="py-2 px-2 text-center">
                        <span className={cn(
                          "inline-block px-2 py-0.5 rounded-md font-medium",
                          lab.status === "critical" ? "bg-destructive-light text-destructive" :
                          lab.status === "warning" ? "bg-warning-light text-warning-foreground" :
                          "bg-success-light text-success"
                        )}>
                          {lab.value}
                        </span>
                      </td>
                    );
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
