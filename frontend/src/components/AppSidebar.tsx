import { motion } from "framer-motion";
import { Activity, MessageSquare, Search, LayoutDashboard, History, X, ChevronLeft } from "lucide-react";
import { cn } from "@/lib/utils";

interface AppSidebarProps {
  activeTab: string;
  onTabChange: (tab: string) => void;
  queryHistory: string[];
  isOpen: boolean;
  onClose: () => void;
}

const navItems = [
  { id: "chat", label: "Chat Assistant", icon: MessageSquare },
  { id: "search", label: "Patient Search", icon: Search },
  { id: "dashboard", label: "Patient Dashboard", icon: LayoutDashboard },
  { id: "history", label: "Query History", icon: History },
];

export function AppSidebar({
  activeTab,
  onTabChange,
  queryHistory,
  isOpen,
  onClose,
}: AppSidebarProps) {
  return (
    <>
      {/* Mobile overlay */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-foreground/20 backdrop-blur-sm z-20 lg:hidden"
          onClick={onClose}
        />
      )}

      <motion.aside
        initial={false}
        animate={{ x: isOpen ? 0 : "-100%" }}
        transition={{ type: "spring", stiffness: 300, damping: 30 }}
        className={cn(
          "fixed lg:relative lg:translate-x-0 z-30 h-full w-64 flex-shrink-0",
          "gradient-sidebar border-r border-sidebar-border",
          "flex flex-col overflow-hidden"
        )}
      >
        {/* Logo / Header */}
        <div className="flex items-center gap-3 px-5 py-5 border-b border-sidebar-border">
          <div className="w-8 h-8 rounded-lg gradient-hero flex items-center justify-center flex-shrink-0">
            <Activity className="w-4 h-4 text-primary-foreground" />
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sidebar-primary-foreground font-semibold text-sm leading-tight">Hospital AI</p>
            <p className="text-sidebar-foreground text-xs truncate">Patient Records Assistant</p>
          </div>
          <button
            onClick={onClose}
            className="lg:hidden text-sidebar-foreground hover:text-sidebar-primary-foreground transition-colors p-1"
          >
            <ChevronLeft className="w-4 h-4" />
          </button>
        </div>

        {/* Navigation */}
        <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
          <p className="text-xs font-medium text-sidebar-foreground/50 uppercase tracking-wider px-2 mb-3">
            Navigation
          </p>
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => {
                  onTabChange(item.id);
                  onClose();
                }}
                className={cn(
                  "w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-150",
                  isActive
                    ? "bg-sidebar-primary text-sidebar-primary-foreground shadow-sm"
                    : "text-sidebar-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground"
                )}
              >
                <Icon className="w-4 h-4 flex-shrink-0" />
                <span>{item.label}</span>
                {isActive && (
                  <motion.div
                    layoutId="active-pill"
                    className="ml-auto w-1.5 h-1.5 rounded-full bg-sidebar-primary-foreground/60"
                  />
                )}
              </button>
            );
          })}

          {/* Query History */}
          {queryHistory.length > 0 && (
            <div className="mt-6">
              <p className="text-xs font-medium text-sidebar-foreground/50 uppercase tracking-wider px-2 mb-3">
                Recent Queries
              </p>
              <div className="space-y-1">
                {queryHistory.slice(0, 8).map((q, i) => (
                  <div
                    key={i}
                    className="flex items-start gap-2 px-3 py-2 rounded-md hover:bg-sidebar-accent cursor-pointer group transition-colors"
                    onClick={() => onTabChange("chat")}
                  >
                    <History className="w-3 h-3 text-sidebar-foreground/40 mt-0.5 flex-shrink-0" />
                    <span className="text-xs text-sidebar-foreground/60 group-hover:text-sidebar-accent-foreground truncate leading-tight">
                      {q}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </nav>

        {/* Footer */}
        <div className="px-5 py-4 border-t border-sidebar-border">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-full bg-sidebar-accent flex items-center justify-center">
              <span className="text-xs font-medium text-sidebar-accent-foreground">DR</span>
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-xs font-medium text-sidebar-primary-foreground truncate">Dr. Admin</p>
              <p className="text-xs text-sidebar-foreground/60 truncate">Senior Physician</p>
            </div>
          </div>
        </div>
      </motion.aside>
    </>
  );
}
