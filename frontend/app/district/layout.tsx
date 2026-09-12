"use client";

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { LayoutDashboard, Users, AlertTriangle, Activity, BriefcaseMedical, BarChart2, FileText, BookOpen, LogOut } from 'lucide-react';

export default function DistrictLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  
  const navItems = [
    { name: 'Overview', href: '/district/dashboard', icon: LayoutDashboard },
    { name: 'Cases', href: '/district/cases', icon: Users },
    { name: 'Alerts', href: '/district/alerts', icon: AlertTriangle },
    { name: 'Assessments', href: '/district/assessments', icon: Activity },
    { name: 'Distress Trends', href: '/district/trends', icon: BarChart2 },
    { name: 'Interventions', href: '/district/interventions', icon: BriefcaseMedical },
    { name: 'Reports', href: '/district/reports', icon: FileText },
    { name: 'Resources', href: '/district/resources', icon: BookOpen },
  ];

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col md:flex-row">
      {/* Sidebar for Desktop */}
      <aside className="hidden md:flex flex-col w-64 bg-slate-900 text-white min-h-screen fixed left-0 top-0">
        <div className="p-6 border-b border-slate-800">
          <h1 className="text-2xl font-bold tracking-tight text-white">SAHAY</h1>
          <p className="text-xs text-slate-400 mt-1">Dynamic Support Platform</p>
        </div>
        
        <div className="flex-1 overflow-y-auto py-4 px-3 space-y-1">
          {navItems.map((item) => {
            const isActive = pathname.startsWith(item.href);
            return (
              <Link 
                key={item.name} 
                href={item.href} 
                className={`flex items-center px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                  isActive ? 'bg-blue-600 text-white' : 'text-slate-300 hover:bg-slate-800 hover:text-white'
                }`}
              >
                <item.icon className={`h-5 w-5 mr-3 ${isActive ? 'text-white' : 'text-slate-400'}`} />
                {item.name}
              </Link>
            );
          })}
        </div>
        
        <div className="p-4 border-t border-slate-800">
           <Link href="/login" className="flex items-center px-3 py-2.5 rounded-lg text-sm font-medium text-slate-300 hover:bg-slate-800 hover:text-white transition-colors">
              <LogOut className="h-5 w-5 mr-3 text-slate-400" />
              Logout
           </Link>
        </div>
      </aside>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col md:pl-64">
        <header className="bg-white border-b border-slate-200 h-16 flex items-center px-6 justify-between md:justify-end">
          <div className="md:hidden flex items-center">
            <h1 className="text-xl font-bold text-slate-900">SAHAY</h1>
          </div>
          <div className="flex items-center space-x-4">
            <span className="text-sm font-medium text-slate-700">District Officer Demo</span>
            <div className="h-8 w-8 rounded-full bg-slate-200 flex items-center justify-center text-slate-600 font-bold">
              DO
            </div>
          </div>
        </header>

        <main className="flex-1 p-6 overflow-auto">
          {children}
        </main>
      </div>
    </div>
  );
}
