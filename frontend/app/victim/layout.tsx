"use client";

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Home, ClipboardCheck, Activity, Phone, HelpCircle, LogOut } from 'lucide-react';

export default function VictimLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  
  const navItems = [
    { name: 'Home', href: '/victim/dashboard', icon: Home },
    { name: 'Check-in', href: '/victim/check-in', icon: ClipboardCheck },
    { name: 'My Progress', href: '/victim/progress', icon: Activity },
    { name: 'Support', href: '/victim/support', icon: Phone },
    { name: 'Help', href: '/victim/help', icon: HelpCircle },
  ];

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      <header className="bg-white border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <span className="text-xl font-bold text-blue-800">SAHAY</span>
            </div>
            <div className="flex items-center">
              <Link href="/login" className="text-slate-500 hover:text-slate-700 flex items-center">
                <LogOut className="h-5 w-5 mr-1" />
                <span className="text-sm font-medium">Logout</span>
              </Link>
            </div>
          </div>
        </div>
      </header>

      <div className="flex-1 w-full flex flex-col md:flex-row gap-6 md:pl-64">
        {/* Main Content */}
        <main className="flex-1 p-4 sm:p-6 lg:p-8">
          {children}
        </main>
      </div>

      {/* Bottom Navigation for Mobile */}
      <div className="md:hidden fixed bottom-0 w-full bg-white border-t border-slate-200 pb-safe">
        <div className="flex justify-around items-center h-16">
          {navItems.map((item) => {
            const isActive = pathname === item.href;
            return (
              <Link key={item.name} href={item.href} className={`flex flex-col items-center p-2 ${isActive ? 'text-blue-700' : 'text-slate-500'}`}>
                <item.icon className="h-6 w-6" />
                <span className="text-xs mt-1">{item.name}</span>
              </Link>
            );
          })}
        </div>
      </div>
      
      {/* Sidebar for Desktop */}
      <div className="hidden md:block fixed top-16 left-0 w-64 h-full bg-white border-r border-slate-200 p-4">
         <nav className="space-y-2 mt-4">
           {navItems.map((item) => {
              const isActive = pathname === item.href;
              return (
                <Link key={item.name} href={item.href} className={`flex items-center p-3 rounded-lg ${isActive ? 'bg-blue-50 text-blue-700 font-medium' : 'text-slate-600 hover:bg-slate-50'}`}>
                  <item.icon className="h-5 w-5 mr-3" />
                  {item.name}
                </Link>
              );
           })}
         </nav>
      </div>
    </div>
  );
}
