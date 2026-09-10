"use client";

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';

interface RegistrationDetail {
  id: string;
  fullName: string;
  email: string;
  phone: string;
  role: string;
  status: string;
  hasActiveCase: string;
  caseId?: string;
  caseDescription?: string;
  createdAt: string;
}

export default function RegistrationReviewPage({ params }: { params: { id: string } }) {
  const [registration, setRegistration] = useState<RegistrationDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    fetchRegistration();
  }, [params.id]);

  const fetchRegistration = async () => {
    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/admin/registrations/${params.id}`);
      if (res.ok) {
        const data = await res.json();
        setRegistration(data);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleAction = async (status: 'approved' | 'rejected') => {
    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/admin/registrations/${params.id}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status })
      });
      if (res.ok) {
        alert(`Registration ${status}`);
        router.push('/admin/registrations');
      }
    } catch (err) {
      console.error(err);
      alert('Error updating status');
    }
  };

  if (loading) return <div className="p-6">Loading...</div>;
  if (!registration) return <div className="p-6">Registration not found.</div>;

  return (
    <div className="p-6 max-w-3xl mx-auto space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">Review Registration</h1>
        <Badge variant={registration.status === 'pending' ? 'secondary' : registration.status === 'approved' ? 'default' : 'destructive'}>
          {registration.status}
        </Badge>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>User Details</CardTitle>
          <CardDescription>Submitted on {new Date(registration.createdAt).toLocaleString()}</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-sm text-slate-500">Full Name</p>
              <p className="font-medium">{registration.fullName}</p>
            </div>
            <div>
              <p className="text-sm text-slate-500">Email</p>
              <p className="font-medium">{registration.email}</p>
            </div>
            <div>
              <p className="text-sm text-slate-500">Phone</p>
              <p className="font-medium">{registration.phone}</p>
            </div>
            <div>
              <p className="text-sm text-slate-500">Requested Role</p>
              <p className="font-medium capitalize">{registration.role}</p>
            </div>
          </div>

          <div className="pt-4 border-t">
            <h3 className="font-semibold mb-2">Case Information</h3>
            <p className="text-sm text-slate-500">Has Active Case: <span className="font-medium text-slate-900">{registration.hasActiveCase}</span></p>
            {registration.hasActiveCase === 'yes' && (
              <div className="mt-2 space-y-2">
                <p className="text-sm text-slate-500">Case ID: <span className="font-medium text-slate-900">{registration.caseId || 'N/A'}</span></p>
                <p className="text-sm text-slate-500">Description:</p>
                <p className="bg-slate-50 p-3 rounded-md text-sm">{registration.caseDescription || 'No description provided.'}</p>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {registration.status === 'pending' && (
        <div className="flex gap-4">
          <Button onClick={() => handleAction('approved')} className="bg-green-600 hover:bg-green-700">Approve</Button>
          <Button onClick={() => handleAction('rejected')} variant="destructive">Reject</Button>
        </div>
      )}
    </div>
  );
}
