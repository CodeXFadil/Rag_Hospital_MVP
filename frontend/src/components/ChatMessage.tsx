import { cn } from "@/lib/utils";
import { motion } from "framer-motion";
import { Bot, User, Copy, CheckCheck, ChevronDown, ChevronUp, Search } from "lucide-react";
import { useState } from "react";
import ReactMarkdown from "react-markdown";

export interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
  debug?: string;
}

interface ChatMessageProps {
  message: Message;
}

export function ChatMessage({ message }: ChatMessageProps) {
  const [copied, setCopied] = useState(false);
  const isUser = message.role === "user";

  const handleCopy = async () => {
    await navigator.clipboard.writeText(message.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25, ease: "easeOut" }}
      className={cn(
        "flex gap-3 group",
        isUser ? "flex-row-reverse" : "flex-row"
      )}
    >
      {/* Avatar */}
      <div
        className={cn(
          "w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5",
          isUser
            ? "gradient-hero"
            : "bg-primary-light border border-primary-muted"
        )}
      >
        {isUser ? (
          <User className="w-4 h-4 text-primary-foreground" />
        ) : (
          <Bot className="w-4 h-4 text-primary" />
        )}
      </div>

      {/* Bubble */}
      <div className={cn("flex-1 min-w-0", isUser ? "flex justify-end" : "")}>
        <div
          className={cn(
            "relative rounded-2xl px-4 py-3 max-w-[85%] text-sm leading-relaxed",
            isUser
              ? "bg-chat-user text-chat-user-foreground rounded-tr-sm shadow-chat"
              : "bg-chat-ai text-chat-ai-foreground border border-chat-ai-border rounded-tl-sm shadow-card"
          )}
        >
          {isUser ? (
            <p className="whitespace-pre-wrap">{message.content}</p>
          ) : (
            <>
              <div className="prose prose-sm max-w-none prose-headings:text-foreground prose-headings:font-semibold prose-p:text-foreground prose-strong:text-foreground prose-li:text-foreground prose-code:text-primary prose-code:bg-primary-light prose-code:px-1 prose-code:rounded prose-h2:text-base prose-h3:text-sm prose-h2:mt-4 prose-h3:mt-3">
                <ReactMarkdown>{message.content}</ReactMarkdown>
              </div>

              {message.debug && (
                <div className="mt-4 border-t border-border/50 pt-3">
                  <details className="group/debug">
                    <summary className="flex items-center gap-2 text-[10px] uppercase tracking-wider font-bold text-muted-foreground hover:text-primary cursor-pointer list-none">
                      <Search className="w-3 h-3" />
                      <span>Debug — Clinical Reasoning Engine</span>
                      <ChevronDown className="w-3 h-3 ml-auto group-open/debug:rotate-180 transition-transform" />
                    </summary>
                    <div className="mt-2 p-2 bg-black/5 rounded border border-border/30 text-[11px] font-mono whitespace-pre-wrap overflow-x-auto max-h-[300px]">
                      {message.debug}
                    </div>
                  </details>
                </div>
              )}
            </>
          )}

          {/* Timestamp + copy button */}
          <div
            className={cn(
              "flex items-center gap-2 mt-2 pt-1 border-t",
              isUser
                ? "border-primary-foreground/10 justify-start"
                : "border-border justify-between"
            )}
          >
            <span
              className={cn(
                "text-xs",
                isUser ? "text-primary-foreground/60" : "text-muted-foreground"
              )}
            >
              {formatTime(message.timestamp)}
            </span>
            {!isUser && (
              <button
                onClick={handleCopy}
                className="opacity-0 group-hover:opacity-100 transition-opacity flex items-center gap-1 text-xs text-muted-foreground hover:text-primary"
              >
                {copied ? (
                  <>
                    <CheckCheck className="w-3 h-3 text-success" />
                    <span className="text-success">Copied</span>
                  </>
                ) : (
                  <>
                    <Copy className="w-3 h-3" />
                    <span>Copy</span>
                  </>
                )}
              </button>
            )}
          </div>
        </div>
      </div>
    </motion.div>
  );
}

export function TypingIndicator() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: 10 }}
      className="flex gap-3"
    >
      <div className="w-8 h-8 rounded-full bg-primary-light border border-primary-muted flex items-center justify-center flex-shrink-0">
        <Bot className="w-4 h-4 text-primary" />
      </div>
      <div className="bg-chat-ai border border-chat-ai-border rounded-2xl rounded-tl-sm px-4 py-3 shadow-card">
        <div className="flex items-center gap-1.5">
          {[0, 1, 2].map((i) => (
            <div
              key={i}
              className="w-2 h-2 rounded-full bg-primary/40 animate-[typing-dot_1.2s_ease-in-out_infinite]"
              style={{ animationDelay: `${i * 0.2}s` }}
            />
          ))}
          <span className="text-xs text-muted-foreground ml-1">AI is analyzing...</span>
        </div>
      </div>
    </motion.div>
  );
}

function formatTime(date: Date) {
  return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}
