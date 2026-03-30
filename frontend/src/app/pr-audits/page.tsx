"use client";

import { useEffect, useState } from "react";

interface PRAudit {
  id: number;
  title: string;
  url: string;
  status: string;
  timestamp: string;
}

export default function PRAuditHistoryPage() {
  const [history, setHistory] = useState<PRAudit[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Make sure this URL matches your actual local backend URL!
    fetch("http://127.0.0.1:8000/api/webhook/history")
      .then((res) => res.json())
      .then((data) => {
        setHistory(data.history);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Failed to fetch PR history", err);
        setLoading(false);
      });
  }, []);

  if (loading) return <div className="p-8 text-white">Loading ULTRA Telemetry...</div>;

  return (
    <div className="min-h-screen bg-gray-900 text-white p-8">
      <div className="max-w-6xl mx-auto">
        <h1 className="text-3xl font-bold mb-2">Autonomous PR Audits</h1>
        <p className="text-gray-400 mb-8">Live telemetry of all GitHub Pull Requests verified by CodeOps ULTRA.</p>

        <div className="bg-gray-800 rounded-lg overflow-hidden border border-gray-700">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-gray-900 border-b border-gray-700">
                <th className="p-4 font-semibold text-gray-300">Pull Request Title</th>
                <th className="p-4 font-semibold text-gray-300">Status</th>
                <th className="p-4 font-semibold text-gray-300">Timestamp</th>
                <th className="p-4 font-semibold text-gray-300">Action</th>
              </tr>
            </thead>
            <tbody>
              {history.length === 0 ? (
                <tr>
                  <td colSpan={4} className="p-4 text-center text-gray-500">No PRs audited yet.</td>
                </tr>
              ) : (
                history.map((audit) => (
                  <tr key={audit.id} className="border-b border-gray-700 hover:bg-gray-750 transition">
                    <td className="p-4 font-medium">{audit.title}</td>
                    <td className="p-4">
                      <span className="bg-green-500/10 text-green-400 px-3 py-1 rounded-full text-sm border border-green-500/20">
                        {audit.status}
                      </span>
                    </td>
                    <td className="p-4 text-gray-400">
                      {new Date(audit.timestamp).toLocaleString()}
                    </td>
                    <td className="p-4">
                      <a 
                        href={audit.url} 
                        target="_blank" 
                        rel="noreferrer"
                        className="text-blue-400 hover:text-blue-300 transition text-sm font-medium"
                      >
                        View on GitHub ↗
                      </a>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}