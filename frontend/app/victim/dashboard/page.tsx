"use client";

import Link from 'next/link';
import { Calendar, PhoneCall, ShieldAlert, ArrowRight, Activity } from 'lucide-react';

export default function VictimDashboard() {
  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-200">
        <h1 className="text-2xl font-bold text-slate-800">Good morning</h1>
        <p className="text-slate-600 mt-1">Your wellbeing matters.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Next Check-in */}
        <div className="bg-blue-50 border border-blue-100 p-6 rounded-xl shadow-sm flex flex-col justify-between">
          <div>
            <div className="flex items-center text-blue-800 mb-4">
              <Calendar className="h-6 w-6 mr-2" />
              <h2 className="text-lg font-semibold">Next Check-in</h2>
            </div>
            <p className="text-slate-700">Scheduled for <span className="font-semibold text-slate-900">Today</span></p>
            <p className="text-sm text-slate-500 mt-1">Estimated duration: 2–3 minutes</p>
          </div>
          <div className="mt-6">
            <Link href="/victim/check-in" className="inline-flex w-full justify-center items-center px-4 py-2 bg-blue-700 text-white rounded-lg hover:bg-blue-800 font-medium transition-colors">
              Start Check-in
              <ArrowRight className="ml-2 h-4 w-4" />
            </Link>
          </div>
        </div>

        {/* Support Card */}
        <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-200 flex flex-col justify-between">
          <div>
            <div className="flex items-center text-rose-600 mb-4">
              <PhoneCall className="h-6 w-6 mr-2" />
              <h2 className="text-lg font-semibold text-slate-800">Need support now?</h2>
            </div>
            <p className="text-sm text-slate-600">You don&apos;t have to go through this alone. Professional support is available 24/7.</p>
          </div>
          <div className="mt-6 space-y-3">
            <button className="w-full text-center px-4 py-2 bg-rose-50 text-rose-700 rounded-lg hover:bg-rose-100 font-medium border border-rose-200 transition-colors">
              Talk to Counsellor
            </button>
            <button className="w-full text-center px-4 py-2 text-slate-700 rounded-lg hover:bg-slate-50 font-medium border border-slate-200 transition-colors">
              Emergency Help
            </button>
          </div>
        </div>
      </div>

      {/* Progress Section */}
      <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-200">
        <div className="flex items-center text-slate-800 mb-4">
          <Activity className="h-6 w-6 mr-2 text-emerald-600" />
          <h2 className="text-lg font-semibold">Your wellbeing journey</h2>
        </div>
        
        <div className="h-32 bg-slate-50 rounded-lg border border-slate-100 flex items-center justify-center p-4">
           {/* Simple mock trend indicator */}
           <p className="text-slate-600 text-center">
             Your recent responses suggest that additional support may be helpful. <br/>
             <Link href="/victim/support" className="text-blue-600 font-medium hover:underline mt-2 inline-block">View Support Services</Link>
           </p>
        </div>
      </div>

      {/* Persistent Emergency Button */}
      <div className="fixed bottom-20 md:bottom-8 right-4 md:right-8">
        <button className="bg-rose-600 text-white rounded-full p-4 shadow-lg flex items-center justify-center hover:bg-rose-700 transition-colors">
          <ShieldAlert className="h-6 w-6" />
        </button>
      </div>
    </div>
  );
}
