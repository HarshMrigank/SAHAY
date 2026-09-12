"use client";

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';

interface Registration {
  id: string;
  fullName: string;
  email: string;
  role: string;
  status: string;
  createdAt: string;
}

export default function AdminRegistrationsPage() {
  const [registrations, setRegistrations] = useState<Registration[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchRegistrations();
  }, []);

  const fetchRegistrations = async () => {
    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/admin/registrations`);
      if (res.ok) {
        const data = await res.json();
        setRegistrations(data);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 max-w-6xl mx-auto space-y-6">
      <h1 className="text-3xl font-bold">Registration Approvals</h1>
      <Card>
        <CardHeader>
          <CardTitle>Pending & Reviewed Registrations</CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <p>Loading...</p>
          ) : registrations.length === 0 ? (
            <p>No registrations found.</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="border-b">
                    <th className="p-3">Name</th>
                    <th className="p-3">Email</th>
                    <th className="p-3">Role</th>
                    <th className="p-3">Status</th>
                    <th className="p-3">Date</th>
                    <th className="p-3">Action</th>
                  </tr>
                </thead>
                <tbody>
                  {registrations.map(reg => (
                    <tr key={reg.id} className="border-b hover:bg-slate-50">
                      <td className="p-3 font-medium">{reg.fullName}</td>
                      <td className="p-3">{reg.email}</td>
                      <td className="p-3 capitalize">{reg.role}</td>
                      <td className="p-3">
                        <Badge variant={reg.status === 'pending' ? 'secondary' : reg.status === 'approved' ? 'default' : 'destructive'}>
                          {reg.status}
                        </Badge>
                      </td>
                      <td className="p-3">{new Date(reg.createdAt).toLocaleDateString()}</td>
                      <td className="p-3">
                        <Link href={`/admin/registrations/${reg.id}`}>
                          <Button variant="outline" size="sm">Review</Button>
                        </Link>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
