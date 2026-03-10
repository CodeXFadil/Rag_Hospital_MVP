import { Patient } from "@/data/mockPatients";
import { motion } from "framer-motion";
import {
  User, Pill, FlaskConical, AlertTriangle, CheckCircle,
  Calendar, Stethoscope, Building2, X,
} from "lucide-react";
import { cn } from "@/lib/utils";

interface PatientSummaryProps {
  patient: Patient;
  onClose?: () => void;
}

const statusConfig = {
  normal: {
    badge: "bg-success-light text-success border border-success/20",
    icon: CheckCircle,
    iconClass: "text-success",
  },
  warning: {
    badge: "bg-warning-light text-warning-foreground border border-warning/20",
    icon: AlertTriangle,
    iconClass: "text-warning",
  },
  critical: {
    badge: "bg-destructive-light text-destructive border border-destructive/20",
    icon: AlertTriangle,
    iconClass: "text-destructive",
  },
};

export function PatientSummary({ patient, onClose }: PatientSummaryProps) {
  const criticalCount = patient.labResults.filter((l) => l.status === "critical").length;
  const warningCount = patient.labResults.filter((l) => l.status === "warning").length;

  return (
    <motion.div
      initial={{ opacity: 0, y: -12 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -12 }}
      transition={{ duration: 0.3 }}
      className="bg-card border border-border rounded-xl shadow-card overflow-hidden"
    >
      {/* Header */}
      <div className="gradient-hero px-5 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-primary-foreground/20 flex items-center justify-center">
            <User className="w-5 h-5 text-primary-foreground" />
          </div>
          <div>
            <h3 className="font-semibold text-primary-foreground text-base">{patient.name}</h3>
            <div className="flex items-center gap-2 mt-0.5">
              <span className="text-primary-foreground/80 text-xs">{patient.id}</span>
              <span className="text-primary-foreground/40">·</span>
              <span className="text-primary-foreground/80 text-xs">{patient.age}y · {patient.gender}</span>
              <span className="text-primary-foreground/40">·</span>
              <span className="text-primary-foreground/80 text-xs">{patient.bloodGroup}</span>
            </div>
          </div>
        </div>
        <div className="flex items-center gap-2">
          {criticalCount > 0 && (
            <span className="flex items-center gap-1 bg-destructive/20 text-primary-foreground text-xs px-2 py-1 rounded-full border border-destructive/30">
              <AlertTriangle className="w-3 h-3" />
              {criticalCount} Critical
            </span>
          )}
          {onClose && (
            <button
              onClick={onClose}
              className="text-primary-foreground/60 hover:text-primary-foreground transition-colors ml-1"
            >
              <X className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>

      {/* Meta row */}
      <div className="px-5 py-3 bg-primary-light/60 border-b border-border flex flex-wrap gap-x-6 gap-y-1">
        <MetaItem icon={Stethoscope} label="Attending" value={patient.attendingDoctor} />
        <MetaItem icon={Building2} label="Ward" value={patient.ward} />
        <MetaItem icon={Calendar} label="Last Visit" value={patient.lastVisit} />
      </div>

      <div className="p-5 grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Diagnoses */}
        <div className="lg:col-span-1">
          <SectionHeader icon={Stethoscope} label="Diagnoses" />
          <div className="mt-2 space-y-1.5">
            {patient.diagnoses.map((d) => (
              <div
                key={d}
                className="flex items-start gap-2 text-sm text-foreground"
              >
                <span className="mt-1.5 w-1.5 h-1.5 rounded-full bg-primary flex-shrink-0" />
                {d}
              </div>
            ))}
          </div>
        </div>

        {/* Medications */}
        <div className="lg:col-span-1">
          <SectionHeader icon={Pill} label="Medications" />
          <div className="mt-2 space-y-2">
            {patient.medications.slice(0, 4).map((m) => (
              <div key={m.name} className="flex items-start gap-2">
                <div className="w-6 h-6 rounded-md bg-accent-light flex items-center justify-center flex-shrink-0 mt-0.5">
                  <Pill className="w-3 h-3 text-accent" />
                </div>
                <div>
                  <p className="text-sm font-medium text-foreground">{m.name}</p>
                  <p className="text-xs text-muted-foreground">{m.dosage} · {m.frequency}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Lab Results */}
        <div className="lg:col-span-1">
          <SectionHeader icon={FlaskConical} label="Lab Results" />
          <div className="mt-2 space-y-2">
            {patient.labResults.map((lab) => {
              const cfg = statusConfig[lab.status];
              return (
                <div key={lab.name} className="flex items-center justify-between gap-2">
                  <div className="flex items-center gap-1.5 min-w-0">
                    <cfg.icon className={cn("w-3.5 h-3.5 flex-shrink-0", cfg.iconClass)} />
                    <span className="text-xs text-muted-foreground truncate">{lab.name}</span>
                  </div>
                  <span className={cn("text-xs px-2 py-0.5 rounded-full font-medium flex-shrink-0", cfg.badge)}>
                    {lab.value} {lab.unit}
                  </span>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Risk strip */}
      {(criticalCount > 0 || warningCount > 0) && (
        <div className="px-5 py-3 bg-warning-light/50 border-t border-warning/20 flex items-start gap-2">
          <AlertTriangle className="w-4 h-4 text-warning mt-0.5 flex-shrink-0" />
          <p className="text-xs text-warning-foreground">
            <span className="font-medium">Risk Indicators: </span>
            {criticalCount > 0 && `${criticalCount} critical value${criticalCount > 1 ? "s" : ""} require immediate attention. `}
            {warningCount > 0 && `${warningCount} value${warningCount > 1 ? "s" : ""} elevated beyond normal range.`}
          </p>
        </div>
      )}
    </motion.div>
  );
}

function SectionHeader({ icon: Icon, label }: { icon: React.ElementType; label: string }) {
  return (
    <div className="flex items-center gap-2">
      <div className="w-5 h-5 rounded bg-primary-light flex items-center justify-center">
        <Icon className="w-3 h-3 text-primary" />
      </div>
      <span className="text-xs font-semibold text-foreground uppercase tracking-wider">{label}</span>
    </div>
  );
}

function MetaItem({ icon: Icon, label, value }: { icon: React.ElementType; label: string; value: string }) {
  return (
    <div className="flex items-center gap-1.5">
      <Icon className="w-3.5 h-3.5 text-primary/60" />
      <span className="text-xs text-muted-foreground">{label}:</span>
      <span className="text-xs font-medium text-foreground">{value}</span>
    </div>
  );
}
