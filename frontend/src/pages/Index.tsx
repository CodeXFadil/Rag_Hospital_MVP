import { useState } from "react";
import { Menu, Activity } from "lucide-react";
import { AppSidebar } from "@/components/AppSidebar";
import { ChatInterface } from "@/components/ChatInterface";
import { PatientSearchView } from "@/components/PatientSearchView";
import { PatientDashboard } from "@/components/PatientDashboard";
import { QueryHistoryView } from "@/components/QueryHistoryView";

const Index = () => {
  const [activeTab, setActiveTab] = useState("chat");
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [queryHistory, setQueryHistory] = useState<string[]>([]);

  const handleQueryAdded = (q: string) => {
    setQueryHistory((prev) => [q, ...prev]);
  };

  const handleHistorySelect = (q: string) => {
    setActiveTab("chat");
  };

  const handleClearHistory = () => {
    setQueryHistory([]);
  };

  const renderMain = () => {
    switch (activeTab) {
      case "chat":
        return <ChatInterface onQueryAdded={handleQueryAdded} />;
      case "search":
        return <PatientSearchView />;
      case "dashboard":
        return <PatientDashboard />;
      case "history":
        return (
          <QueryHistoryView
            history={queryHistory}
            onClear={handleClearHistory}
            onSelectQuery={handleHistorySelect}
          />
        );
      default:
        return <ChatInterface onQueryAdded={handleQueryAdded} />;
    }
  };

  const tabLabels: Record<string, string> = {
    chat: "Chat Assistant",
    search: "Patient Search",
    dashboard: "Patient Dashboard",
    history: "Query History",
  };

  return (
    <div className="flex h-screen w-full overflow-hidden bg-background">
      {/* Sidebar */}
      <AppSidebar
        activeTab={activeTab}
        onTabChange={setActiveTab}
        queryHistory={queryHistory}
        isOpen={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
      />

      {/* Main */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        {/* Top bar */}
        <header className="h-14 flex items-center gap-3 px-4 border-b border-border bg-card/80 backdrop-blur-sm flex-shrink-0">
          <button
            onClick={() => setSidebarOpen((v) => !v)}
            className="w-8 h-8 flex items-center justify-center rounded-lg hover:bg-muted transition-colors text-muted-foreground hover:text-foreground"
          >
            <Menu className="w-4 h-4" />
          </button>

          {/* Breadcrumb */}
          <div className="flex items-center gap-2 text-sm">
            <Activity className="w-4 h-4 text-primary" />
            <span className="text-muted-foreground">Hospital AI</span>
            <span className="text-muted-foreground/40">/</span>
            <span className="font-medium text-foreground">{tabLabels[activeTab]}</span>
          </div>

          <div className="ml-auto flex items-center gap-2">
            <span className="hidden sm:flex items-center gap-1.5 text-xs text-muted-foreground bg-success-light text-success border border-success/20 px-3 py-1.5 rounded-full">
              <span className="w-1.5 h-1.5 rounded-full bg-success animate-pulse-soft" />
              System Online
            </span>
          </div>
        </header>

        {/* Content */}
        <main className="flex-1 min-h-0 overflow-hidden">
          {renderMain()}
        </main>
      </div>
    </div>
  );
};

export default Index;
