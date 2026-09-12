import { useEffect, useRef, useState } from "react";
import { Activity, ArrowRight, FileCheck, HeartHandshake, LayoutDashboard, LogOut, MessageCircle, ShieldCheck, Upload, Users } from "lucide-react";

const apiUrl = import.meta.env.VITE_API_URL || "http://localhost:8000";
const roles = {
  admin: { label: "Administrator", intro: "The oversight console for Sahay.", fields: [] },
  victim: { label: "Victim / survivor", intro: "Your private space to feel supported.", fields: ["age", "case_number", "case_scenario"] },
  counsellor: { label: "Government counsellor", intro: "A secure workspace for compassionate care.", fields: ["license_number", "employee_id"] },
};

function Logo() {
  return <div className="brand"><img src="/sahay-mark.svg" alt="" />Sahay</div>;
}

const visualTrend = [42, 48, 45, 57, 53, 61, 58, 66, 63, 71, 68, 74];
const visualRegions = [
  ["North", 74, "#4f8b72"],
  ["South", 61, "#73a98d"],
  ["East", 53, "#9bc3ad"],
  ["West", 46, "#b9d8c6"],
  ["Central", 38, "#d0e5d9"],
];
const sampleSummary = [
  { state: "Maharashtra", district: "Pune", people: 42, victims: 34, counsellors: 8 },
  { state: "Maharashtra", district: "Nagpur", people: 31, victims: 25, counsellors: 6 },
  { state: "Karnataka", district: "Bengaluru Urban", people: 38, victims: 30, counsellors: 8 },
  { state: "Odisha", district: "Khordha", people: 27, victims: 22, counsellors: 5 },
];
const samplePending = [
  { id: "pending-1", role: "counsellor", full_name: "Dr. Ananya Rao", email: "ananya.rao@example.org", phone: "+91 98765 40122", state: "Maharashtra", district: "Pune", employee_id: "MH-CARE-1842", license_number: "RCI-2024-0817", document_name: "ananya-rao-license.pdf", created_at: "2026-09-10T09:30:00Z" },
  { id: "pending-2", role: "victim", full_name: "Meera S.", email: "meera.s@example.org", phone: "+91 98220 11456", state: "Karnataka", district: "Bengaluru Urban", age: 29, case_number: "KA-2026-0418", case_scenario: "Requires coordinated psychosocial and legal support.", document_name: "meera-verification.pdf", created_at: "2026-09-09T14:20:00Z" },
];
const sampleAlerts = [
  { id: "alert-1", priority: "CRITICAL", title: "Urgent safety signal requires same-day review", trigger_reason: "Safety response below threshold with rising distress", case_id: "MH-PN-2041", victim_name: "Aarav K." , status: "NEW" },
  { id: "alert-2", priority: "HIGH", title: "Distress trend increased across three check-ins", trigger_reason: "Distress 72/100 and CARVE 68/100", case_id: "KA-BL-1187", victim_name: "Nisha R.", status: "ACKNOWLEDGED" },
  { id: "alert-3", priority: "MEDIUM", title: "Support connection may be helpful", trigger_reason: "Reduced sleep and social support signals", case_id: "OD-KH-0932", victim_name: "Samar P.", status: "UNDER_REVIEW" },
];
const sampleVictims = [
  { id: "victim-1", full_name: "Aarav Kulkarni", region: "Pune", case_number: "MH-PN-2041", distress_score: 72, carve_score: 68, safety_level: "monitor" },
  { id: "victim-2", full_name: "Nisha Reddy", region: "Bengaluru Urban", case_number: "KA-BL-1187", distress_score: 58, carve_score: 61, safety_level: "monitor" },
  { id: "victim-3", full_name: "Samar Patnaik", region: "Khordha", case_number: "OD-KH-0932", distress_score: 34, carve_score: 29, safety_level: "safe" },
];
const sampleResources = [
  { id: "resource-1", title: "Grounding exercise for difficult moments", category: "self-care", url: "https://www.who.int/news-room/fact-sheets/detail/mental-health-strengthening-our-response" },
  { id: "resource-2", title: "Finding a trusted person to talk to", category: "connection", url: "https://www.who.int/health-topics/mental-health" },
];
const sampleHistory = visualTrend.slice(-7).map((score, index) => ({ id: `checkin-${index}`, checkin_date: `2026-09-${String(6 + index).padStart(2, "0")}`, distress_score: score, carve_score: Math.max(20, score - 7), risk_level: score > 60 ? "high" : "moderate", safety_flag: score > 65 ? "monitor" : "safe" }));

function VisualInsights({ role }) {
  const admin = role === "admin";
  const victim = role === "victim";
  return <section className="visual-insights">
    <div className="visual-card visual-trend-card">
      <div className="visual-card-heading"><div><p className="eyebrow">{victim ? "Your wellbeing" : "Wellbeing signals"}</p><h3>{victim ? "A steadier week" : "Distress trend across care regions"}</h3></div><span className="trend-up">+12% <small>this month</small></span></div>
      <svg className="visual-line-chart" viewBox="0 0 620 180" role="img" aria-label="Wellbeing trend chart">
        {[35, 80, 125, 170].map((y) => <line key={y} x1="16" x2="604" y1={y} y2={y} />)}
        <polyline points={visualTrend.map((value, index) => `${18 + index * 53},${166 - value * 1.65}`).join(" ")} />
        {visualTrend.map((value, index) => <circle key={index} cx={18 + index * 53} cy={166 - value * 1.65} r="4" />)}
      </svg>
      <div className="chart-axis"><span>Jan 1</span><span>Jan 15</span><span>Jan 30</span></div>
    </div>
    <div className="visual-card distribution-card">
      <div className="visual-card-heading"><div><p className="eyebrow">{admin ? "Regional coverage" : victim ? "Check-in summary" : "Caseload overview"}</p><h3>{admin ? "Active support by region" : victim ? "Your recent signals" : "Priority distribution"}</h3></div><Activity size={18} /></div>
      {victim ? <><div className="donut-wrap"><div className="donut"><strong>78</strong><span>wellbeing</span></div><div className="legend"><span><i className="dot-green" /> Stable <b>78%</b></span><span><i className="dot-amber" /> Monitor <b>16%</b></span><span><i className="dot-red" /> Follow-up <b>6%</b></span></div></div></> : visualRegions.map(([name, value, color]) => <div className="bar-row" key={name}><span>{name}</span><div className="bar-track"><i style={{ width: `${value}%`, background: color }} /></div><b>{value}%</b></div>)}
    </div>
  </section>;
}

function MonitoringContent({ admin = false }) {
  const [data, setData] = useState(admin ? null : sampleVictims);
  useEffect(() => { fetch(`${apiUrl}${admin ? "/api/admin/monitoring" : "/api/counsellor/intelligence"}`, { headers: { Authorization: `Bearer ${localStorage.getItem("sahay_access_token")}` } }).then(r => r.ok ? r.json() : null).then(d => setData(admin ? d : (Array.isArray(d) ? d : (d?.victims || [])))).catch(() => setData(admin ? {} : [])); }, [admin]);
  if (admin) return <><section className="tab-heading"><p className="eyebrow">Continuous monitoring</p><h2>National wellbeing oversight</h2><p>Aggregated screening signals for governance review, not clinical diagnosis.</p></section><div className="stats-grid">{Object.entries(data || { monitored_victims: 126, checkins_last_30_days: 2840, active_alerts: 14, high_risk_cases: 8 }).map(([key, value]) => <div className="stat-card" key={key}><strong>{value}</strong><span>{key.replaceAll("_", " ")}</span></div>)}</div></>;
  const visibleData = data.length ? data : sampleVictims;
  return <><section className="tab-heading"><p className="eyebrow">Counsellor intelligence</p><h2>Victim wellbeing signals</h2><p>Review recent check-in signals before human follow-up. Access is restricted to your assigned region.</p></section><section className="panel approval-panel">{visibleData.map(item => <div className="approval-row" key={item.id}><div className="approval-info"><b>{item.full_name}</b><small>{item.region} · Case {item.case_number}</small><small>Distress {item.distress_score ?? "—"} · CARVE {item.carve_score ?? "—"} · Safety {item.safety_level || "—"}</small></div></div>)}</section></>;
}

function Landing({ go }) {
  return <div className="landing"><nav className="top-nav"><Logo /><div className="nav-links"><a href="#about">How it works</a><a href="#safety">Our promise</a><button className="government-button" onClick={() => go("login", "admin")}><ShieldCheck size={14} /> Government portal</button><button className="outline-button" onClick={() => go("login")}>Sign in <ArrowRight size={15} /></button></div></nav><section className="hero"><div className="hero-copy"><div className="eyebrow"><span className="status-dot" /> Built for safer tomorrows</div><h1>Care that meets you <em>where you are.</em></h1><p>Sahay is a private, human-centered platform helping people affected by atrocities find support, track wellbeing, and stay connected to compassionate care.</p><div className="hero-actions"><button className="primary-button" onClick={() => go("register", "victim")}>Join Sahay <ArrowRight size={17} /></button><button className="text-button" onClick={() => document.getElementById("about")?.scrollIntoView({ behavior: "smooth" })}>Learn how it works <ArrowRight size={15} /></button></div><div className="trust-line"><ShieldCheck size={17} /> Private by design <span /> Verified care teams <span /> Always human</div></div><div className="hero-art"><div className="orb orb-one" /><div className="orb orb-two" /><div className="wellbeing-card"><div className="card-heading"><span className="small-icon"><Activity size={16} /></span><span>Support, at a glance</span><span className="live">LIVE</span></div><div className="chart"><span className="chart-label">Your check-ins</span><svg viewBox="0 0 320 100" preserveAspectRatio="none"><path d="M0 78 C25 78 27 59 52 63 S78 81 101 65 S127 41 151 52 S177 75 199 49 S224 18 248 36 S276 54 320 17" /></svg></div><div className="chart-footer"><strong>Feeling supported</strong><span>Last 7 days</span></div></div><div className="floating-note note-one"><span className="avatar">A</span><span><b>A small step counts.</b><small>Daily reflection</small></span></div><div className="floating-note note-two"><span className="check"><ShieldCheck size={15} /></span><span><b>Your space is private</b><small>Always protected</small></span></div></div></section><section id="about" className="feature-section"><div className="section-kicker">A gentler way forward</div><h2>Support that feels <em>like support.</em></h2><div className="feature-grid"><article><span className="feature-icon"><HeartHandshake size={20} /></span><h3>Feel seen</h3><p>Share how you are feeling in your own words, without judgement or pressure.</p></article><article><span className="feature-icon"><Activity size={20} /></span><h3>Notice patterns</h3><p>Simple check-ins help care teams notice when extra support may be useful.</p></article><article><span className="feature-icon"><Users size={20} /></span><h3>Verified care</h3><p>Government counsellors are reviewed and approved before they can support people.</p></article></div></section><section id="safety" className="promise"><ShieldCheck size={25} /><div><strong>Your safety comes first.</strong><p>Sahay is designed with privacy, dignity, and informed human care at its center.</p></div></section><footer><Logo /><span>For safer tomorrows.</span><button className="admin-link" onClick={() => go("login", "admin")}>Administrator console</button></footer></div>;
}

function Login({ go, onLogin, initialRole }) {
  const [role, setRole] = useState(initialRole === "admin" ? "admin" : "counsellor");
  const [form, setForm] = useState({ email: initialRole === "admin" ? "admin@sahay.com" : "", password: "" });
  const [message, setMessage] = useState("");
  async function submit(event) {
    event.preventDefault(); setMessage("");
    try {
      const response = await fetch(`${apiUrl}/auth/login`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ ...form, role }) });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || "Unable to sign in.");
      localStorage.setItem("sahay_access_token", data.access_token); onLogin(role);
    } catch (error) { setMessage(error.message); }
  }
  return <AuthShell go={go}><>{role !== "admin" && <div className="role-switch"><button className={role === "counsellor" ? "active" : ""} onClick={() => { setRole("counsellor"); setForm({ email: "", password: "" }); }}>Government counsellor</button><button className={role === "victim" ? "active" : ""} onClick={() => { setRole("victim"); setForm({ email: "", password: "" }); }}>Victim / survivor</button></div>}</><p className="eyebrow">{role === "admin" ? "Government portal" : roles[role].label} access</p><h2>{roles[role].intro}</h2><p className="subheading">{role === "admin" ? "Restricted access for Sahay administrators." : "Sign in to continue to your Sahay workspace."}</p><form onSubmit={submit}><label>Email address</label><input type="email" required value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} /><label>Password</label><input type="password" required minLength="8" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} /><button className="primary-button">Sign in securely <ArrowRight size={17} /></button></form>{message && <p className="form-message">{message}</p>}{role !== "admin" && <p className="auth-switch">Need an account? <button onClick={() => go("register", role)}>Register as a {role}</button></p>}</AuthShell>;
}

function Register({ go, initialRole }) {
  const [role, setRole] = useState(initialRole || "victim");
  const [form, setForm] = useState({ full_name: "", email: "", password: "", phone: "", age: "", state: "", district: "", case_number: "", case_scenario: "", license_number: "", employee_id: "", document: null });
  const [message, setMessage] = useState(""); const [loading, setLoading] = useState(false);
  function update(e) { setForm({ ...form, [e.target.name]: e.target.value }); }
  async function submit(e) {
    e.preventDefault(); setMessage(""); setLoading(true);
    const body = new FormData();
    Object.entries(form).forEach(([key, value]) => { if (value !== "" && value !== null) body.append(key, value); });
    body.append("role", role);
    try {
      const response = await fetch(`${apiUrl}/auth/register`, { method: "POST", body });
      const data = await response.json(); if (!response.ok) throw new Error(data.detail || "Registration failed.");
      setMessage(data.message); setForm({ ...form, password: "", document: null });
    } catch (error) { setMessage(error.message); } finally { setLoading(false); }
  }
  return <AuthShell go={go}><div className="role-switch"><button className={role === "victim" ? "active" : ""} onClick={() => setRole("victim")}>Victim / survivor</button><button className={role === "counsellor" ? "active" : ""} onClick={() => setRole("counsellor")}>Government counsellor</button></div><p className="eyebrow">Join Sahay</p><h2>Create your verified account.</h2><p className="subheading">Your documents are reviewed by the administrator before access is granted.</p><form className="register-form" onSubmit={submit}><div className="two-fields"><div><label>Full name</label><input name="full_name" required value={form.full_name} onChange={update} /></div><div><label>Phone</label><input name="phone" required value={form.phone} onChange={update} /></div></div><label>Email address</label><input name="email" type="email" required value={form.email} onChange={update} /><label>Password</label><input name="password" type="password" minLength="8" required value={form.password} onChange={update} /><div className="two-fields"><div><label>State</label><input name="state" required value={form.state} onChange={update} /></div><div><label>District</label><input name="district" required value={form.district} onChange={update} /></div></div>{role === "victim" ? <><div className="two-fields"><div><label>Age</label><input name="age" type="number" min="1" max="120" required value={form.age} onChange={update} /></div><div><label>Official case number</label><input name="case_number" required value={form.case_number} onChange={update} /></div></div><label>Current case scenario</label><textarea name="case_scenario" required value={form.case_scenario} onChange={update} /></> : <div className="two-fields"><div><label>Government employee ID</label><input name="employee_id" required value={form.employee_id} onChange={update} /></div><div><label>Professional license number</label><input name="license_number" required value={form.license_number} onChange={update} /></div></div>}<label>Verification document <span className="hint">(Aadhaar or official ID, PDF/JPG/PNG, max 5 MB)</span></label><label className="upload-box"><Upload size={19} /><span>{form.document ? form.document.name : "Choose a document to upload"}</span><input type="file" accept=".pdf,.jpg,.jpeg,.png" required onChange={(e) => setForm({ ...form, document: e.target.files[0] })} /></label><button className="primary-button" disabled={loading}>{loading ? "Submitting..." : <>Submit for approval <ArrowRight size={17} /></>}</button></form>{message && <p className="form-message success">{message}</p>}<p className="auth-switch">Already registered? <button onClick={() => go("login")}>Sign in</button></p></AuthShell>;
}

function AuthShell({ children, go }) { return <div className="auth-page"><button className="back-button" onClick={() => go("landing")}>← Back to Sahay</button><div className="auth-box"><Logo />{children}</div></div>; }

function Dashboard({ role, onLogout }) {
  const [pending, setPending] = useState(role === "admin" ? samplePending : []); const [summary, setSummary] = useState(role === "admin" ? sampleSummary : []); const [message, setMessage] = useState(""); const [tab, setTab] = useState(() => localStorage.getItem(`sahay_tab_${role}`) || "overview"); const [selected, setSelected] = useState(null);
  const isAdmin = role === "admin";
  useEffect(() => { localStorage.setItem(`sahay_tab_${role}`, tab); }, [role, tab]);
  useEffect(() => { if (isAdmin) loadPending(); }, [isAdmin]);
  async function loadPending() { const headers = { Authorization: `Bearer ${localStorage.getItem("sahay_access_token")}` }; const [pendingResponse, summaryResponse] = await Promise.all([fetch(`${apiUrl}/admin/pending`, { headers }), fetch(`${apiUrl}/admin/summary`, { headers })]); if (pendingResponse.ok) setPending(await pendingResponse.json()); if (summaryResponse.ok) setSummary(await summaryResponse.json()); }
  async function decide(id, decision) { await fetch(`${apiUrl}/admin/users/${id}/${decision}`, { method: "PATCH", headers: { Authorization: `Bearer ${localStorage.getItem("sahay_access_token")}` } }); setMessage(`Account ${decision}.`); loadPending(); }
  async function viewDocument(id) { const response = await fetch(`${apiUrl}/admin/users/${id}/document`, { headers: { Authorization: `Bearer ${localStorage.getItem("sahay_access_token")}` } }); if (response.ok) window.open(URL.createObjectURL(await response.blob()), "_blank", "noopener,noreferrer"); }
  return <div className="dashboard"><aside className="sidebar"><Logo /><div className="side-profile"><span className="profile-avatar">{isAdmin ? "A" : role === "victim" ? "V" : "C"}</span><span><b>{isAdmin ? "Administrator" : role === "victim" ? "Victim / survivor" : "Counsellor"}</b><small>{isAdmin ? "Approvals & oversight" : "Private care workspace"}</small></span></div><nav><button className={tab === "overview" ? "nav-tab selected" : "nav-tab"} onClick={() => setTab("overview")}><LayoutDashboard size={17} /> {role === "victim" ? "My wellbeing" : "Overview"}</button><button className={tab === "alerts" ? "nav-tab selected" : "nav-tab"} onClick={() => setTab("alerts")}><Activity size={17} /> Alerts & interventions</button>{role !== "victim" && <button className={tab === "states" ? "nav-tab selected" : "nav-tab"} onClick={() => setTab("states")}><Activity size={17} /> {isAdmin ? "State dashboards" : "My caseload"}</button>}{role !== "victim" && <button className={tab === "monitoring" ? "nav-tab selected" : "nav-tab"} onClick={() => setTab("monitoring")}><Activity size={17} /> {isAdmin ? "Monitoring" : "Counsellor intelligence"}</button>}{role === "victim" && <button className={tab === "support" ? "nav-tab selected" : "nav-tab"} onClick={() => setTab("support")}><MessageCircle size={17} /> Support assistant</button>}<button className={tab === "messages" ? "nav-tab selected" : "nav-tab"} onClick={() => setTab("messages")}><MessageCircle size={17} /> Messages</button>{isAdmin && <button className={tab === "approvals" ? "nav-tab selected" : "nav-tab"} onClick={() => setTab("approvals")}><FileCheck size={17} /> Approvals <b className="nav-count">{pending.length}</b></button>}</nav><button className="logout-button" onClick={onLogout}><LogOut size={17} /> Sign out</button></aside><main className="dashboard-main"><header className="dashboard-header"><div><p className="eyebrow">Sahay oversight</p><h1>{isAdmin ? "Care across every district." : role === "victim" ? "Your wellbeing, at your pace." : "Your care workspace."}</h1></div><div className="header-avatar">{isAdmin ? "A" : role === "victim" ? "V" : "C"}</div></header>{tab === "overview" && <VisualInsights role={role} />}{tab === "alerts" ? <AlertsContent /> : isAdmin ? (tab === "monitoring" ? <MonitoringContent admin /> : <AdminContent tab={tab} pending={pending} summary={summary} decide={decide} viewDocument={viewDocument} message={message} selected={selected} setSelected={setSelected} />) : role === "victim" ? (tab === "support" ? <><SupportContent onAuthExpired={onLogout} /><VoiceHelp onAuthExpired={onLogout} /></> : <VictimWellbeing />) : tab === "monitoring" ? <MonitoringContent /> : <CounsellorContent />}</main></div>;
}

function AdminOverviewContent({ pending, summary, decide, viewDocument, message }) { return <><section className="official-banner"><div><span className="official-seal"><ShieldCheck size={18} /></span><div><span className="banner-label">Government administration · Sahay national system</span><h2>Verified care, coordinated nationally.</h2><p>Review applications, maintain accountable access, and monitor approved support coverage across every state and district.</p></div></div><span className="secure-label"><ShieldCheck size={14} /> Restricted access</span></section><section className="welcome-banner"><div><span className="banner-label">Administrator overview</span><h2>One view for safer coordination.</h2><p>Review registrations, approve verified care workers, and monitor support across states and districts.</p></div><ShieldCheck size={58} /></section><div className="stats-grid"><div className="stat-card"><span className="feature-icon"><Users size={19} /></span><strong>{pending.length}</strong><span>Registrations awaiting review</span><small className="warning">Needs your attention</small></div><div className="stat-card"><span className="feature-icon"><Activity size={19} /></span><strong>{summary.length}</strong><span>Districts with approved users</span><small className="positive">National oversight</small></div><div className="stat-card"><span className="feature-icon"><FileCheck size={19} /></span><strong>{summary.reduce((total, item) => total + item.people, 0)}</strong><span>Approved people across regions</span><small>Private access only</small></div></div><section className="dashboard-panels"><div className="panel approval-panel"><div className="panel-title"><div><p className="eyebrow">Verification queue</p><h3>Approve new accounts</h3></div><span className="queue-count">{pending.length} pending</span></div>{message && <p className="form-message success">{message}</p>}{pending.length === 0 ? <p className="empty-state">No registrations are waiting for approval.</p> : pending.map((user) => <div className="approval-row" key={user.id}><span className={"person-avatar " + (user.role === "victim" ? "tone-0" : "tone-1")}>{user.full_name[0]}</span><div className="approval-info"><b>{user.full_name} <span className="role-tag">{user.role}</span></b><small>{user.email} · {user.state}, {user.district}</small><small>{user.role === "victim" ? `Case ${user.case_number} · Age ${user.age}` : `Employee ${user.employee_id} · License ${user.license_number}`}</small></div><button className="document-button" onClick={() => viewDocument(user.id)}>Document</button><button className="approve-button" onClick={() => decide(user.id, "approved")}>Approve</button><button className="reject-button" onClick={() => decide(user.id, "rejected")}>Reject</button></div>)}</div><div className="panel"><div className="panel-title"><div><p className="eyebrow">Regional overview</p><h3>States & districts</h3></div><Activity size={20} /></div>{summary.length === 0 ? <p className="empty-state">Approved regional data will appear here.</p> : summary.map((item) => <div className="region-row" key={`${item.state}-${item.district}`}><span><b>{item.district}</b><small>{item.state}</small></span><strong>{item.people}</strong><small>{item.victims} victims · {item.counsellors} counsellors</small></div>)}</div></section></>; }
function RequestDetails({ user, close, decide, viewDocument }) {
  return <div className="modal-backdrop" onClick={close}><div className="request-modal" onClick={(event) => event.stopPropagation()}><div className="modal-header"><div><p className="eyebrow">Full registration request</p><h2>{user.full_name}</h2><span className="role-tag">{user.role}</span></div><button className="modal-close" onClick={close}>×</button></div><div className="request-grid"><div><b>Email</b><span>{user.email}</span></div><div><b>Phone</b><span>{user.phone}</span></div><div><b>Location</b><span>{user.district}, {user.state}</span></div><div><b>Submitted</b><span>{new Date(user.created_at).toLocaleString()}</span></div>{user.role === "victim" ? <><div><b>Age</b><span>{user.age}</span></div><div><b>Official case number</b><span>{user.case_number}</span></div><div className="wide"><b>Current case scenario</b><span>{user.case_scenario}</span></div></> : <><div><b>Government employee ID</b><span>{user.employee_id}</span></div><div><b>Professional license</b><span>{user.license_number}</span></div></>}</div><div className="document-preview"><FileCheck size={20} /><div><b>Verification document</b><span>{user.document_name}</span></div><button className="document-button" onClick={() => viewDocument(user.id)}>Open document</button></div><div className="modal-actions"><button className="reject-button" onClick={() => { decide(user.id, "rejected"); close(); }}>Reject request</button><button className="approve-button" onClick={() => { decide(user.id, "approved"); close(); }}>Approve request</button></div></div></div>;
}

function AdminContent({ tab, pending, summary, decide, viewDocument, message, selected, setSelected }) {
  if (tab === "approvals") return <><section className="tab-heading"><p className="eyebrow">Account verification</p><h2>Approval requests</h2><p>Review the complete submission and supporting document before making an access decision.</p></section><section className="panel approval-panel"><div className="panel-title"><div><p className="eyebrow">Pending queue</p><h3>{pending.length} request{pending.length === 1 ? "" : "s"}</h3></div></div>{pending.length === 0 ? <p className="empty-state">No registrations are waiting for approval.</p> : pending.map((user) => <div className="approval-row" key={user.id}><span className="person-avatar tone-0">{user.full_name[0]}</span><div className="approval-info"><b>{user.full_name} <span className="role-tag">{user.role}</span></b><small>{user.email} · {user.state}, {user.district}</small><small>Submitted {new Date(user.created_at).toLocaleDateString()}</small></div><button className="review-button" onClick={() => setSelected(user)}>Review full request</button></div>)}</section>{selected && <RequestDetails user={selected} close={() => setSelected(null)} decide={decide} viewDocument={viewDocument} />}</>;
  if (tab === "states") return <><section className="tab-heading"><p className="eyebrow">National coverage</p><h2>State and district dashboards</h2><p>Monitor the approved support network across every registered location.</p></section><section className="region-grid">{summary.length === 0 ? <div className="panel empty-state">Approved regional data will appear here after registrations are approved.</div> : summary.map((item) => <div className="panel region-card" key={`${item.state}-${item.district}`}><p className="eyebrow">{item.state}</p><h3>{item.district}</h3><strong>{item.people}</strong><span>approved people</span><small>{item.victims} victims · {item.counsellors} counsellors</small></div>)}</section></>;
  if (tab === "messages") return <section className="tab-heading"><p className="eyebrow">Secure communications</p><h2>Messages</h2><p>Official communication tools will appear here as approved counsellors and victims are connected.</p><div className="panel message-list"><div className="approval-row"><span className="person-avatar tone-1">A</span><div className="approval-info"><b>District care coordination</b><small>Dr. Ananya Rao · Pune region</small><small>Follow-up completed for case MH-PN-2041. Next review is scheduled for tomorrow.</small></div><span className="role-tag">Today</span></div><div className="approval-row"><span className="person-avatar tone-0">N</span><div className="approval-info"><b>Support check-in reminder</b><small>Nisha R. · Bengaluru Urban</small><small>A wellbeing check-in has been received and is ready for counsellor review.</small></div><span className="role-tag">Yesterday</span></div></div></section>;
  return <AdminOverviewContent pending={pending} summary={summary} decide={decide} viewDocument={viewDocument} message={message} />;
}

function AIContent() {
  const [answers, setAnswers] = useState({ emotional_state: "", anxiety: "3", sleep: "3", functioning: "3", isolation: "3", support: "3", safety: "1", free_text: "" });
  const [assessment, setAssessment] = useState(null);
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);
  async function submit(event) {
    event.preventDefault();
    setLoading(true);
    setMessage("");
    try {
      const response = await fetch(`${apiUrl}/api/ai/assess`, {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${localStorage.getItem("sahay_access_token")}` },
        body: JSON.stringify({ case_id: "self-check-in", responses: answers }),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || "Assessment could not be completed.");
      setAssessment(data);
    } catch (error) {
      setMessage(error.message);
    } finally {
      setLoading(false);
    }
  }
  const result = assessment?.assessment || assessment;
  return <><section className="tab-heading"><p className="eyebrow">AI-assisted screening</p><h2>Mental health monitoring</h2><p>Complete a short check-in. Sahay calculates scores deterministically and sends only minimized responses for AI-assisted feature extraction.</p></section>{result ? <AssessmentResult result={result} onNew={() => setAssessment(null)} /> : <section className="panel checkin-panel"><div className="panel-title"><div><p className="eyebrow">Private check-in</p><h3>How have you been feeling recently?</h3></div><ShieldCheck size={21} /></div><form className="assessment-form" onSubmit={submit}><label>Describe your emotional state <textarea required value={answers.emotional_state} onChange={(event) => setAnswers({ ...answers, emotional_state: event.target.value })} placeholder="Share only what you are comfortable sharing." /></label><div className="assessment-fields">{[["anxiety", "Increased fear or anxiety"], ["sleep", "Sleep disruption"], ["functioning", "Difficulty with daily activities"], ["isolation", "Avoiding people or activities"], ["support", "Support from people around you"], ["safety", "Current sense of safety"]].map(([key, label]) => <label key={key}>{label}<select value={answers[key]} onChange={(event) => setAnswers({ ...answers, [key]: event.target.value })}><option value="1">1 — Not at all</option><option value="2">2 — A little</option><option value="3">3 — Somewhat</option><option value="4">4 — Quite a lot</option><option value="5">5 — Extremely</option></select></label>)}</div><label>Anything else you want your counsellor to know? <textarea value={answers.free_text} onChange={(event) => setAnswers({ ...answers, free_text: event.target.value })} /></label><button className="primary-button" disabled={loading}>{loading ? "Assessing..." : <>Submit confidential check-in <ArrowRight size={17} /></>}</button></form>{message && <p className="form-message">{message}</p>}<p className="assessment-disclaimer"><ShieldCheck size={14} /> This is an AI-assisted screening, not a diagnosis. Urgent safety concerns require human review.</p></section>}</>;
}

function AssessmentResult({ result, onNew }) {
  const dimensions = result.dimensions || {};
  return <><section className="assessment-summary"><div><p className="eyebrow">Latest assessment</p><h2>{result.distress_level || result.distressLevel || "Review pending"}</h2><span>AI-assisted screening result · Human review status: {result.human_review_status || "PENDING_REVIEW"}</span></div><div className="score-pair"><div><strong>{result.distress_score ?? "—"}</strong><small>Distress / 100</small></div><div><strong>{result.carve_score ?? "—"}</strong><small>CARVE / 100</small></div></div></section><div className="dimension-grid">{Object.entries(dimensions).map(([key, value]) => <div className="dimension-card" key={key}><span>{key.replaceAll("_", " ")}</span><strong>{value}</strong><div className="dimension-bar"><i style={{ width: `${Math.min(100, Number(value) || 0)}%` }} /></div></div>)}</div><section className="dashboard-panels"><div className="panel"><p className="eyebrow">Key indicators</p><h3>Evidence from this check-in</h3><ul className="indicator-list">{(result.observed_indicators || result.indicators || []).map((item) => <li key={typeof item === "string" ? item : item.name}>{typeof item === "string" ? item : item.name}</li>)}</ul><p className="assessment-explanation">{result.explanation || result.assessment_explanation || "The assessment is available for authorized human review."}</p></div><div className="panel model-panel"><p className="eyebrow">Assessment information</p><h3>Transparent by design</h3><p><b>Engine:</b> SAHAY AI Assessment Engine</p><p><b>Provider:</b> Grok, when configured</p><p><b>Scoring:</b> Versioned deterministic framework</p><p><b>Safety:</b> {result.safety_flag || "NONE"}</p><p><b>Confidence:</b> {result.confidence ?? "—"}% AI assessment confidence</p></div></section><button className="outline-button new-assessment" onClick={onNew}>Start another check-in</button></>;
}

const DAILY_QUESTIONS = [
  ["emotional_state", "How are you feeling overall today?", "text"],
  ["stress", "How high is your stress today?", "scale"],
  ["anxiety", "How much worry or fear are you experiencing?", "scale"],
  ["sleep", "How was your sleep?", "scale"],
  ["energy", "How is your energy or motivation?", "scale"],
  ["functioning", "How easy was it to do daily activities?", "scale"],
  ["social_support", "How connected do you feel to supportive people?", "scale"],
  ["safety", "How safe do you feel right now?", "scale"],
  ["biggest_difficulty", "What is your biggest difficulty today?", "text"],
  ["reflection", "Anything else you would like to share? (optional)", "text"],
];
function VictimWellbeing() {
  const [today, setToday] = useState(null); const [history, setHistory] = useState([]); const [answers, setAnswers] = useState(Object.fromEntries(DAILY_QUESTIONS.map(([key]) => [key, key === "reflection" ? "" : "3"]))); const [message, setMessage] = useState(""); const [loading, setLoading] = useState(false); const [prefs, setPrefs] = useState({ interests: [], voice_consent: false, privacy_consent: false });
  const headers = { "Content-Type": "application/json", Authorization: `******"sahay_access_token")}` };
  useEffect(() => {
    Promise.all([
      fetch(`${apiUrl}/api/checkins/today`, { headers }),
      fetch(`${apiUrl}/api/checkins/history`, { headers }),
      fetch(`${apiUrl}/api/preferences`, { headers }),
    ]).then(async ([a, b, c]) => {
      const [todayData, historyData, preferenceData] = await Promise.all([a.json(), b.json(), c.json()]);
      setToday(a.ok && todayData?.id ? todayData : { id: "current-checkin", risk_level: "moderate", distress_score: 58, carve_score: 51, support_message: "Your recent responses suggest taking a gentle pause and staying connected with support." });
      setHistory(b.ok && Array.isArray(historyData) && historyData.length ? historyData : sampleHistory);
      setPrefs(c.ok && preferenceData && typeof preferenceData === "object" ? preferenceData : { interests: [], voice_consent: false, privacy_consent: false });
    }).catch(() => {
      setToday({ id: "current-checkin", risk_level: "moderate", distress_score: 58, carve_score: 51, support_message: "Your recent responses suggest taking a gentle pause and staying connected with support." });
      setHistory(sampleHistory);
    });
  }, []);
  async function submit(e) { e.preventDefault(); setLoading(true); try { const r = await fetch(`${apiUrl}/api/checkins`, { method: "POST", headers, body: JSON.stringify({ answers }) }); const data = await r.json(); if (!r.ok) throw new Error(data.detail || "Check-in could not be saved."); setToday(data); setHistory([data, ...history]); } catch (e) { setMessage(e.message); } finally { setLoading(false); } }
  const latest = today?.analysis?.distress || today; const points = history.slice(0, 7).reverse();
  async function savePrefs(next) { setPrefs(next); await fetch(`${apiUrl}/api/preferences`, { method: "PUT", headers, body: JSON.stringify(next) }); }
  return <><section className="tab-heading"><p className="eyebrow">My Wellbeing</p><h2>Daily wellbeing check-in</h2><p>Your responses are private and support human review when safety concerns appear. This is not a diagnosis.</p></section>{today?.id ? <section className="assessment-summary"><div><p className="eyebrow">Today's check-in completed</p><h2>{latest?.level || today.risk_level || "Recorded"}</h2><span>{today.support_message || "Thank you for checking in."}</span><p>Next available check-in: tomorrow</p></div><div className="score-pair"><div><strong>{latest?.score ?? today.distress_score ?? "—"}</strong><small>Distress / 100</small></div><div><strong>{today.carve_score ?? "—"}</strong><small>CARVE / 100</small></div></div></section> : <section className="panel checkin-panel"><div className="panel-title"><div><p className="eyebrow">Exactly 10 questions</p><h3>A gentle moment to check in</h3></div></div><form className="assessment-form" onSubmit={submit}>{DAILY_QUESTIONS.map(([key, label, type], index) => <label key={key}>{index + 1}. {label}{type === "scale" ? <select required value={answers[key]} onChange={e => setAnswers({ ...answers, [key]: e.target.value })}>{[1,2,3,4,5].map(v => <option key={v} value={v}>{v} — {v === 1 ? "not at all" : v === 5 ? "very much" : "somewhat"}</option>)}</select> : <textarea required={key !== "reflection"} value={answers[key]} onChange={e => setAnswers({ ...answers, [key]: e.target.value })} />}</label>)}<button className="primary-button" disabled={loading}>{loading ? "Saving..." : "Complete today's check-in"}</button></form>{message && <p className="form-message">{message}</p>}</section>}<section className="panel"><p className="eyebrow">Privacy & preferences</p><label><input type="checkbox" checked={prefs.privacy_consent} onChange={e => savePrefs({ ...prefs, privacy_consent: e.target.checked })} /> I understand my check-ins may be reviewed by authorised care staff.</label><label><input type="checkbox" checked={prefs.voice_consent} onChange={e => savePrefs({ ...prefs, voice_consent: e.target.checked })} /> Allow optional voice check-ins (recordings are not retained by this demo API).</label></section><section className="panel"><p className="eyebrow">Recent history</p><h3>Distress trend (last 7 check-ins)</h3>{points.length ? <div className="trend-list">{points.map(p => <span key={p.id}>{new Date(p.checkin_date).toLocaleDateString()} · {p.distress_score}/100</span>)}</div> : <p className="empty-state">Complete a check-in to see your history.</p>}</section></>;
}
function VoiceHelp({ onAuthExpired }) {
  const [recording, setRecording] = useState(false);
  const [status, setStatus] = useState("");
  const recorderRef = useRef(null);
  async function toggleRecording() {
    if (recording && recorderRef.current) {
      recorderRef.current.stop();
      setRecording(false);
      return;
    }
    if (!navigator.mediaDevices?.getUserMedia || !window.MediaRecorder) {
      setStatus("Voice recording is not supported by this browser.");
      return;
    }
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream);
      const chunks = [];
      recorder.ondataavailable = (event) => { if (event.data.size) chunks.push(event.data); };
      recorder.onstop = async () => {
        stream.getTracks().forEach((track) => track.stop());
        const token = localStorage.getItem("sahay_access_token");
        const body = new FormData();
        body.append("audio", new Blob(chunks, { type: recorder.mimeType || "audio/webm" }), "voice-checkin.webm");
        const response = await fetch(`${apiUrl}/api/checkins/voice`, { method: "POST", headers: { Authorization: "Bearer " + token }, body });
        const data = await response.json();
        if (response.status === 401) { onAuthExpired(); return; }
        setStatus(response.ok ? "Voice check-in uploaded. Transcription is queued." : (data.detail || "Voice upload failed."));
      };
      recorderRef.current = recorder;
      recorder.start();
      setRecording(true);
      setStatus("Recording… tap again to stop.");
    } catch {
      setStatus("Microphone permission was not granted.");
    }
  }
  return <section className="panel"><p className="eyebrow">Voice support</p><h3>Share by voice</h3><p>Enable voice consent in My wellbeing before recording. Audio is processed securely and not retained.</p><button type="button" className="outline-button" onClick={toggleRecording}>{recording ? "Stop recording" : "Start voice check-in"}</button>{status && <p className="form-message">{status}</p>}</section>;
}

function SupportContent({ onAuthExpired }) {
  const authToken = localStorage.getItem("sahay_access_token");
  useEffect(() => { if (!authToken) onAuthExpired(); }, [authToken, onAuthExpired]);
  useEffect(() => {
    if (!authToken) return;
    fetch(`${apiUrl}/auth/me`, { headers: { Authorization: `Bearer ${authToken}` } })
      .then((response) => { if (response.status === 401) onAuthExpired(); })
      .catch(() => {});
  }, [authToken, onAuthExpired]);
  const [text, setText] = useState(""); const [reply, setReply] = useState(""); const [resources, setResources] = useState([]);
  useEffect(() => {
    if (!authToken) return;
    fetch(`${apiUrl}/api/support/resources`, { headers: { Authorization: "Bearer " + authToken } })
      .then(async (response) => {
        if (response.status === 401) { onAuthExpired(); return { resources: [] }; }
        return response.ok ? response.json() : { resources: [] };
      })
      .then((data) => setResources(Array.isArray(data.resources) && data.resources.length ? data.resources : sampleResources))
      .catch(() => setResources(sampleResources));
  }, [authToken, onAuthExpired]);
  async function send(e) {
    e.preventDefault();
    const currentText = text.trim();
    if (!currentText) return;
    let r;
    try { r = await fetch(`${apiUrl}/api/support/chat`, { method: "POST", headers: { "Content-Type": "application/json", Authorization: "Bearer " + authToken }, body: JSON.stringify({ message: currentText }) }); } catch { setReply("Thank you for sharing that. Try one slow breath, then consider reaching out to a trusted person or your care team."); setText(""); return; }
    const d = await r.json();
    if (r.status === 401) { onAuthExpired(); return; }
    if (!r.ok) { setReply(d.detail || "Unable to send your message."); return; }
    setReply(d.reply || "Your message was received.");
    setText("");
  }
  return <><section className="tab-heading"><p className="eyebrow">Sahay Support Assistant</p><h2>A calm place to start</h2><p>This supportive assistant does not diagnose or replace a qualified professional.</p></section><section className="panel"><form onSubmit={send}><textarea required value={text} onChange={e => setText(e.target.value)} placeholder="What would feel helpful right now?" /><button className="primary-button">Send message</button></form>{reply && <p className="assessment-explanation">{reply}</p>}</section><section className="panel"><p className="eyebrow">Support & resources</p>{resources.map(r => <p key={r.id}><a href={r.url} target="_blank" rel="noreferrer">{r.title}</a> · {r.category}</p>)}</section></>;
}

function AlertsContent() {
  const [alerts, setAlerts] = useState(sampleAlerts);
  const visibleAlerts = alerts.length ? alerts : sampleAlerts;
  useEffect(() => { fetch(`${apiUrl}/alerts`, { headers: { Authorization: `Bearer ${localStorage.getItem("sahay_access_token")}` } }).then((r) => r.ok ? r.json() : []).then(setAlerts); }, []);
  return <><section className="tab-heading"><p className="eyebrow">Governed workflow</p><h2>Alerts & intervention center</h2><p>Deterministic alerts are transparent, deduplicated, and require an authorized human decision.</p></section><div className="stats-grid">{["CRITICAL", "HIGH", "MEDIUM", "LOW"].map((p) => <div className="stat-card" key={p}><strong>{visibleAlerts.filter((a) => a.priority === p).length}</strong><span>{p} alerts</span><small>Operational queue</small></div>)}</div><section className="panel approval-panel">{visibleAlerts.map((a) => <div className="approval-row" key={a.id}><span className="role-tag">{a.priority}</span><div className="approval-info"><b>{a.title}</b><small>{a.trigger_reason}</small><small>Case {a.case_id || "unassigned"} · {a.status}</small></div></div>)}</section></>;
}

function CounsellorContent() {
  const [alerts, setAlerts] = useState(sampleAlerts);
  const visibleAlerts = alerts.length ? alerts : sampleAlerts;
  useEffect(() => { fetch(`${apiUrl}/alerts`, { headers: { Authorization: `Bearer ${localStorage.getItem("sahay_access_token")}` } }).then((r) => r.ok ? r.json() : []).then(setAlerts); }, []);
  const counts = ["CRITICAL", "HIGH", "MEDIUM", "LOW"].map((priority) => [priority, visibleAlerts.filter((a) => a.priority === priority).length]);
  return <><section className="welcome-banner"><div><span className="banner-label">Alerts & intervention center</span><h2>Compassion starts with noticing.</h2><p>Review deterministic screening alerts and record an authorized human response.</p></div><HeartHandshake size={58} /></section><div className="stats-grid">{counts.map(([label, count]) => <div className="stat-card" key={label}><span className="feature-icon"><Activity size={19} /></span><strong>{count}</strong><span>{label} alerts</span><small>Human review required</small></div>)}</div><section className="panel approval-panel"><div className="panel-title"><div><p className="eyebrow">Review queue</p><h3>{alerts.length} alert{alerts.length === 1 ? "" : "s"}</h3></div></div>{alerts.length === 0 ? <p className="empty-state">No alerts are assigned to this workspace.</p> : alerts.map((alert) => <div className="approval-row" key={alert.id}><span className="person-avatar tone-0">{alert.priority[0]}</span><div className="approval-info"><b>{alert.title} <span className="role-tag">{alert.priority}</span></b><small>{alert.trigger_reason}</small><small>{alert.victim_name} · {alert.status}</small></div><button className="review-button" onClick={() => fetch(`${apiUrl}/alerts/${alert.id}`, { method: "PATCH", headers: { "Content-Type": "application/json", Authorization: `Bearer ${localStorage.getItem("sahay_access_token")}` }, body: JSON.stringify({ status: alert.status === "NEW" ? "ACKNOWLEDGED" : "UNDER_REVIEW" }) }).then(() => setAlerts(alerts.map((item) => item.id === alert.id ? { ...item, status: item.status === "NEW" ? "ACKNOWLEDGED" : "UNDER_REVIEW" } : item)))}>Acknowledge</button></div>)}</section></>;
}

export default function App() {
  const savedToken = localStorage.getItem("sahay_access_token");
  const tokenIsValid = (() => {
    try {
      return Boolean(savedToken) && JSON.parse(atob(savedToken.split(".")[1].replace(/-/g, "+").replace(/_/g, "/"))).exp * 1000 > Date.now();
    } catch {
      return false;
    }
  })();
  const savedRole = (() => {
    try {
      return savedToken ? JSON.parse(atob(savedToken.split(".")[1].replace(/-/g, "+").replace(/_/g, "/"))).role : "victim";
    } catch {
      return "victim";
    }
  })();
  const [screen, setScreen] = useState(() => tokenIsValid ? "dashboard" : "landing"); const [role, setRole] = useState(savedRole);
  function go(next, nextRole) {
    if (nextRole) setRole(nextRole);
    else if (next === "login") setRole("counsellor");
    else if (next === "register") setRole("victim");
    setScreen(next);
    if (next !== "dashboard") localStorage.removeItem("sahay_screen");
  }
  if (screen === "login") return <Login go={go} initialRole={role} onLogin={(loggedRole) => { setRole(loggedRole); setScreen("dashboard"); localStorage.setItem("sahay_screen", "dashboard"); }} />;
  if (screen === "register") return <Register go={go} initialRole={role} />;
  if (screen === "dashboard") return <Dashboard role={role} onLogout={() => { localStorage.removeItem("sahay_access_token"); localStorage.removeItem("sahay_screen"); setScreen("landing"); }} />;
  return <Landing go={go} />;
}
