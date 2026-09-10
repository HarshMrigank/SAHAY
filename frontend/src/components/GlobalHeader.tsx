"use client";

import Link from 'next/link';
import { Shield } from 'lucide-react';

export default function GlobalHeader() {
  return (
    <header className="bg-primary text-primary-foreground shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <Link href="/" className="flex items-center gap-2 text-primary-foreground font-bold text-xl hover:opacity-90">
          <Shield className="h-6 w-6" />
          <span>SAHAY</span>
        </Link>
        <nav className="hidden md:flex items-center gap-6">
          <Link href="/" className="text-sm font-medium hover:text-primary-foreground/80">Home</Link>
          <Link href="/#about" className="text-sm font-medium hover:text-primary-foreground/80">About</Link>
          <Link href="/#features" className="text-sm font-medium hover:text-primary-foreground/80">Features</Link>
          <Link href="/admin/data" className="text-sm font-medium hover:text-primary-foreground/80">Data Stats</Link>
        </nav>
        <div className="flex items-center gap-4">
          <Link 
            href="/login" 
            className="text-sm font-medium bg-background text-foreground hover:bg-background/90 px-4 py-2 rounded-md transition-colors"
          >
            Sign In
          </Link>
        </div>
      </div>
    </header>
  );
}
