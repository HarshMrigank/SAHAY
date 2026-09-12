"use client";

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { ArrowUpRight, ArrowRight } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line } from 'recharts';

export default function DistrictDashboard() {
  const [dashboardData, setDashboardData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDashboard = async () => {
      try {
        const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/district/dashboard`);
        if (res.ok) {
          const data = await res.json();
          setDashboardData(data);
        }
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchDashboard();
  }, []);

  if (loading) return <div className="p-8">Loading dashboard data...</div>;
  if (!dashboardData) return <div className="p-8">Failed to load dashboard.</div>;

  const { stats, riskData, trendData, priorityCases } = dashboardData;

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">District Wellbeing Monitoring</h1>
          <p className="text-sm text-slate-500 mt-1">Overview of active cases and priority alerts</p>
        </div>
        <div className="text-sm text-slate-500 bg-white px-3 py-1.5 rounded-md border border-slate-200">
          Last updated: Just now
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex flex-col justify-between">
          <p className="text-sm font-medium text-slate-500">Total Active</p>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="text-3xl font-bold text-slate-900">{stats?.totalActive || 0}</span>
          </div>
        </div>
        <div className="bg-emerald-50 p-5 rounded-xl border border-emerald-100 shadow-sm flex flex-col justify-between">
          <p className="text-sm font-medium text-emerald-800">Low Risk</p>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="text-3xl font-bold text-emerald-700">{stats?.lowRisk || 0}</span>
          </div>
        </div>
        <div className="bg-amber-50 p-5 rounded-xl border border-amber-100 shadow-sm flex flex-col justify-between">
          <p className="text-sm font-medium text-amber-800">Moderate</p>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="text-3xl font-bold text-amber-700">{stats?.moderateRisk || 0}</span>
          </div>
        </div>
        <div className="bg-orange-50 p-5 rounded-xl border border-orange-100 shadow-sm flex flex-col justify-between">
          <p className="text-sm font-medium text-orange-800">High Risk</p>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="text-3xl font-bold text-orange-700">{stats?.highRisk || 0}</span>
            <span className="text-sm font-medium text-orange-600 flex items-center"><ArrowUpRight className="h-3 w-3" /> {stats?.highRiskTrend || '0%'}</span>
          </div>
        </div>
        <div className="bg-rose-50 p-5 rounded-xl border border-rose-100 shadow-sm flex flex-col justify-between">
          <p className="text-sm font-medium text-rose-800">Critical</p>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="text-3xl font-bold text-rose-700">{stats?.criticalRisk || 0}</span>
            <span className="text-sm font-medium text-rose-600 flex items-center"><ArrowUpRight className="h-3 w-3" /> {stats?.criticalRiskTrend || '0%'}</span>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Risk Distribution Chart */}
        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
          <h3 className="text-lg font-semibold text-slate-800 mb-4">Risk Distribution</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={riskData || []} margin={{ top: 20, right: 30, left: 0, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{fill: '#64748b'}} />
                <YAxis axisLine={false} tickLine={false} tick={{fill: '#64748b'}} />
                <Tooltip cursor={{fill: '#f1f5f9'}} contentStyle={{borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)'}} />
                <Bar dataKey="value" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Distress Trend */}
        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
          <h3 className="text-lg font-semibold text-slate-800 mb-4">Average District Distress Trend</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={trendData || []} margin={{ top: 20, right: 30, left: 0, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                <XAxis dataKey="week" axisLine={false} tickLine={false} tick={{fill: '#64748b'}} />
                <YAxis axisLine={false} tickLine={false} tick={{fill: '#64748b'}} domain={[0, 100]} />
                <Tooltip contentStyle={{borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)'}} />
                <Line type="monotone" dataKey="score" stroke="#3b82f6" strokeWidth={3} dot={{r: 4, fill: '#3b82f6', strokeWidth: 2, stroke: '#fff'}} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Priority Cases Table */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="px-6 py-5 border-b border-slate-200 flex justify-between items-center bg-slate-50">
          <h3 className="text-lg font-semibold text-slate-800">Priority Cases Requiring Review</h3>
          <Link href="/district/cases" className="text-sm font-medium text-blue-600 hover:text-blue-800 flex items-center">
            View All <ArrowRight className="ml-1 h-4 w-4" />
          </Link>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-slate-600">
            <thead className="text-xs text-slate-500 bg-white border-b border-slate-200 uppercase">
              <tr>
                <th className="px-6 py-4 font-medium">Case ID</th>
                <th className="px-6 py-4 font-medium">Risk Level</th>
                <th className="px-6 py-4 font-medium">Trend</th>
                <th className="px-6 py-4 font-medium">Last Check-in</th>
                <th className="px-6 py-4 font-medium">Assigned Officer</th>
                <th className="px-6 py-4 font-medium">Status</th>
                <th className="px-6 py-4 font-medium text-right">Action</th>
              </tr>
            </thead>
            <tbody>
              {(priorityCases || []).map((c: any, i: number) => (
                <tr key={c.id} className={`border-b border-slate-100 hover:bg-slate-50 transition-colors ${i === 0 ? 'bg-rose-50/30' : ''}`}>
                  <td className="px-6 py-4 font-medium text-slate-900">{c.id}</td>
                  <td className="px-6 py-4">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium
                      ${c.risk === 'CRITICAL' ? 'bg-rose-100 text-rose-800' : 'bg-orange-100 text-orange-800'}
                    `}>
                      {c.risk}
                    </span>
                  </td>
                  <td className="px-6 py-4 font-bold text-slate-700">{c.trend}</td>
                  <td className="px-6 py-4">{c.checkIn}</td>
                  <td className="px-6 py-4">{c.officer}</td>
                  <td className="px-6 py-4">{c.status}</td>
                  <td className="px-6 py-4 text-right">
                    <Link href={`/district/cases/${c.id}`} className="font-medium text-blue-600 hover:text-blue-800">
                      {c.action || 'View'}
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
