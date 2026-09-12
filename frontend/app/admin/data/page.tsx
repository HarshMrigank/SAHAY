"use client";

import { useState, useEffect } from 'react';
import { Users, FileText, CheckCircle, AlertTriangle, Database } from 'lucide-react';
import Link from 'next/link';

export default function AdminDataPage() {
  const [stats, setStats] = useState({
    users: 0,
    cases: 0,
    checkIns: 0,
    alerts: 0,
  });
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Simulate fetching from database
    setTimeout(() => {
      setStats({
        users: 1420,
        cases: 384,
        checkIns: 8900,
        alerts: 42,
      });
      setIsLoading(false);
    }, 800);
  }, []);

  return (
    <div className="min-h-screen bg-background">
      <header className="bg-card border-b border-border shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2 text-primary font-bold text-xl">
            <Database className="h-6 w-6" />
            <span>SAHAY Admin</span>
          </div>
          <nav className="flex items-center gap-4">
            <Link href="/" className="text-sm font-medium text-muted-foreground hover:text-foreground">Home</Link>
            <Link href="/admin/data" className="text-sm font-medium text-foreground">Data Statistics</Link>
          </nav>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-foreground">Database Statistics</h1>
          <p className="mt-2 text-muted-foreground">Overview of seeded system data and records.</p>
        </div>

        {isLoading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 animate-pulse">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="bg-card p-6 rounded-lg border border-border shadow-sm h-32"></div>
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="bg-card p-6 rounded-lg border border-border shadow-sm flex items-center gap-4">
              <div className="p-3 bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 rounded-full">
                <Users className="h-6 w-6" />
              </div>
              <div>
                <p className="text-sm font-medium text-muted-foreground">Total Users</p>
                <p className="text-2xl font-bold text-foreground">{stats.users.toLocaleString()}</p>
              </div>
            </div>

            <div className="bg-card p-6 rounded-lg border border-border shadow-sm flex items-center gap-4">
              <div className="p-3 bg-emerald-100 dark:bg-emerald-900/30 text-emerald-600 dark:text-emerald-400 rounded-full">
                <FileText className="h-6 w-6" />
              </div>
              <div>
                <p className="text-sm font-medium text-muted-foreground">Active Cases</p>
                <p className="text-2xl font-bold text-foreground">{stats.cases.toLocaleString()}</p>
              </div>
            </div>

            <div className="bg-card p-6 rounded-lg border border-border shadow-sm flex items-center gap-4">
              <div className="p-3 bg-purple-100 dark:bg-purple-900/30 text-purple-600 dark:text-purple-400 rounded-full">
                <CheckCircle className="h-6 w-6" />
              </div>
              <div>
                <p className="text-sm font-medium text-muted-foreground">Total Check-ins</p>
                <p className="text-2xl font-bold text-foreground">{stats.checkIns.toLocaleString()}</p>
              </div>
            </div>

            <div className="bg-card p-6 rounded-lg border border-border shadow-sm flex items-center gap-4">
              <div className="p-3 bg-red-100 dark:bg-red-900/30 text-red-600 dark:text-red-400 rounded-full">
                <AlertTriangle className="h-6 w-6" />
              </div>
              <div>
                <p className="text-sm font-medium text-muted-foreground">High Risk Alerts</p>
                <p className="text-2xl font-bold text-foreground">{stats.alerts.toLocaleString()}</p>
              </div>
            </div>
          </div>
        )}

        <div className="mt-12 bg-card border border-border rounded-lg overflow-hidden shadow-sm">
          <div className="px-6 py-4 border-b border-border bg-muted/30">
            <h3 className="text-lg font-medium text-foreground">Recent System Activity</h3>
          </div>
          <div className="divide-y divide-border">
            {[
              { id: 1, action: "New victim profile registered", time: "2 minutes ago", status: "Success" },
              { id: 2, action: "High priority alert dispatched to District Officer", time: "15 minutes ago", status: "Critical" },
              { id: 3, action: "Counselor completed assessment", time: "1 hour ago", status: "Success" },
              { id: 4, action: "System health check", time: "3 hours ago", status: "Success" },
              { id: 5, action: "Bulk data backup completed", time: "12 hours ago", status: "Info" },
            ].map((activity) => (
              <div key={activity.id} className="px-6 py-4 flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-foreground">{activity.action}</p>
                  <p className="text-xs text-muted-foreground mt-1">{activity.time}</p>
                </div>
                <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium
                  ${activity.status === 'Success' ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900/30 dark:text-emerald-400' : 
                    activity.status === 'Critical' ? 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400' : 
                    'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400'}`}>
                  {activity.status}
                </span>
              </div>
            ))}
          </div>
        </div>
      </main>
    </div>
  );
}
