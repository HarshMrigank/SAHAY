import Link from 'next/link';
import GlobalHeader from '@/components/GlobalHeader';
import { Lock, Activity, Users, CheckCircle, Database } from 'lucide-react';

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-background flex flex-col">
      <GlobalHeader />

      {/* Hero Section */}
      <section className="bg-primary text-primary-foreground py-20 sm:py-28 lg:py-36 relative overflow-hidden">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10 text-center">
          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold tracking-tight mb-6">
            Empowering Mental Wellbeing <br className="hidden sm:block" /> Through Technology
          </h1>
          <p className="mt-4 text-xl sm:text-2xl max-w-3xl mx-auto text-primary-foreground/90 font-medium">
            SAHAY is a dynamic mental health monitoring & support system designed to safely bridge the gap between victims, counselors, and authorities.
          </p>
          <div className="mt-10 flex justify-center gap-4">
            <Link href="/register" className="px-8 py-3 rounded-md bg-accent text-accent-foreground font-semibold text-lg hover:bg-accent/90 transition-colors shadow-sm">
              Create Profile
            </Link>
            <Link href="/login" className="px-8 py-3 rounded-md bg-background text-foreground font-semibold text-lg hover:bg-background/90 transition-colors shadow-sm">
              Sign In
            </Link>
          </div>
        </div>
      </section>

      {/* About SAHAY Section */}
      <section id="about" className="py-20 bg-background">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl font-bold text-foreground mb-4">About SAHAY</h2>
          <div className="w-24 h-1 bg-primary mx-auto mb-8 rounded-full"></div>
          <p className="max-w-4xl mx-auto text-lg text-muted-foreground leading-relaxed">
            SAHAY acts as a protective digital layer that continuously monitors the mental wellbeing of individuals navigating complex social and legal challenges. By analyzing check-ins and behavioral markers, our system proactively identifies signs of distress, ensuring timely professional intervention before situations escalate.
          </p>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20 bg-secondary/50 border-y border-border">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-foreground mb-4">Core Features</h2>
            <div className="w-24 h-1 bg-primary mx-auto rounded-full"></div>
          </div>
          <div className="grid md:grid-cols-3 gap-8">
            <div className="bg-card p-8 rounded-xl border border-border shadow-sm">
              <Activity className="h-12 w-12 text-primary mb-6" />
              <h3 className="text-xl font-bold text-foreground mb-3">Dynamic Assessment</h3>
              <p className="text-muted-foreground leading-relaxed">
                Regular, culturally-sensitive check-ins customized to the individual&apos;s risk profile and immediate needs.
              </p>
            </div>
            <div className="bg-card p-8 rounded-xl border border-border shadow-sm">
              <Users className="h-12 w-12 text-primary mb-6" />
              <h3 className="text-xl font-bold text-foreground mb-3">Tiered Intervention</h3>
              <p className="text-muted-foreground leading-relaxed">
                Automated escalation routing flags concerning trends directly to district mental health professionals and support staff.
              </p>
            </div>
            <div className="bg-card p-8 rounded-xl border border-border shadow-sm">
              <Lock className="h-12 w-12 text-primary mb-6" />
              <h3 className="text-xl font-bold text-foreground mb-3">Secure Records</h3>
              <p className="text-muted-foreground leading-relaxed">
                End-to-end encryption of sensitive health data, ensuring privacy for vulnerable populations.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="py-20 bg-background">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-foreground mb-4">How It Works</h2>
            <div className="w-24 h-1 bg-primary mx-auto rounded-full"></div>
          </div>
          <div className="grid md:grid-cols-4 gap-6 text-center">
            <div>
              <div className="mx-auto h-16 w-16 bg-primary text-primary-foreground rounded-full flex items-center justify-center text-2xl font-bold mb-4 shadow-md">1</div>
              <h4 className="text-lg font-bold text-foreground mb-2">Registration</h4>
              <p className="text-sm text-muted-foreground">Secure onboarding through authorized institutional channels.</p>
            </div>
            <div>
              <div className="mx-auto h-16 w-16 bg-primary text-primary-foreground rounded-full flex items-center justify-center text-2xl font-bold mb-4 shadow-md">2</div>
              <h4 className="text-lg font-bold text-foreground mb-2">Check-ins</h4>
              <p className="text-sm text-muted-foreground">User responds to periodic wellbeing questionnaires.</p>
            </div>
            <div>
              <div className="mx-auto h-16 w-16 bg-primary text-primary-foreground rounded-full flex items-center justify-center text-2xl font-bold mb-4 shadow-md">3</div>
              <h4 className="text-lg font-bold text-foreground mb-2">Analysis</h4>
              <p className="text-sm text-muted-foreground">AI processes responses to map cognitive and emotional risk markers.</p>
            </div>
            <div>
              <div className="mx-auto h-16 w-16 bg-primary text-primary-foreground rounded-full flex items-center justify-center text-2xl font-bold mb-4 shadow-md">4</div>
              <h4 className="text-lg font-bold text-foreground mb-2">Support</h4>
              <p className="text-sm text-muted-foreground">Professional counselors are alerted to intervene when necessary.</p>
            </div>
          </div>
        </div>
      </section>

      {/* Responsible AI & Privacy */}
      <section className="py-20 bg-primary text-primary-foreground">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-2 gap-12 items-center">
            <div>
              <h2 className="text-3xl font-bold mb-6">Responsible AI & Privacy</h2>
              <ul className="space-y-4">
                <li className="flex items-start">
                  <CheckCircle className="h-6 w-6 mr-3 text-accent flex-shrink-0" />
                  <p className="text-primary-foreground/90 font-medium">Models are transparent, accountable, and designed to support—not replace—clinical judgment.</p>
                </li>
                <li className="flex items-start">
                  <CheckCircle className="h-6 w-6 mr-3 text-accent flex-shrink-0" />
                  <p className="text-primary-foreground/90 font-medium">Data is anonymized and localized strictly within Indian data centers following national guidelines.</p>
                </li>
                <li className="flex items-start">
                  <CheckCircle className="h-6 w-6 mr-3 text-accent flex-shrink-0" />
                  <p className="text-primary-foreground/90 font-medium">Consent is continuously reaffirmed, and users maintain the right to exit the monitoring program.</p>
                </li>
              </ul>
            </div>
            <div className="bg-background text-foreground p-8 rounded-xl shadow-lg border border-border">
              <div className="flex items-center gap-3 mb-4">
                <Database className="h-8 w-8 text-primary" />
                <h3 className="text-2xl font-bold">Data Transparency</h3>
              </div>
              <p className="text-muted-foreground mb-6">
                Curious about our system&apos;s scale? You can view anonymized system-wide statistics securely.
              </p>
              <Link href="/admin/data" className="inline-block px-6 py-2 bg-primary text-primary-foreground font-semibold rounded hover:bg-primary/90 transition-colors">
                View Admin Statistics
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-card border-t border-border py-8 text-center text-muted-foreground">
        <p className="text-sm">© 2026 SAHAY Initiative. Developed for SIH. All rights reserved.</p>
      </footer>
    </div>
  );
}
