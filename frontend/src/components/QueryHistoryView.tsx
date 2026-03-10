import { useState } from "react";
import { Clock, MessageSquare, Trash2, Search } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

interface QueryHistoryViewProps {
  history: string[];
  onClear: () => void;
  onSelectQuery: (q: string) => void;
}

export function QueryHistoryView({ history, onClear, onSelectQuery }: QueryHistoryViewProps) {
  const [filter, setFilter] = useState("");

  const filtered = history.filter((q) =>
    q.toLowerCase().includes(filter.toLowerCase())
  );

  return (
    <div className="p-5 space-y-4 h-full flex flex-col">
      <div className="flex items-center justify-between flex-shrink-0">
        <div>
          <h2 className="text-base font-semibold text-foreground">Query History</h2>
          <p className="text-xs text-muted-foreground">{history.length} queries in this session</p>
        </div>
        {history.length > 0 && (
          <button
            onClick={onClear}
            className="flex items-center gap-1.5 text-xs text-muted-foreground hover:text-destructive transition-colors px-3 py-1.5 rounded-lg hover:bg-destructive-light"
          >
            <Trash2 className="w-3.5 h-3.5" />
            Clear all
          </button>
        )}
      </div>

      {history.length > 0 && (
        <div className="relative flex-shrink-0">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-muted-foreground" />
          <input
            type="text"
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            placeholder="Filter history..."
            className="w-full pl-9 pr-3 py-2 bg-card border border-border rounded-lg text-xs text-foreground placeholder:text-muted-foreground outline-none focus:border-primary transition-all"
          />
        </div>
      )}

      <div className="flex-1 min-h-0 overflow-y-auto">
        {history.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-48 gap-3">
            <div className="w-12 h-12 rounded-full bg-muted flex items-center justify-center">
              <Clock className="w-6 h-6 text-muted-foreground" />
            </div>
            <div className="text-center">
              <p className="text-sm font-medium text-foreground">No queries yet</p>
              <p className="text-xs text-muted-foreground">Your search history will appear here</p>
            </div>
          </div>
        ) : (
          <div className="space-y-2">
            <AnimatePresence>
              {filtered.map((q, i) => (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.04 }}
                  className="flex items-start gap-3 p-3 bg-card border border-border rounded-xl hover:border-primary hover:shadow-card cursor-pointer group transition-all"
                  onClick={() => onSelectQuery(q)}
                >
                  <div className="w-7 h-7 rounded-lg bg-primary-light flex items-center justify-center flex-shrink-0 mt-0.5">
                    <MessageSquare className="w-3.5 h-3.5 text-primary" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm text-foreground group-hover:text-primary transition-colors leading-snug">{q}</p>
                    <p className="text-xs text-muted-foreground mt-1">
                      Query #{history.length - i}
                    </p>
                  </div>
                </motion.div>
              ))}
            </AnimatePresence>
          </div>
        )}
      </div>
    </div>
  );
}
