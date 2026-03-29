// frontend/src/app/assistant/page.tsx
"use client";

import React, { useState, useEffect } from "react";
import axios from "axios";
import Link from "next/link";
import { 
  Bot, 
  Code2, 
  Loader2, 
  ShieldAlert, 
  Terminal,
  ArrowRightLeft,
  History as HistoryIcon,
  Clock,
  X
} from "lucide-react";
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';

// Define the interface for our History Items
interface ReviewHistoryItem {
  id: number;
  original_code: string;
  analysis: string;
  timestamp: string;
}

export default function StandaloneAssistant() {
  const [inputCode, setInputCode] = useState("# Paste your raw script here for Enterprise Review...\n");
  const [outputData, setOutputData] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // --- NEW: History State ---
  const [history, setHistory] = useState<ReviewHistoryItem[]>([]);
  const [showHistory, setShowHistory] = useState(false);

  // Fetch history when the component loads
  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    try {
      const res = await axios.get("/api/v2/history");
      if (!res.data.error) setHistory(res.data);
    } catch { 
      console.error("History fetch failed. Ensure backend is updated."); 
    }
  };

  const triggerReview = async () => {
    if (!inputCode) return;
    setIsLoading(true);
    setError(null);
    setOutputData("# Analyzing Abstract Syntax Tree and searching for vulnerabilities...");

    try {
      const res = await axios.post("/api/v2/agent/review", { 
        code: inputCode,
        language: "auto-detect" 
      });
      
      if (res.data.error) {
        setError(res.data.error);
        setOutputData(null);
      } else {
        setOutputData(res.data.ai_analysis);
        fetchHistory(); // <-- NEW: Refresh the history drawer after a successful review!
      }
    } catch (err) {
      if (axios.isAxiosError(err)) {
        setError(err.message || "Failed to connect to Cognitive Core.");
      } else if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("An unknown cognitive core error occurred.");
      }
      setOutputData(null);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-950 text-gray-100 p-6 font-sans flex flex-col">
      <header className="flex items-center justify-between border-b border-gray-800 pb-4 mb-6">
        <div className="flex items-center gap-3">
          <Bot className="w-8 h-8 text-violet-500" />
          <div className="flex items-baseline gap-2">
            <h1 className="text-2xl font-bold tracking-tighter text-transparent bg-clip-text bg-gradient-to-r from-violet-400 to-fuchsia-500">
              ULTRA Code Assistant
            </h1>
            <span className="px-1.5 py-0.5 rounded border border-violet-500/30 bg-violet-500/10 text-[10px] font-bold text-violet-400 uppercase tracking-widest">
              Standalone Agent
            </span>
          </div>
        </div>
        
        {/* NEW: Added Review History Button next to the Mission Control Link */}
        <div className="flex items-center gap-3">
          <button 
            onClick={() => setShowHistory(!showHistory)} 
            className="flex items-center gap-2 px-4 py-2 rounded-lg bg-gray-900 border border-gray-700 hover:border-violet-500 transition-all text-sm"
          >
            <HistoryIcon className="w-4 h-4" /> Review History
          </button>
          <Link href="/" className="px-4 py-2 rounded-lg bg-gray-900 border border-gray-700 hover:border-cyan-500 transition-all text-sm flex items-center gap-2">
            <Terminal className="w-4 h-4" /> Mission Control
          </Link>
        </div>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 flex-1 h-[80vh] relative">
        
        {/* --- NEW: History Slide-out Drawer --- */}
        {showHistory && (
          <div className="absolute right-0 top-0 bottom-0 w-80 bg-gray-900 border-l border-gray-800 z-50 p-4 shadow-2xl overflow-y-auto animate-in slide-in-from-right">
            <div className="flex justify-between items-center mb-6">
              <h3 className="font-bold flex items-center gap-2 text-violet-300">
                <Clock className="w-4 h-4 text-violet-500" /> Past Reviews
              </h3>
              <button onClick={() => setShowHistory(false)}>
                <X className="w-5 h-5 text-gray-500 hover:text-white transition-colors" />
              </button>
            </div>
            <div className="space-y-4">
              {history.length === 0 && <p className="text-gray-500 text-sm">No history found.</p>}
              {history.map((item) => (
                <div 
                  key={item.id} 
                  onClick={() => { 
                    // When clicked, load the AI's old answer into the right panel!
                    setOutputData(item.analysis); 
                    setShowHistory(false); 
                  }} 
                  className="p-3 bg-gray-950 border border-gray-800 rounded-lg cursor-pointer hover:border-violet-500 transition-all group"
                >
                  <p className="text-xs text-violet-400 mb-1 truncate font-mono">
                    {new Date(item.timestamp).toLocaleString()}
                  </p>
                  <p className="text-sm font-medium line-clamp-2 text-gray-400 font-mono text-[10px] group-hover:text-gray-200">
                    {item.original_code}
                  </p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* LEFT PANEL: The Colorful Editable Overlay Workspace */}
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-4 flex flex-col shadow-2xl relative group">
          <h2 className="text-xs font-bold text-gray-500 uppercase mb-3 flex items-center gap-2">
            <Code2 className="w-4 h-4 text-cyan-400" /> Draft Code
          </h2>
          
          <div className="relative flex-1 w-full bg-[#1e1e1e] border border-gray-700 rounded-lg overflow-hidden group-focus-within:border-violet-500 transition-colors">
            
            {/* The Glowing Background (Syntax Highlighter) */}
            <SyntaxHighlighter
              language="python"
              style={vscDarkPlus}
              customStyle={{
                position: 'absolute',
                top: 0, left: 0, right: 0, bottom: 0,
                background: 'transparent',
                margin: 0,
                padding: '1rem',
                fontSize: '0.875rem',
                lineHeight: '1.5',
                fontFamily: 'monospace',
                pointerEvents: 'none',
              }}
            >
              {inputCode + '\n'}
            </SyntaxHighlighter>
            
            {/* The Invisible Typing Layer (Textarea) */}
            <textarea
              value={inputCode}
              onChange={(e) => setInputCode(e.target.value)}
              spellCheck={false}
              className="absolute inset-0 w-full h-full bg-transparent text-transparent caret-white resize-none outline-none scrollbar-hide"
              style={{
                padding: '1rem',
                fontSize: '0.875rem',
                lineHeight: '1.5',
                fontFamily: 'monospace',
              }}
            />
          </div>

          <button
            onClick={triggerReview}
            disabled={isLoading || !inputCode}
            className="mt-4 w-full bg-violet-600 hover:bg-violet-500 text-white font-bold py-3 rounded-lg flex items-center justify-center gap-2 transition-all disabled:opacity-50"
          >
            {isLoading ? <Loader2 className="w-5 h-5 animate-spin" /> : <ArrowRightLeft className="w-5 h-5" />}
            {isLoading ? "Executing Deep Audit..." : "Initiate AI Code Review"}
          </button>
        </div>

        {/* RIGHT PANEL: AI Output */}
        <div className="bg-[#1e1e1e] border border-gray-800 rounded-xl overflow-hidden flex flex-col shadow-2xl relative">
          <div className="bg-gray-900 border-b border-gray-800 p-3 px-4 flex items-center gap-2 z-10">
            <ShieldAlert className="w-4 h-4 text-emerald-400" /> 
            <span className="text-xs font-bold text-gray-500 uppercase">ULTRA Verified Optimization</span>
          </div>
          <div className="flex-1 bg-[#1e1e1e] overflow-auto scrollbar-hide relative">
            {error && (
              <div className="p-4 text-red-400 font-bold flex items-center gap-2">
                ❌ {error}
              </div>
            )}
            
            {!error && outputData && (
              <SyntaxHighlighter 
                language="python" 
                style={vscDarkPlus}
                customStyle={{ background: 'transparent', margin: 0, padding: '1rem', fontSize: '0.875rem', height: '100%' }}
              >
                {outputData}
              </SyntaxHighlighter>
            )}

            {!error && !outputData && (
              <div className="p-4 text-gray-600 font-mono text-sm">Awaiting code submission...</div>
            )}
          </div>
        </div>

      </div>
    </div>
  );
}