import { useEffect, useState } from 'react';
import axios from 'axios';
import { BarChart, Bar, ResponsiveContainer, XAxis, YAxis, CartesianGrid, Tooltip } from 'recharts';

const API = axios.create({ baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8001/api/v1' });

function App() {
  const [token, setToken] = useState(localStorage.getItem('cropshield-admin-token') || '');
  const [user, setUser] = useState(JSON.parse(localStorage.getItem('cropshield-admin-user') || 'null'));
  const [form, setForm] = useState({ email: 'admin@cropshield.ai', password: 'admin123' });
  const [stats, setStats] = useState(null);
  const [info, setInfo] = useState('');

  const authHeaders = { Authorization: `Bearer ${token}` };

  const fetchDashboard = async () => {
    if (!token) return;
    try {
      const resp = await API.get('/admin/dashboard', { headers: authHeaders });
      setStats(resp.data);
    } catch (err) {
      setInfo(err.response?.data?.detail || 'Unable to load admin dashboard.');
    }
  };

  useEffect(() => {
    if (token) fetchDashboard();
  }, [token]);

  const handleLogin = async (event) => {
    event.preventDefault();
    try {
      const payload = new FormData();
      payload.append('email', form.email);
      payload.append('password', form.password);
      const resp = await API.post('/auth/login', payload, { headers: { 'Content-Type': 'multipart/form-data' } });
      const adminUser = resp.data.user;
      if (adminUser.role !== 'ADMIN') {
        throw new Error('This portal is for admin users only.');
      }
      localStorage.setItem('cropshield-admin-token', resp.data.access_token);
      localStorage.setItem('cropshield-admin-user', JSON.stringify(adminUser));
      setToken(resp.data.access_token);
      setUser(adminUser);
      setInfo('Admin login successful.');
    } catch (err) {
      setInfo(err.response?.data?.detail || err.message || 'Authentication failed.');
    }
  };

  if (!token || !user) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-slate-100 p-6">
        <div className="w-full max-w-md rounded-3xl bg-white p-8 shadow-xl">
          <p className="text-sm uppercase tracking-[0.25em] text-emerald-600">CropShield AI</p>
          <h1 className="mt-4 text-3xl font-bold text-slate-900">Admin login</h1>
          <form className="mt-6 space-y-4" onSubmit={handleLogin}>
            <input className="w-full rounded-xl border border-slate-200 px-4 py-3" type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} />
            <input className="w-full rounded-xl border border-slate-200 px-4 py-3" type="password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} />
            <button className="w-full rounded-xl bg-emerald-600 px-4 py-3 font-semibold text-white" type="submit">Login</button>
          </form>
          {info && <div className="mt-4 rounded-xl bg-amber-50 p-3 text-sm text-amber-700">{info}</div>}
        </div>
      </div>
    );
  }

  const charts = Object.entries(stats?.summary?.disease_stats || {}).map(([name, value]) => ({ name, value }));

  return (
    <div className="min-h-screen bg-[radial-gradient(circle_at_top,_#ecfdf5_0%,_#f8fafc_40%,_#eef2ff_100%)] p-6 text-slate-900">
      <div className="mx-auto max-w-7xl">
        <header className="mb-6 flex items-center justify-between rounded-[28px] bg-gradient-to-r from-emerald-700 via-green-700 to-lime-600 p-6 text-white shadow-xl">
          <div>
            <p className="text-xs uppercase tracking-[0.3em] text-emerald-100">Admin portal</p>
            <h2 className="mt-2 text-3xl font-bold">CropShield Dashboard</h2>
          </div>
          <button className="rounded-xl bg-white/10 px-4 py-2 transition hover:bg-white/20" onClick={() => {
            localStorage.removeItem('cropshield-admin-token');
            localStorage.removeItem('cropshield-admin-user');
            setToken('');
            setUser(null);
          }}>Logout</button>
        </header>

        <section className="mb-6 grid gap-4 md:grid-cols-4">
          <StatCard label="Farmers" value={stats?.summary?.total_farmers ?? 0} />
          <StatCard label="Diagnoses" value={stats?.summary?.total_diagnoses ?? 0} />
          <StatCard label="Hotspots" value={stats?.hotspots?.length ?? 0} />
          <StatCard label="Expert queue" value={stats?.expert_queue?.length ?? 0} />
        </section>

        <section className="grid gap-6 lg:grid-cols-[1.2fr_0.8fr]">
          <div className="rounded-[28px] border border-slate-200/80 bg-white/90 p-6 shadow-lg backdrop-blur-sm">
            <h3 className="mb-4 text-xl font-bold">Disease statistics</h3>
            <div className="h-72">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={charts}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="value" fill="#10b981" radius={[8,8,0,0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
          <div className="rounded-[28px] border border-slate-200/80 bg-white/90 p-6 shadow-lg backdrop-blur-sm">
            <h3 className="mb-4 text-xl font-bold">Recent activities</h3>
            <div className="space-y-3">
              {(stats?.recent_activity || []).slice(0, 5).map((item) => (
                <div className="rounded-xl border border-slate-200 bg-slate-50 p-3" key={item.id}>
                  <div className="font-semibold text-slate-800">{item.crop_name}</div>
                  <div className="text-sm text-slate-600">{item.disease_name}</div>
                </div>
              ))}
            </div>
          </div>
        </section>

        <section className="mt-6 grid gap-6 lg:grid-cols-[1.1fr_0.9fr]">
          <div className="rounded-[28px] border border-slate-200/80 bg-white/90 p-6 shadow-lg backdrop-blur-sm">
            <h3 className="mb-4 text-xl font-bold">Field hotspot alerts</h3>
            <div className="space-y-3">
              {(stats?.hotspots || []).map((hotspot) => (
                <div className="rounded-2xl border border-amber-200 bg-amber-50 p-3" key={hotspot.region}>
                  <div className="flex items-center justify-between">
                    <span className="font-semibold text-slate-800">{hotspot.region}</span>
                    <span className="rounded-full bg-amber-100 px-2 py-1 text-xs font-semibold text-amber-800">{hotspot.risk_score}/100</span>
                  </div>
                  <div className="mt-2 text-sm text-slate-600">{hotspot.disease} · {hotspot.trend}</div>
                  <div className="mt-1 text-sm text-slate-700">{hotspot.note}</div>
                </div>
              ))}
            </div>
          </div>

          <div className="rounded-[28px] border border-slate-200/80 bg-white/90 p-6 shadow-lg backdrop-blur-sm">
            <h3 className="mb-4 text-xl font-bold">Expert validation queue</h3>
            <div className="space-y-3">
              {(stats?.expert_queue || []).map((item) => (
                <div className="rounded-2xl border border-slate-200 bg-slate-50 p-3" key={item.id}>
                  <div className="flex items-center justify-between">
                    <span className="font-semibold text-slate-800">{item.disease_name}</span>
                    <span className="text-xs font-semibold uppercase tracking-wide text-emerald-700">{item.priority}</span>
                  </div>
                  <div className="mt-1 text-sm text-slate-600">{item.farmer_name} · {item.region}</div>
                  <div className="mt-1 text-sm text-slate-500">{item.status}</div>
                </div>
              ))}
            </div>
          </div>
        </section>

        <section className="mt-6 rounded-[28px] border border-slate-200/80 bg-white/90 p-6 shadow-lg backdrop-blur-sm">
          <h3 className="mb-4 text-xl font-bold">Registered farmers</h3>
          <div className="overflow-x-auto">
            <table className="min-w-full text-left text-sm">
              <thead>
                <tr className="border-b border-slate-200 text-slate-500">
                  <th className="py-2">Name</th>
                  <th>Email</th>
                  <th>Location</th>
                </tr>
              </thead>
              <tbody>
                {(stats?.farmers || []).map((farmer) => (
                  <tr key={farmer.id} className="border-b border-slate-100">
                    <td className="py-3">{farmer.name}</td>
                    <td>{farmer.email}</td>
                    <td>{farmer.location || 'N/A'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      </div>
    </div>
  );
}

function StatCard({ label, value }) {
  return (
    <div className="rounded-2xl bg-white p-5 shadow-sm">
      <div className="text-sm text-slate-500">{label}</div>
      <div className="mt-2 text-3xl font-bold">{value}</div>
    </div>
  );
}

export default App;
