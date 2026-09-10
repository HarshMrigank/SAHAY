"use client";

import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';

interface AIResult {
  riskScore: number;
  sentiment: string;
  flags: string[];
  explanation: string;
}

export default function AITestingPage() {
  const [inputText, setInputText] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<AIResult | null>(null);

  const handleTest = async () => {
    if (!inputText) return;
    setLoading(true);
    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/admin/ai/test`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: inputText })
      });
      if (res.ok) {
        const data = await res.json();
        setResult(data);
      } else {
        alert('Failed to analyze text.');
      }
    } catch (err) {
      console.error(err);
      alert('Error connecting to AI service.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 max-w-4xl mx-auto space-y-6">
      <h1 className="text-3xl font-bold">AI Pipeline Testing</h1>
      <p className="text-slate-500">Test the distress analysis model with custom input.</p>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Input Text</CardTitle>
            <CardDescription>Enter simulated check-in or chat text</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label>Transcript / Message</Label>
              <textarea 
                className="flex min-h-[200px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                placeholder="Type the message here..."
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
              />
            </div>
            <Button onClick={handleTest} disabled={loading || !inputText} className="w-full">
              {loading ? 'Analyzing...' : 'Run Analysis'}
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Analysis Results</CardTitle>
          </CardHeader>
          <CardContent>
            {!result && !loading && (
              <p className="text-slate-500 text-sm italic">Run an analysis to see results here.</p>
            )}
            {loading && <p className="text-slate-500 text-sm">Processing...</p>}
            {result && (
              <div className="space-y-4">
                <div>
                  <p className="text-sm text-slate-500 mb-1">Risk Score (0-100)</p>
                  <div className="flex items-center gap-3">
                    <span className={`text-2xl font-bold ${
                      result.riskScore > 75 ? 'text-rose-600' : 
                      result.riskScore > 40 ? 'text-orange-500' : 'text-emerald-600'
                    }`}>
                      {result.riskScore}
                    </span>
                  </div>
                </div>
                <div>
                  <p className="text-sm text-slate-500 mb-1">Sentiment</p>
                  <Badge variant={result.sentiment === 'negative' ? 'destructive' : 'secondary'} className="capitalize">
                    {result.sentiment}
                  </Badge>
                </div>
                <div>
                  <p className="text-sm text-slate-500 mb-1">Flags Detected</p>
                  <div className="flex flex-wrap gap-2">
                    {result.flags && result.flags.length > 0 ? (
                      result.flags.map((flag, idx) => (
                        <Badge key={idx} variant="outline" className="border-rose-200 text-rose-700 bg-rose-50">{flag}</Badge>
                      ))
                    ) : (
                      <span className="text-sm text-slate-400">None</span>
                    )}
                  </div>
                </div>
                <div>
                  <p className="text-sm text-slate-500 mb-1">Explanation</p>
                  <p className="text-sm bg-slate-50 p-3 rounded border border-slate-100">{result.explanation}</p>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
