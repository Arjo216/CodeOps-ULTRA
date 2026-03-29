// frontend/src/app/page.tsx
"use client";

import React, { useState, useEffect, useRef } from "react";
import axios from "axios";
import Link from "next/link";
import { 
  Play, 
  TerminalSquare, 
  Code2, 
  Loader2, 
  ShieldCheck, 
  FileSpreadsheet, 
  X, 
  History as HistoryIcon, 
  Clock,
  Bot
} from "lucide-react";
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';

interface HistoryItem {
  id: number;
  task: string;
  code: string;
  logs: string[];
  timestamp: string;
}

export default function MissionControl() {
  const [mounted, setMounted] = useState(false);
  const [task, setTask] = useState("");
  const [code, setCode] = useState("# Your AI-verified code will appear here...");
  const [logs, setLogs] = useState<string[]>(["System initialized. Ready..."]);
  const [isLoading, setIsLoading] = useState(false);
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [showHistory, setShowHistory] = useState(false);
  
  const [dataset, setDataset] = useState<string | null>(null);
  const [language, setLanguage] = useState("python"); // <-- NEW Polyglot State
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    setMounted(true);
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    try {
      const res = await axios.get("/api/history");
      if (!res.data.error) setHistory(res.data);
    } catch { 
      console.error("History fetch failed"); 
    }
  };

  const handleCsvUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setDataset(reader.result as string);
      };
      reader.readAsText(file);
    }
  };

  const runAgent = async () => {
    if (!task && !dataset) return;
    setIsLoading(true);
    setCode(`# Agent is auditing and verifying ${language} code...`);
    setLogs([`Starting CodeOps ULTRA Agent [Runtime: ${language}]...`]);

    try {
      // Send the language preference to the backend!
      const response = await axios.post("/api/solve", { task, dataset, language });
      setCode(response.data.code);
      setLogs((prev) => [...prev, ...response.data.logs, `Success in ${response.data.attempts} attempts.`]);
      fetchHistory(); 
    } catch (error) {
      const errorMsg = axios.isAxiosError(error) ? error.message : "Unknown error";
      setLogs((prev) => [...prev, "❌ API Error: " + errorMsg]);
      setCode("# Execution Failed. Check logs.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-950 text-gray-100 p-6 font-sans">
      <header className="flex items-center justify-between border-b border-gray-800 pb-4 mb-6">
        <div className="flex items-center gap-3">
          <ShieldCheck className="w-8 h-8 text-cyan-400" />
          <div className="flex items-baseline gap-2">
            <h1 className="text-2xl font-bold tracking-tighter text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-500">
              CodeOps ULTRA
            </h1>
            <span className="px-1.5 py-0.5 rounded border border-cyan-500/30 bg-cyan-500/10 text-[10px] font-bold text-cyan-400 uppercase tracking-widest">
              Enterprise Edition
            </span>
          </div>
        </div>
        
        <div className="flex items-center gap-3">
          <Link href="/assistant" className="flex items-center gap-2 px-4 py-2 rounded-lg bg-violet-900/20 border border-violet-700/50 hover:border-violet-400 transition-all text-sm text-violet-300">
            <Bot className="w-4 h-4" /> ULTRA Assistant
          </Link>
          <button 
            onClick={() => setShowHistory(!showHistory)}
            className="flex items-center gap-2 px-4 py-2 rounded-lg bg-gray-900 border border-gray-700 hover:border-cyan-500 transition-all text-sm"
          >
            <HistoryIcon className="w-4 h-4" /> Audit History
          </button>
        </div>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 h-[80vh] relative">
        {showHistory && (
          <div className="absolute right-0 top-0 bottom-0 w-80 bg-gray-900 border-l border-gray-800 z-50 p-4 shadow-2xl overflow-y-auto animate-in slide-in-from-right">
            <div className="flex justify-between items-center mb-6">
              <h3 className="font-bold flex items-center gap-2"><Clock className="w-4 h-4" /> Past Audits</h3>
              <button onClick={() => setShowHistory(false)}><X className="w-5 h-5 text-gray-500 hover:text-white" /></button>
            </div>
            <div className="space-y-4">
              {history.length === 0 && <p className="text-gray-500 text-sm">No history found.</p>}
              {history.map((item) => (
                <div 
                  key={item.id} 
                  onClick={() => { setCode(item.code); setLogs(item.logs); setShowHistory(false); }}
                  className="p-3 bg-gray-950 border border-gray-800 rounded-lg cursor-pointer hover:border-cyan-500 transition-all"
                >
                  <p className="text-xs text-cyan-400 mb-1 truncate font-mono">{new Date(item.timestamp).toLocaleString()}</p>
                  <p className="text-sm font-medium line-clamp-2 text-gray-300">{item.task}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        <div className="lg:col-span-4 flex flex-col gap-6">
          <div className="bg-gray-900 border border-gray-800 rounded-xl p-4 flex flex-col">
            <h2 className="text-xs font-bold text-gray-500 uppercase mb-3 flex items-center gap-2">
              <TerminalSquare className="w-4 h-4" /> Agent Directive
            </h2>
            <textarea
              className="w-full bg-gray-950 border border-gray-700 rounded-lg p-3 text-sm focus:outline-none focus:border-cyan-500 transition-colors resize-none mb-3"
              rows={4}
              placeholder={`e.g., Write a ${language === 'python' ? 'web scraper' : 'REST API'}...`}
              value={task}
              onChange={(e) => setTask(e.target.value)}
            />
            
            {/* NEW: Polyglot Language Selector */}
            <div className="flex items-center gap-2 mb-3">
              <span className="text-xs font-bold text-gray-500 uppercase">Runtime:</span>
              <select 
                value={language}
                onChange={(e) => setLanguage(e.target.value)}
                className="flex-1 bg-gray-950 border border-gray-700 text-gray-300 text-sm rounded-lg p-2 focus:outline-none focus:border-cyan-500"
              >
                <option value="python">🐍 Python 3.11</option>
                <option value="javascript">⚡ Node.js (JavaScript)</option>
                <option value="c">🛠️ C (GCC)</option>
                <option value="cpp">⚙️ C++ (GCC)</option>
                <option value="rust">🦀 Rust</option>
                <option value="go">🐹 Go</option>
                <option value="java">☕ Java 21</option>
              </select>
            </div>

            <input type="file" accept=".csv" ref={fileInputRef} className="hidden" onChange={handleCsvUpload} />
            <button 
              onClick={() => dataset ? setDataset(null) : fileInputRef.current?.click()}
              className={`w-full mb-3 py-2.5 rounded-lg text-sm flex items-center justify-center gap-2 border border-dashed transition-all ${dataset ? 'border-red-500/50 text-red-400' : 'border-gray-700 text-gray-400 hover:border-cyan-500'}`}
            >
              <FileSpreadsheet className="w-4 h-4" /> {dataset ? "Remove Dataset" : "Attach CSV"}
            </button>

            <button
              onClick={runAgent}
              disabled={isLoading || (!task && !dataset)}
              className="w-full bg-cyan-600 hover:bg-cyan-500 text-white font-bold py-3 rounded-lg flex items-center justify-center gap-2 transition-all disabled:opacity-50"
            >
              {isLoading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Play className="w-5 h-5" />}
              {isLoading ? "Auditing..." : "Deploy Agent"}
            </button>
          </div>

          <div className="bg-black border border-gray-800 rounded-xl p-4 flex-1 flex flex-col overflow-hidden">
            <h2 className="text-xs font-bold text-gray-500 uppercase mb-3 flex items-center gap-2">
              <Code2 className="w-4 h-4" /> Live Telemetry
            </h2>
            <div className="flex-1 bg-gray-950 p-3 font-mono text-[10px] overflow-y-auto rounded-lg">
              {logs.map((log, idx) => (
                <div key={idx} className="mb-1">
                  <span className="text-gray-700">[{mounted ? new Date().toLocaleTimeString() : "00:00"}]</span>{" "}
                  <span className={log.includes("Success") ? "text-green-400" : log.includes("Error") || log.includes("❌") ? "text-red-400" : "text-cyan-400"}>{log}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="lg:col-span-8 bg-[#1e1e1e] border border-gray-800 rounded-xl overflow-hidden flex flex-col relative">
          <div className="bg-gray-900 border-b border-gray-800 p-2 px-4 flex items-center justify-between z-10 relative">
            {/* Dynamically update the extension! */}
            <span className="text-[10px] font-mono text-gray-500">
              verified_solution.{language === 'javascript' ? 'js' : 'py'}
            </span>
            <div className="flex gap-1">
              <div className="w-2 h-2 rounded-full bg-red-500/50"></div>
              <div className="w-2 h-2 rounded-full bg-yellow-500/50"></div>
              <div className="w-2 h-2 rounded-full bg-green-500/50"></div>
            </div>
          </div>
          
          <div className="flex-1 bg-[#1e1e1e] overflow-auto scrollbar-hide">
            <SyntaxHighlighter 
              language={language === 'javascript' ? 'javascript' : 'python'} 
              style={vscDarkPlus}
              customStyle={{ background: 'transparent', margin: 0, padding: '1rem', fontSize: '0.875rem', height: '100%' }}
            >
              {code}
            </SyntaxHighlighter>

            {(!code.includes("Your AI-verified code") && !code.includes("Agent is auditing") && !code.includes("Execution Failed")) && (
              <div className="absolute top-12 right-6 px-2 py-1 bg-green-500/10 border border-green-500/30 rounded text-[10px] text-green-400 font-bold uppercase tracking-widest pointer-events-none">
                Verified Safe
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}