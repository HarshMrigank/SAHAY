"use client";

import { useState } from 'react';
import Link from 'next/link';
import { ArrowLeft, AlertTriangle, Activity, BrainCircuit, ShieldAlert } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceArea } from 'recharts';

const trajectoryData = [
  { date: 'Aug 01', score: 32, note: 'Initial' },
  { date: 'Aug 15', score: 37, note: 'Stable' },
  { date: 'Aug 22', score: 44, note: 'Slight stress' },
  { date: 'Aug 29', score: 53, note: 'Missed check-in' },
  { date: 'Sep 05', score: 68, note: 'Sleep issues' },
  { date: 'Sep 07', score: 74, note: 'High fear reported' },
];

export default function CaseDetailPage({ params }: { params: { id: string } }) {
  const [activeTab, setActiveTab] = useState('overview');

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center text-sm text-slate-500 mb-2">
            <Link href="/district/cases" className="hover:text-slate-800 flex items-center">
              <ArrowLeft className="h-4 w-4 mr-1" /> Back to Cases
            </Link>
            <span className="mx-2">/</span>
            <span>Case Details</span>
          </div>
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-bold text-slate-900">{params.id}</h1>
            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-emerald-100 text-emerald-800">
              Active
            </span>
          </div>
        </div>
        
        <div className="flex gap-3">
          <button className="px-4 py-2 bg-white border border-slate-300 text-slate-700 rounded-lg hover:bg-slate-50 font-medium text-sm transition-colors">
            Add Note
          </button>
          <button className="px-4 py-2 bg-blue-700 text-white rounded-lg hover:bg-blue-800 font-medium text-sm transition-colors flex items-center">
            <ShieldAlert className="h-4 w-4 mr-2" /> Assign Intervention
          </button>
        </div>
      </div>

      {/* Top Status Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-rose-50 border border-rose-200 p-4 rounded-xl">
          <p className="text-sm font-medium text-rose-800 flex items-center"><AlertTriangle className="h-4 w-4 mr-1" /> Current Risk</p>
          <p className="text-2xl font-bold text-rose-700 mt-1">HIGH</p>
        </div>
        <div className="bg-white border border-slate-200 p-4 rounded-xl">
          <p className="text-sm font-medium text-slate-500">Distress Score</p>
          <div className="flex items-end gap-2 mt-1">
             <p className="text-2xl font-bold text-slate-900">74<span className="text-sm font-normal text-slate-500">/100</span></p>
             <p className="text-sm font-medium text-rose-600 mb-1">↑ +8.8%</p>
          </div>
        </div>
        <div className="bg-white border border-slate-200 p-4 rounded-xl">
          <p className="text-sm font-medium text-slate-500">Trend</p>
          <p className="text-xl font-bold text-slate-800 mt-1">Increasing</p>
        </div>
        <div className="bg-white border border-slate-200 p-4 rounded-xl">
          <p className="text-sm font-medium text-slate-500">Assigned Officer</p>
          <p className="text-lg font-medium text-slate-800 mt-1">Counsellor A</p>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-slate-200">
        <nav className="-mb-px flex space-x-8">
          {['overview', 'timeline', 'assessments', 'interventions'].map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm capitalize ${
                activeTab === tab
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-slate-500 hover:text-slate-700 hover:border-slate-300'
              }`}
            >
              {tab}
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Left Column (Main Charts/AI) */}
        <div className="lg:col-span-2 space-y-6">
          
          {/* Distress Trajectory Chart */}
          <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
            <h3 className="text-lg font-semibold text-slate-800 mb-1">Distress Trajectory</h3>
            <p className="text-sm text-slate-500 mb-6">Longitudinal view of wellbeing over time.</p>
            
            <div className="h-72">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={trajectoryData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                  <XAxis dataKey="date" axisLine={false} tickLine={false} tick={{fill: '#64748b', fontSize: 12}} />
                  <YAxis axisLine={false} tickLine={false} tick={{fill: '#64748b', fontSize: 12}} domain={[0, 100]} />
                  <Tooltip 
                    contentStyle={{borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)'}} 
                  />
                  <ReferenceArea y1={0} y2={40} fill="#10b981" fillOpacity={0.05} />
                  <ReferenceArea y1={40} y2={65} fill="#f59e0b" fillOpacity={0.05} />
                  <ReferenceArea y1={65} y2={85} fill="#f97316" fillOpacity={0.05} />
                  <ReferenceArea y1={85} y2={100} fill="#e11d48" fillOpacity={0.05} />
                  <Line 
                    type="monotone" 
                    dataKey="score" 
                    stroke="#0f172a" 
                    strokeWidth={3} 
                    dot={{r: 5, fill: '#0f172a', strokeWidth: 2, stroke: '#fff'}} 
                    activeDot={{r: 7, fill: '#3b82f6'}}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
            
            <div className="mt-4 flex justify-between text-xs text-slate-500">
               <div className="flex items-center"><span className="w-3 h-3 rounded-full bg-emerald-100 border border-emerald-300 mr-1.5"></span> Low (0-40)</div>
               <div className="flex items-center"><span className="w-3 h-3 rounded-full bg-amber-100 border border-amber-300 mr-1.5"></span> Moderate (41-65)</div>
               <div className="flex items-center"><span className="w-3 h-3 rounded-full bg-orange-100 border border-orange-300 mr-1.5"></span> High (66-85)</div>
               <div className="flex items-center"><span className="w-3 h-3 rounded-full bg-rose-100 border border-rose-300 mr-1.5"></span> Critical (86-100)</div>
            </div>
          </div>

          {/* AI Explainability Panel */}
          <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
             <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-slate-800 flex items-center">
                   <BrainCircuit className="h-5 w-5 mr-2 text-indigo-600" />
                   Explainable AI: Why this alert?
                </h3>
                <span className="text-xs bg-indigo-50 text-indigo-700 px-2.5 py-1 rounded-md font-medium border border-indigo-100">Prototype Analysis</span>
             </div>
             
             <p className="text-slate-700 font-medium mb-4">The latest interaction contains indicators of increased stress and fear compared with previous check-ins.</p>
             
             <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h4 className="text-sm font-semibold text-slate-500 uppercase tracking-wider mb-3">Contributing Indicators</h4>
                  <ul className="space-y-2">
                     <li className="flex items-start">
                        <span className="text-rose-500 mr-2 mt-0.5">+</span>
                        <span className="text-sm text-slate-700">Distress increased by 19% over the last two assessments</span>
                     </li>
                     <li className="flex items-start">
                        <span className="text-rose-500 mr-2 mt-0.5">+</span>
                        <span className="text-sm text-slate-700">Increased fear-related language</span>
                     </li>
                     <li className="flex items-start">
                        <span className="text-rose-500 mr-2 mt-0.5">+</span>
                        <span className="text-sm text-slate-700">Sleep difficulties reported consistently</span>
                     </li>
                  </ul>
                </div>
                <div>
                  <h4 className="text-sm font-semibold text-slate-500 uppercase tracking-wider mb-3">Protective Indicators</h4>
                  <ul className="space-y-2">
                     <li className="flex items-start">
                        <span className="text-emerald-500 mr-2 mt-0.5">-</span>
                        <span className="text-sm text-slate-700">Recent willingness to seek support</span>
                     </li>
                  </ul>
                </div>
             </div>
             
             <div className="mt-6 p-4 bg-slate-50 rounded-lg border border-slate-200">
                <h4 className="text-sm font-semibold text-slate-800 mb-1">Recommended Next Step</h4>
                <p className="text-sm text-slate-600">Priority human wellbeing assessment via phone call to verify safety and offer immediate counselling support.</p>
             </div>
          </div>
        </div>
        
        {/* Right Column (Timeline/Wellbeing details) */}
        <div className="space-y-6">
           
           {/* Prediction Card */}
           <div className="bg-gradient-to-br from-indigo-900 to-slate-900 p-6 rounded-xl border border-slate-800 shadow-md text-white">
              <h3 className="text-lg font-semibold mb-4 flex items-center">
                 <Activity className="h-5 w-5 mr-2 text-indigo-400" /> Future Distress Risk
              </h3>
              <div className="space-y-4">
                 <div className="flex justify-between items-center border-b border-white/10 pb-3">
                    <span className="text-slate-300 text-sm">7-day risk</span>
                    <span className="font-bold text-orange-400">HIGH</span>
                 </div>
                 <div className="flex justify-between items-center border-b border-white/10 pb-3">
                    <span className="text-slate-300 text-sm">30-day risk</span>
                    <span className="font-bold text-amber-400">MODERATE-HIGH</span>
                 </div>
                 <div className="flex justify-between items-center">
                    <span className="text-slate-300 text-sm">Prediction Confidence</span>
                    <span className="font-medium text-white">84%</span>
                 </div>
              </div>
              <div className="mt-4 pt-4 border-t border-white/10">
                 <p className="text-xs text-slate-400 italic">Predictions are decision-support indicators and require human review.</p>
              </div>
           </div>

           {/* Current Wellbeing Status */}
           <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
              <h3 className="text-lg font-semibold text-slate-800 mb-4">Reported Wellbeing</h3>
              
              <div className="space-y-4">
                 <div>
                    <div className="flex justify-between items-center mb-1">
                       <span className="text-sm font-medium text-slate-600">Fear</span>
                       <span className="text-sm font-medium text-rose-600">Elevated</span>
                    </div>
                    <div className="w-full bg-slate-100 rounded-full h-2">
                       <div className="bg-rose-500 h-2 rounded-full" style={{ width: '80%' }}></div>
                    </div>
                 </div>
                 <div>
                    <div className="flex justify-between items-center mb-1">
                       <span className="text-sm font-medium text-slate-600">Stress</span>
                       <span className="text-sm font-medium text-rose-600">Elevated</span>
                    </div>
                    <div className="w-full bg-slate-100 rounded-full h-2">
                       <div className="bg-rose-500 h-2 rounded-full" style={{ width: '75%' }}></div>
                    </div>
                 </div>
                 <div>
                    <div className="flex justify-between items-center mb-1">
                       <span className="text-sm font-medium text-slate-600">Sleep</span>
                       <span className="text-sm font-medium text-orange-600">Reduced</span>
                    </div>
                    <div className="w-full bg-slate-100 rounded-full h-2">
                       <div className="bg-orange-500 h-2 rounded-full" style={{ width: '60%' }}></div>
                    </div>
                 </div>
                 <div>
                    <div className="flex justify-between items-center mb-1">
                       <span className="text-sm font-medium text-slate-600">Daily Functioning</span>
                       <span className="text-sm font-medium text-amber-600">Moderately Affected</span>
                    </div>
                    <div className="w-full bg-slate-100 rounded-full h-2">
                       <div className="bg-amber-500 h-2 rounded-full" style={{ width: '50%' }}></div>
                    </div>
                 </div>
              </div>
           </div>
           
           {/* Brief Timeline */}
           <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
              <div className="flex justify-between items-center mb-4">
                 <h3 className="text-lg font-semibold text-slate-800">Recent Activity</h3>
                 <Link href="#" className="text-sm text-blue-600 font-medium">View All</Link>
              </div>
              <div className="relative border-l-2 border-slate-200 ml-3 space-y-6">
                 <div className="relative pl-6">
                    <span className="absolute -left-2.5 top-1 h-5 w-5 rounded-full bg-rose-100 border-2 border-rose-500 flex items-center justify-center"></span>
                    <p className="text-sm font-medium text-slate-800">Distress Increased (Alert)</p>
                    <p className="text-xs text-slate-500 mt-0.5">Today, 10:22 AM</p>
                 </div>
                 <div className="relative pl-6">
                    <span className="absolute -left-2.5 top-1 h-5 w-5 rounded-full bg-white border-2 border-slate-300 flex items-center justify-center"></span>
                    <p className="text-sm font-medium text-slate-800">Routine Check-in</p>
                    <p className="text-xs text-slate-500 mt-0.5">Today, 10:20 AM</p>
                 </div>
                 <div className="relative pl-6">
                    <span className="absolute -left-2.5 top-1 h-5 w-5 rounded-full bg-emerald-100 border-2 border-emerald-500 flex items-center justify-center"></span>
                    <p className="text-sm font-medium text-slate-800">Counselling Assigned</p>
                    <p className="text-xs text-slate-500 mt-0.5">Sep 05, 14:30 PM</p>
                 </div>
              </div>
           </div>

        </div>
      </div>
    </div>
  );
}
