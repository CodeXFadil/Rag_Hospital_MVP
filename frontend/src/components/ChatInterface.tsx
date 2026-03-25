import { useState, useRef, useEffect, useCallback } from "react";
import { AnimatePresence } from "framer-motion";
import { Trash2, Bot } from "lucide-react";
import { ChatMessage, TypingIndicator, Message } from "@/components/ChatMessage";
import { ChatInput } from "@/components/ChatInput";
import { PatientSummary } from "@/components/PatientSummary";
import type { Patient } from "@/data/mockPatients";

interface ChatInterfaceProps {
  onQueryAdded: (query: string) => void;
}

const welcomeMessages: Message[] = [
  {
    id: "welcome",
    role: "assistant",
    content: `## Welcome to Hospital Patient Records Assistant 👋

I'm your AI-powered clinical assistant. I can help you with:

- **Patient summaries** — Ask "Summarize patient P001" or search by name
- **Medication queries** — E.g., "What medications is Rahul Sharma taking?"
- **Lab results** — E.g., "Which patients have HbA1c above 8?"
- **Clinical overviews** — Get structured patient data at a glance

*Available patients: Rahul Sharma (P001), Anita Desai (P014), Mohammed Al-Hassan (P022)*

How can I assist you today?`,
    timestamp: new Date(),
  },
];

export function ChatInterface({ onQueryAdded }: ChatInterfaceProps) {
  const [messages, setMessages] = useState<Message[]>(welcomeMessages);
  const [isLoading, setIsLoading] = useState(false);
  const [activePatient, setActivePatient] = useState<Patient | null>(null);
  const [backendVersion, setBackendVersion] = useState<string>("V3.0");
  const [isOnline, setIsOnline] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  // Normalize URL to prevent trailing slash issues
  const rawUrl = import.meta.env.VITE_API_URL || "http://localhost:8000";
  const apiUrl = rawUrl.replace(/\/$/, "");

  // Check backend health on mount
  useEffect(() => {
    const checkHealth = async () => {
      try {
        const res = await fetch(`${apiUrl}/health`);
        if (res.ok) {
          const data = await res.json();
          setBackendVersion(data.version || "V3.6");
          setIsOnline(true);
        } else {
          setIsOnline(false);
          setBackendVersion("OFFLINE");
        }
      } catch (err) {
        console.error("Backend offline:", err);
        setIsOnline(false);
        setBackendVersion("CONNECT ERROR");
      }
    };
    checkHealth();
    const interval = setInterval(checkHealth, 30000);
    return () => clearInterval(interval);
  }, [apiUrl]);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, isLoading]);

  const handleSubmit = useCallback(
    async (query: string) => {
      const userMsg: Message = {
        id: Date.now().toString(),
        role: "user",
        content: query,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, userMsg]);
      setIsLoading(true);
      onQueryAdded(query);

      try {
        const response = await fetch(`${apiUrl}/api/chat`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ query }),
        });
        
        if (!response.ok) {
          const errorData = await response.json().catch(() => ({}));
          const specificError = errorData.detail || `Server Error ${response.status}`;
          throw new Error(specificError);
        }
        
        const data = await response.json();
        
        let text = data.llm_response || "No response generated.";
        
        // Append risk flags — only for summary intent or explicit risk queries
        const summaryIntents = ["patient_summary", "clinical_notes"];
        const riskKeywords = ["risk", "flag", "warning", "indicator", "concern", "danger", "alert", "analysis", "problem", "critical"];
        const intentVal: string = data.intent?.primary_intent || "";
        const queryAsksForRisks = riskKeywords.some((kw) => query.toLowerCase().includes(kw));
        const shouldShowRisks = summaryIntents.includes(intentVal) || queryAsksForRisks;

        if (shouldShowRisks && data.risk_flags && data.risk_flags.length > 0) {
          text += "\n\n### 🚨 Risk Indicators\n" + data.risk_flags.map((f: any) => `- **${f.flag}**: ${f.detail}`).join("\n");
        }

        
        // Append notes if any
        if (data.notes && data.notes.length > 0) {
          const relevantNotes = data.notes.filter((n: any) => n.score > 0.1);
          if (relevantNotes.length > 0) {
            text += "\n\n### 📄 Relevant Clinical Notes\n" + relevantNotes.map((n: any) => `> **${n.patient_id} - ${n.name}**: ${n.text}`).join("\n\n");
          }
        }

        // Set active patient if found
        if (data.patients && data.patients.length > 0) {
          const p = data.patients[0];
          setActivePatient({
            id: p.patient_id,
            name: p.name,
            age: parseInt(p.age) || 0,
            gender: p.gender,
            bloodGroup: "Unknown",
            diagnoses: p.diagnoses?.split(",\n") || [],
            medications: [{ name: p.medications, dosage: "", frequency: "", since: "" }],
            labResults: [{ name: p.lab_results, value: "", unit: "", normalRange: "", status: "normal" }],
            lastVisit: p.visit_history.split("\n")[0] || "Unknown",
            ward: "Unknown",
            attendingDoctor: "Unknown",
            notes: "Retrieved from RAG backend"
          });
        }

        const aiMsg: Message = {
          id: (Date.now() + 1).toString(),
          role: "assistant",
          content: text,
          timestamp: new Date(),
        };
        setMessages((prev) => [...prev, aiMsg]);

      } catch (error: any) {
        console.error("Fetch error:", error);
        const errMsg: Message = {
          id: (Date.now() + 1).toString(),
          role: "assistant",
          content: `❌ **Backend Error**\n\n${error.message || "Failed to connect to the backend server."}`,
          timestamp: new Date(),
        };
        setMessages((prev) => [...prev, errMsg]);
      }
      
      setIsLoading(false);
    },
    [onQueryAdded, apiUrl]
  );

  const handleClear = () => {
    setMessages(welcomeMessages);
    setActivePatient(null);
  };

  return (
    <div className="flex flex-col h-full min-h-0">
      {/* Header */}
      <div className="flex items-center justify-between px-5 py-4 border-b border-border bg-card/50 flex-shrink-0">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg gradient-hero flex items-center justify-center">
            <Bot className="w-4 h-4 text-primary-foreground" />
          </div>
          <div>
            <h2 className="text-sm font-semibold text-foreground">Clinical Assistant</h2>
            <div className="flex items-center gap-1.5">
              <span className={`w-2 h-2 rounded-full ${isOnline ? 'bg-success animate-pulse-soft' : 'bg-destructive'}`} />
              <span className="text-xs text-muted-foreground uppercase">
                {isOnline ? `LIVE BACKEND ${backendVersion}` : "BACKEND OFFLINE"}
              </span>
            </div>
          </div>
        </div>
        <button
          onClick={handleClear}
          className="flex items-center gap-1.5 text-xs text-muted-foreground hover:text-destructive transition-colors px-3 py-1.5 rounded-lg hover:bg-destructive-light"
        >
          <Trash2 className="w-3.5 h-3.5" />
          Clear chat
        </button>
      </div>

      {/* Scrollable area */}
      <div
        ref={scrollRef}
        className="flex-1 min-h-0 overflow-y-auto px-4 py-4 space-y-4"
      >
        {/* Patient summary card (pinned when active) */}
        <AnimatePresence>
          {activePatient && (
            <PatientSummary
              key={activePatient.id}
              patient={activePatient}
              onClose={() => setActivePatient(null)}
            />
          )}
        </AnimatePresence>

        {/* Messages */}
        {messages.map((msg) => (
          <ChatMessage key={msg.id} message={msg} />
        ))}

        {/* Typing indicator */}
        <AnimatePresence>
          {isLoading && <TypingIndicator key="typing" />}
        </AnimatePresence>
      </div>

      {/* Input */}
      <div className="px-4 pb-4 pt-3 border-t border-border bg-card/30 flex-shrink-0">
        <ChatInput onSubmit={handleSubmit} isLoading={isLoading} />
      </div>
    </div>
  );
}
