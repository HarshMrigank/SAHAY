"use client";

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { ArrowLeft, AlertTriangle, Activity, BrainCircuit, ShieldAlert } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceArea } from 'recharts';

export default function CaseDetailPage({ params }: { params: { id: string } }) {
  const [activeTab, setActiveTab] = useState('overview');
  const [caseData, setCaseData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchCase = async () => {
      try {
        const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/district/cases/${params.id}`);
        if (res.ok) {
          const data = await res.json();
          setCaseData(data);
        }
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchCase();
  }, [params.id]);

  if (loading) return <div className="p-8">Loading case details...</div>;
  if (!caseData) return <div className="p-8">Case not found or failed to load.</div>;

  const { trajectoryData, metrics, aiExplainability } = caseData;

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center text-sm text-slate-500 mb-2">
            <Link href="/district/dashboard" className="hover:text-slate-800 flex items-center">
              <ArrowLeft className="h-4 w-4 mr-1" /> Back to Dashboard
            </Link>
            <span className="mx-2">/</span>
            <span>Case Details</span>
          </div>
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-bold text-slate-900">{params.id}</h1>
            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-emerald-100 text-emerald-800">
              {caseData.status || 'Active'}
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
          <p className="text-2xl font-bold text-rose-700 mt-1">{metrics?.riskLevel || 'HIGH'}</p>
        </div>
        <div className="bg-white border border-slate-200 p-4 rounded-xl">
          <p className="text-sm font-medium text-slate-500">Distress Score</p>
          <div className="flex items-end gap-2 mt-1">
             <p className="text-2xl font-bold text-slate-900">{metrics?.distressScore || 0}<span className="text-sm font-normal text-slate-500">/100</span></p>
             <p className="text-sm font-medium text-rose-600 mb-1">{metrics?.distressTrend || ''}</p>
          </div>
        </div>
        <div className="bg-white border border-slate-200 p-4 rounded-xl">
          <p className="text-sm font-medium text-slate-500">Trend</p>
          <p className="text-xl font-bold text-slate-800 mt-1">{metrics?.trendText || 'Increasing'}</p>
        </div>
        <div className="bg-white border border-slate-200 p-4 rounded-xl">
          <p className="text-sm font-medium text-slate-500">Assigned Officer</p>
          <p className="text-lg font-medium text-slate-800 mt-1">{caseData.assignedOfficer || 'Unassigned'}</p>
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
                <LineChart data={trajectoryData || []} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
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
             
             <p className="text-slate-700 font-medium mb-4">{aiExplainability?.summary || 'Analysis derived from recent check-ins.'}</p>
             
             <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h4 className="text-sm font-semibold text-slate-500 uppercase tracking-wider mb-3">Contributing Indicators</h4>
                  <ul className="space-y-2">
                     {(aiExplainability?.contributing || []).map((ind: string, idx: number) => (
                       <li key={idx} className="flex items-start">
                         <span className="text-rose-500 mr-2 mt-0.5">+</span>
                         <span className="text-sm text-slate-700">{ind}</span>
                       </li>
                     ))}
                  </ul>
                </div>
                <div>
                  <h4 className="text-sm font-semibold text-slate-500 uppercase tracking-wider mb-3">Protective Indicators</h4>
                  <ul className="space-y-2">
                     {(aiExplainability?.protective || []).map((ind: string, idx: number) => (
                       <li key={idx} className="flex items-start">
                         <span className="text-emerald-500 mr-2 mt-0.5">-</span>
                         <span className="text-sm text-slate-700">{ind}</span>
                       </li>
                     ))}
                  </ul>
                </div>
             </div>
             
             <div className="mt-6 p-4 bg-slate-50 rounded-lg border border-slate-200">
                <h4 className="text-sm font-semibold text-slate-800 mb-1">Recommended Next Step</h4>
                <p className="text-sm text-slate-600">{aiExplainability?.recommendation || 'Review case manually.'}</p>
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
                    <span className="font-bold text-orange-400">{metrics?.risk7Day || 'N/A'}</span>
                 </div>
                 <div className="flex justify-between items-center border-b border-white/10 pb-3">
                    <span className="text-slate-300 text-sm">30-day risk</span>
                    <span className="font-bold text-amber-400">{metrics?.risk30Day || 'N/A'}</span>
                 </div>
                 <div className="flex justify-between items-center">
                    <span className="text-slate-300 text-sm">Prediction Confidence</span>
                    <span className="font-medium text-white">{metrics?.confidence || 'N/A'}</span>
                 </div>
              </div>
              <div className="mt-4 pt-4 border-t border-white/10">
                 <p className="text-xs text-slate-400 italic">Predictions are decision-support indicators and require human review.</p>
              </div>
           </div>
        </div>
      </div>
    </div>
  );
}
