"use client";

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';

const step1Schema = z.object({
  fullName: z.string().min(2, "Full name is required"),
  email: z.string().email("Invalid email address"),
  phone: z.string().min(10, "Phone number is required"),
  role: z.string().min(1, "Role is required"),
});

const step2Schema = z.object({
  hasActiveCase: z.enum(["yes", "no"]),
});

const step3Schema = z.object({
  caseId: z.string().optional(),
  caseDescription: z.string().optional(),
});

type FormData = z.infer<typeof step1Schema> & z.infer<typeof step2Schema> & z.infer<typeof step3Schema>;

export default function RegisterPage() {
  const [step, setStep] = useState(1);
  const [formData, setFormData] = useState<Partial<FormData>>({});

  const form1 = useForm<z.infer<typeof step1Schema>>({
    resolver: zodResolver(step1Schema),
    defaultValues: { fullName: "", email: "", phone: "", role: "" }
  });

  const form2 = useForm<z.infer<typeof step2Schema>>({
    resolver: zodResolver(step2Schema),
    defaultValues: { hasActiveCase: "no" }
  });

  const form3 = useForm<z.infer<typeof step3Schema>>({
    resolver: zodResolver(step3Schema),
    defaultValues: { caseId: "", caseDescription: "" }
  });

  const onNextStep1 = (data: z.infer<typeof step1Schema>) => {
    setFormData({ ...formData, ...data });
    setStep(2);
  };

  const onNextStep2 = (data: z.infer<typeof step2Schema>) => {
    setFormData({ ...formData, ...data });
    if (data.hasActiveCase === "yes") {
      setStep(3);
    } else {
      submitFinalData({ ...formData, ...data });
    }
  };

  const onNextStep3 = (data: z.infer<typeof step3Schema>) => {
    submitFinalData({ ...formData, ...data });
  };

  const submitFinalData = async (data: Partial<FormData>) => {
    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/registrations`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      });
      if (res.ok) {
        alert("Registration submitted for approval.");
        window.location.href = "/";
      } else {
        alert("Failed to submit registration.");
      }
    } catch (err) {
      console.error(err);
      alert("Error submitting registration.");
    }
  };

  return (
    <div className="flex items-center justify-center min-h-screen bg-slate-50 p-4">
      <Card className="w-full max-w-lg">
        <CardHeader>
          <CardTitle>SAHAY Registration</CardTitle>
          <CardDescription>Step {step} of {step === 2 && form2.watch("hasActiveCase") === "no" ? 2 : 3}</CardDescription>
        </CardHeader>
        <CardContent>
          {step === 1 && (
            <form onSubmit={form1.handleSubmit(onNextStep1)} className="space-y-4">
              <div className="space-y-2">
                <Label>Full Name</Label>
                <Input {...form1.register("fullName")} placeholder="John Doe" />
                {form1.formState.errors.fullName && <p className="text-red-500 text-sm">{form1.formState.errors.fullName.message}</p>}
              </div>
              <div className="space-y-2">
                <Label>Email</Label>
                <Input {...form1.register("email")} type="email" placeholder="john@example.com" />
                {form1.formState.errors.email && <p className="text-red-500 text-sm">{form1.formState.errors.email.message}</p>}
              </div>
              <div className="space-y-2">
                <Label>Phone</Label>
                <Input {...form1.register("phone")} placeholder="+91 9876543210" />
                {form1.formState.errors.phone && <p className="text-red-500 text-sm">{form1.formState.errors.phone.message}</p>}
              </div>
              <div className="space-y-2">
                <Label>Role</Label>
                <select {...form1.register("role")} className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50">
                  <option value="">Select a role</option>
                  <option value="victim">Victim / Survivor</option>
                  <option value="district">District Official</option>
                  <option value="admin">Admin</option>
                </select>
                {form1.formState.errors.role && <p className="text-red-500 text-sm">{form1.formState.errors.role.message}</p>}
              </div>
              <Button type="submit" className="w-full">Next</Button>
            </form>
          )}

          {step === 2 && (
            <form onSubmit={form2.handleSubmit(onNextStep2)} className="space-y-4">
              <div className="space-y-2">
                <Label>Do you have an active case?</Label>
                <select {...form2.register("hasActiveCase")} className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50">
                  <option value="yes">Yes</option>
                  <option value="no">No</option>
                </select>
              </div>
              <div className="flex justify-between">
                <Button type="button" variant="outline" onClick={() => setStep(1)}>Back</Button>
                <Button type="submit">Next</Button>
              </div>
            </form>
          )}

          {step === 3 && (
            <form onSubmit={form3.handleSubmit(onNextStep3)} className="space-y-4">
              <div className="space-y-2">
                <Label>Case ID (if known)</Label>
                <Input {...form3.register("caseId")} placeholder="CASE-1234" />
              </div>
              <div className="space-y-2">
                <Label>Case Description / Context</Label>
                <Input {...form3.register("caseDescription")} placeholder="Briefly describe..." />
              </div>
              <div className="flex justify-between">
                <Button type="button" variant="outline" onClick={() => setStep(2)}>Back</Button>
                <Button type="submit">Submit Registration</Button>
              </div>
            </form>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
