import { useState, useRef, FormEvent } from "react";
import { Send, Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";

interface ChatInputProps {
  onSubmit: (query: string) => void;
  isLoading: boolean;
}

const suggestions = [
  "How many diabetic patients are there?",
  "What is the average age of female patients?",
  "Which patients have HbA1c above 8?",
  "Count patients grouped by gender",
];

export function ChatInput({ onSubmit, isLoading }: ChatInputProps) {
  const [value, setValue] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleSubmit = (e?: FormEvent) => {
    e?.preventDefault();
    if (!value.trim() || isLoading) return;
    onSubmit(value.trim());
    setValue("");
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handleInput = () => {
    const el = textareaRef.current;
    if (!el) return;
    el.style.height = "auto";
    el.style.height = Math.min(el.scrollHeight, 160) + "px";
  };

  return (
    <div className="space-y-3">
      {/* Suggestion chips */}
      <div className="flex flex-wrap gap-2">
        {suggestions.map((s) => (
          <button
            key={s}
            onClick={() => {
              setValue(s);
              textareaRef.current?.focus();
            }}
            className="text-xs px-3 py-1.5 rounded-full bg-primary-light text-primary border border-primary-muted hover:bg-primary-muted transition-colors truncate max-w-[200px]"
          >
            {s}
          </button>
        ))}
      </div>

      {/* Input box */}
      <form onSubmit={handleSubmit} className="relative">
        <div
          className={cn(
            "flex items-end gap-3 bg-card border rounded-2xl px-4 py-3 shadow-card transition-all duration-150",
            "focus-within:border-primary focus-within:shadow-elevated"
          )}
        >
          <textarea
            ref={textareaRef}
            value={value}
            onChange={(e) => setValue(e.target.value)}
            onKeyDown={handleKeyDown}
            onInput={handleInput}
            rows={1}
            placeholder="Ask about a patient, medication, lab results..."
            className="flex-1 resize-none bg-transparent text-sm text-foreground placeholder:text-muted-foreground outline-none leading-relaxed min-h-[24px] max-h-[160px]"
            disabled={isLoading}
          />
          <button
            type="submit"
            disabled={!value.trim() || isLoading}
            className={cn(
              "w-9 h-9 rounded-xl flex items-center justify-center flex-shrink-0 transition-all",
              value.trim() && !isLoading
                ? "gradient-hero shadow-sm hover:opacity-90 active:scale-95"
                : "bg-muted cursor-not-allowed"
            )}
          >
            {isLoading ? (
              <Loader2 className="w-4 h-4 animate-spin text-muted-foreground" />
            ) : (
              <Send
                className={cn(
                  "w-4 h-4",
                  value.trim() ? "text-primary-foreground" : "text-muted-foreground"
                )}
              />
            )}
          </button>
        </div>
        <p className="text-xs text-muted-foreground text-center mt-2">
          Press Enter to send · Shift+Enter for new line
        </p>
      </form>
    </div>
  );
}
