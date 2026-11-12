import { useEffect, useMemo, useState } from 'react';
import axios from 'axios';

const API = axios.create({ baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8001/api/v1' });

function App() {
  const [authMode, setAuthMode] = useState('login');
  const [token, setToken] = useState(localStorage.getItem('cropshield-token') || '');
  const [user, setUser] = useState(JSON.parse(localStorage.getItem('cropshield-user') || 'null'));
  const [dashboard, setDashboard] = useState({ totalDiagnoses: 0, recent: [], weather: null });
  const [form, setForm] = useState({ name: '', email: 'farmer@demo.com', password: 'password123', location: 'Patna' });
  const [upload, setUpload] = useState({ cropName: 'Tomato', location: 'Patna', file: null });
  const [result, setResult] = useState(null);
  const [pestResult, setPestResult] = useState(null);
  const [info, setInfo] = useState('');
  const [loading, setLoading] = useState(false);

  const authHeaders = useMemo(() => ({ Authorization: `Bearer ${token}` }), [token]);

  const saveSession = (newToken, newUser) => {
    localStorage.setItem('cropshield-token', newToken);
    localStorage.setItem('cropshield-user', JSON.stringify(newUser));
    setToken(newToken);
    setUser(newUser);
  };

  const clearSession = () => {
    localStorage.removeItem('cropshield-token');
    localStorage.removeItem('cropshield-user');
    setToken('');
    setUser(null);
    setDashboard({ totalDiagnoses: 0, recent: [], weather: null });
    setResult(null);
    setPestResult(null);
  };

  const fetchDashboard = async () => {
    if (!token) return;
    try {
      const [historyResp, weatherResp] = await Promise.all([
        API.get('/diagnoses/history', { headers: authHeaders }),
        API.get('/weather/current', { headers: authHeaders, params: { latitude: 25.61, longitude: 85.13 } }),
      ]);
      setDashboard({
        totalDiagnoses: historyResp.data.diagnoses.length,
        recent: historyResp.data.diagnoses.slice(-3).reverse(),
        weather: weatherResp.data,
      });
    } catch (err) {
      setInfo('Unable to load farmer dashboard data.');
    }
  };

  useEffect(() => {
    if (token && user) {
      fetchDashboard();
    }
  }, [token, user]);

  const handleAuth = async (event) => {
    event.preventDefault();
    setLoading(true);
    try {
      const endpoint = authMode === 'login' ? '/auth/login' : '/auth/register';
      const payload = new FormData();
      if (authMode === 'register') payload.append('name', form.name);
      payload.append('email', form.email);
      payload.append('password', form.password);
      if (authMode === 'register') payload.append('location', form.location);

      const resp = await API.post(endpoint, payload, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });

      if (authMode === 'register') {
        setInfo('Registration successful. Please log in to continue.');
        setAuthMode('login');
      } else {
        saveSession(resp.data.access_token, resp.data.user);
        setInfo('Login successful.');
      }
    } catch (err) {
      setInfo(err.response?.data?.detail || 'Authentication failed.');
    } finally {
      setLoading(false);
    }
  };

  const handleDetect = async (event) => {
    event.preventDefault();
    if (!upload.file) {
      setInfo('Select an image before submitting.');
      return;
    }
    setLoading(true);
    try {
      const fd = new FormData();
      fd.append('crop_name', upload.cropName);
      fd.append('location', upload.location);
      fd.append('file', upload.file);
      const resp = await API.post('/diagnoses/detect', fd, {
        headers: { ...authHeaders, 'Content-Type': 'multipart/form-data' },
      });
      setResult(resp.data);
      setPestResult(null);
      setInfo(resp.data.prediction.message || 'Diagnosis processed.');
      await fetchDashboard();
    } catch (err) {
      setInfo(err.response?.data?.detail || 'Could not process the image.');
    } finally {
      setLoading(false);
    }
  };

  const handlePestDetect = async () => {
    if (!upload.file) {
      setInfo('Select an image before running the pest scan.');
      return;
    }
    setLoading(true);
    try {
      const fd = new FormData();
      fd.append('crop_name', upload.cropName);
      fd.append('location', upload.location);
      fd.append('file', upload.file);
      const resp = await API.post('/diagnoses/pest-detect', fd, {
        headers: { ...authHeaders, 'Content-Type': 'multipart/form-data' },
      });
      setPestResult(resp.data);
      setInfo(resp.data.prediction.message || 'Pest scan complete.');
    } catch (err) {
      setInfo(err.response?.data?.detail || 'Could not run the pest scan.');
    } finally {
      setLoading(false);
    }
  };

  if (!token || !user) {
    return (
      <div className="min-h-screen bg-slate-100 text-slate-900">
        <div className="mx-auto flex min-h-screen max-w-6xl items-center justify-center p-6">
          <div className="grid w-full overflow-hidden rounded-3xl bg-white shadow-2xl lg:grid-cols-2">
            <div className="bg-gradient-to-br from-emerald-700 via-green-700 to-lime-600 p-10 text-white">
              <p className="text-sm uppercase tracking-[0.3em] text-emerald-100">CropShield AI</p>
              <h1 className="mt-6 text-4xl font-bold">Farmer portal</h1>
              <p className="mt-4 max-w-md text-emerald-50">
                Detect crop disease, review weather risk, and receive actionable guidance for better field decisions.
              </p>
              <div className="mt-8 space-y-4 text-sm text-emerald-50">
                <div>• Disease detection workflow</div>
                <div>• Weather-based risk scoring</div>
                <div>• Recommendations and history</div>
              </div>
            </div>

            <div className="p-8 md:p-10">
              <div className="mb-6 flex gap-3 rounded-full bg-emerald-50 p-1">
                <button className={`flex-1 rounded-full px-4 py-2 font-medium ${authMode === 'login' ? 'bg-emerald-600 text-white' : 'text-slate-600'}`} onClick={() => setAuthMode('login')}>Login</button>
                <button className={`flex-1 rounded-full px-4 py-2 font-medium ${authMode === 'register' ? 'bg-emerald-600 text-white' : 'text-slate-600'}`} onClick={() => setAuthMode('register')}>Register</button>
              </div>

              <form className="space-y-4" onSubmit={handleAuth}>
                {authMode === 'register' && (
                  <input className="w-full rounded-xl border border-slate-200 px-4 py-3" placeholder="Full name" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
                )}
                <input className="w-full rounded-xl border border-slate-200 px-4 py-3" type="email" placeholder="Email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} />
                <input className="w-full rounded-xl border border-slate-200 px-4 py-3" type="password" placeholder="Password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} />
                {authMode === 'register' && (
                  <input className="w-full rounded-xl border border-slate-200 px-4 py-3" placeholder="Location" value={form.location} onChange={(e) => setForm({ ...form, location: e.target.value })} />
                )}
                <button className="w-full rounded-xl bg-emerald-600 px-4 py-3 font-semibold text-white hover:bg-emerald-700" type="submit" disabled={loading}>{loading ? 'Please wait...' : authMode === 'login' ? 'Login' : 'Create account'}</button>
              </form>

              {info && <div className="mt-4 rounded-xl bg-amber-50 p-3 text-sm text-amber-700">{info}</div>}
            </div>
          </div>
        </div>
      </div>
    );
  }

  const weatherData = dashboard.weather || { risk: { category: 'Moderate', score: 58, explanation: 'Weather is moderate.' } };

  return (
    <div className="min-h-screen bg-[radial-gradient(circle_at_top,_#ecfdf5_0%,_#f8fafc_36%,_#f1f5f9_100%)] text-slate-900">
      <div className="mx-auto max-w-7xl px-4 py-6">
        <header className="mb-6 flex flex-col justify-between gap-4 rounded-[28px] bg-gradient-to-r from-emerald-700 via-green-700 to-lime-600 p-6 text-white shadow-2xl md:flex-row md:items-center">
          <div>
            <p className="text-xs uppercase tracking-[0.35em] text-emerald-100">CropShield AI</p>
            <h2 className="mt-2 text-3xl font-bold">Welcome back, {user.name}</h2>
            <p className="mt-2 max-w-xl text-sm text-emerald-50">Monitor field health, detect crop issues, and prioritize interventions with clearer insights.</p>
          </div>
          <button className="rounded-xl border border-white/20 bg-white/10 px-4 py-2 font-medium text-white backdrop-blur-sm transition hover:bg-white/20" onClick={clearSession}>Logout</button>
        </header>

        <section className="mb-6 grid gap-4 md:grid-cols-4">
          <StatTile label="Diagnoses" value={dashboard.totalDiagnoses} tone="emerald" />
          <StatTile label="Weather risk" value={weatherData.risk.category} tone="amber" />
          <StatTile label="Humidity" value={`${weatherData.humidity ?? 70}%`} tone="cyan" />
          <StatTile label="Location" value={user.location || 'Patna'} tone="slate" />
        </section>

        <section className="grid gap-6 lg:grid-cols-[1.2fr_0.8fr]">
          <div className="rounded-[28px] border border-slate-200/80 bg-white/90 p-6 shadow-lg backdrop-blur-sm">
            <div className="mb-4 flex items-center justify-between">
              <h3 className="text-xl font-bold text-slate-900">Crop disease detection</h3>
              <span className="rounded-full bg-emerald-100 px-3 py-1 text-xs font-semibold uppercase tracking-wide text-emerald-700">AI check</span>
            </div>
            <form className="space-y-4" onSubmit={handleDetect}>
              <div className="grid gap-4 md:grid-cols-2">
                <input className="rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-slate-800 outline-none transition focus:border-emerald-400 focus:bg-white" placeholder="Crop name" value={upload.cropName} onChange={(e) => setUpload({ ...upload, cropName: e.target.value })} />
                <input className="rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-slate-800 outline-none transition focus:border-emerald-400 focus:bg-white" placeholder="Location" value={upload.location} onChange={(e) => setUpload({ ...upload, location: e.target.value })} />
              </div>
              <input className="w-full rounded-xl border border-dashed border-slate-300 bg-slate-50 p-4 text-sm text-slate-600 file:mr-3 file:rounded-lg file:border-0 file:bg-emerald-600 file:px-3 file:py-2 file:text-sm file:font-medium file:text-white" type="file" accept="image/png,image/jpeg" onChange={(e) => setUpload({ ...upload, file: e.target.files[0] })} />
              <button className="w-full rounded-xl bg-emerald-600 px-4 py-3 font-semibold text-white shadow-md transition hover:bg-emerald-700 disabled:cursor-not-allowed disabled:opacity-70" type="submit" disabled={loading}>{loading ? 'Processing...' : 'Upload and detect'}</button>
            </form>
            {result && (
              <div className="mt-6 rounded-2xl border border-emerald-200 bg-emerald-50 p-4 shadow-sm">
                <div className="flex items-center justify-between gap-4">
                  <div>
                    <p className="text-sm text-emerald-700">Prediction status</p>
                    <h4 className="text-2xl font-bold text-emerald-900">{result.prediction.label || 'Unavailable'}</h4>
                  </div>
                  <div className="rounded-full bg-white px-3 py-2 text-lg font-bold text-emerald-700">{result.prediction.confidence || 0}%</div>
                </div>
                <p className="mt-3 text-sm text-emerald-800">{result.prediction.message}</p>
                <div className="mt-4 grid gap-3 md:grid-cols-2">
                  <div><p className="font-semibold text-emerald-900">Symptoms</p><ul className="list-disc pl-5 text-sm text-slate-700">{(result.prediction.symptoms || []).map((item, idx) => <li key={idx}>{item}</li>)}</ul></div>
                  <div><p className="font-semibold text-emerald-900">Recommendations</p><ul className="list-disc pl-5 text-sm text-slate-700">{(result.prediction.recommendations || []).map((item, idx) => <li key={idx}>{item}</li>)}</ul></div>
                </div>
              </div>
            )}

            <div className="mt-4 rounded-2xl border border-violet-200 bg-violet-50 p-4 shadow-sm">
              <div className="flex items-center justify-between gap-3">
                <div>
                  <p className="text-sm font-medium text-violet-700">Pest monitoring</p>
                  <h4 className="text-xl font-bold text-violet-900">Field pest scan</h4>
                </div>
                <button type="button" onClick={handlePestDetect} className="rounded-xl bg-violet-600 px-3 py-2 text-sm font-semibold text-white hover:bg-violet-700">Run scan</button>
              </div>
              {pestResult && (
                <div className="mt-3 rounded-xl bg-white/75 p-3 text-sm text-violet-900">
                  <div className="font-semibold">{pestResult.prediction.label}</div>
                  <div className="mt-1 text-violet-700">{pestResult.prediction.message}</div>
                </div>
              )}
            </div>
          </div>

          <div className="space-y-6">
            <div className="rounded-[28px] border border-slate-200/80 bg-white/90 p-5 shadow-lg backdrop-blur-sm">
              <h3 className="mb-4 text-xl font-bold">Weather & risk</h3>
              <div className="space-y-3">
                <MetricRow label="Temperature" value={`${weatherData.temperature ?? 28}°C`} accent="amber" />
                <MetricRow label="Humidity" value={`${weatherData.humidity ?? 70}%`} accent="cyan" />
                <MetricRow label="Risk category" value={weatherData.risk.category} accent="emerald" />
              </div>
              <p className="mt-4 text-sm leading-6 text-slate-600">{weatherData.risk.explanation}</p>
            </div>

            <div className="rounded-[28px] border border-slate-200/80 bg-white/90 p-5 shadow-lg backdrop-blur-sm">
              <div className="mb-4 flex items-center justify-between">
                <h3 className="text-xl font-bold">Field risk map</h3>
                <span className="text-xs uppercase tracking-wide text-slate-500">GIS view</span>
              </div>
              <div className="relative h-40 overflow-hidden rounded-2xl border border-slate-200 bg-[linear-gradient(135deg,#e0f2fe_0%,#ecfeff_35%,#f0fdf4_100%)]">
                <div className="absolute left-6 top-7 h-2.5 w-2.5 rounded-full bg-emerald-500 shadow-[0_0_0_6px_rgba(16,185,129,0.18)]" />
                <div className="absolute left-16 top-16 h-2.5 w-2.5 rounded-full bg-amber-400 shadow-[0_0_0_6px_rgba(251,191,36,0.18)]" />
                <div className="absolute right-12 top-10 h-2.5 w-2.5 rounded-full bg-red-400 shadow-[0_0_0_6px_rgba(248,113,113,0.18)]" />
                <div className="absolute bottom-5 left-1/2 h-12 w-12 -translate-x-1/2 rounded-full border border-dashed border-emerald-400/80 bg-white/30" />
                <div className="absolute inset-0 opacity-40 [background-image:linear-gradient(rgba(148,163,184,0.18)_1px,transparent_1px),linear-gradient(90deg,rgba(148,163,184,0.18)_1px,transparent_1px)] [background-size:22px_22px]" />
              </div>
              <div className="mt-4 grid grid-cols-3 gap-2 text-center text-xs text-slate-600">
                <div className="rounded-xl bg-emerald-50 p-2"><div className="font-bold text-emerald-700">Low</div><div>North</div></div>
                <div className="rounded-xl bg-amber-50 p-2"><div className="font-bold text-amber-700">Medium</div><div>Central</div></div>
                <div className="rounded-xl bg-red-50 p-2"><div className="font-bold text-red-700">High</div><div>South</div></div>
              </div>
            </div>
          </div>
        </section>

        <section className="mt-6 grid gap-6 lg:grid-cols-2">
          <div className="rounded-[28px] border border-slate-200/80 bg-white/90 p-6 shadow-lg backdrop-blur-sm">
            <h3 className="mb-4 text-xl font-bold">Recent diagnoses</h3>
            <div className="space-y-3">
              {(dashboard.recent || []).length === 0 ? <div className="text-slate-500">No diagnosis records yet.</div> : dashboard.recent.map((row) => (
                <div key={row.id} className="rounded-2xl border border-slate-200 bg-slate-50 p-3">
                  <div className="flex items-center justify-between"><span className="font-semibold text-slate-800">{row.crop_name}</span><span className="text-sm text-slate-500">{row.confidence}%</span></div>
                  <div className="mt-1 text-sm text-slate-600">{row.disease_name}</div>
                </div>
              ))}
            </div>
          </div>

          <div className="rounded-[28px] border border-slate-200/80 bg-white/90 p-6 shadow-lg backdrop-blur-sm">
            <div className="mb-4 flex items-center justify-between">
              <h3 className="text-xl font-bold">Agricultural recommendations</h3>
              <span className="rounded-full bg-amber-100 px-2 py-1 text-xs font-semibold uppercase tracking-wide text-amber-700">Action plan</span>
            </div>
            <div className="text-sm leading-6 text-slate-600">
              {result ? (
                <div>
                  <p className="mb-4 font-semibold text-slate-800">{result.prediction.crop} · {result.prediction.label}</p>
                  {result.prediction.action_plan?.length ? (
                    <div className="space-y-4">
                      {result.prediction.action_plan.map((phase, idx) => (
                        <div key={idx} className="rounded-2xl border border-emerald-100 bg-emerald-50/60 p-4">
                          <h4 className="font-semibold text-emerald-900">{idx + 1}. {phase.timing}</h4>
                          <ul className="mt-2 list-disc space-y-1.5 pl-5 text-slate-700">
                            {phase.steps.map((step, stepIdx) => <li key={stepIdx}>{step}</li>)}
                          </ul>
                        </div>
                      ))}
                      {result.prediction.follow_up && <p className="font-medium text-slate-700">Follow-up: {result.prediction.follow_up}</p>}
                      {result.prediction.safety_note && <p className="rounded-xl border border-amber-200 bg-amber-50 p-3 text-amber-900">{result.prediction.safety_note}</p>}
                    </div>
                  ) : (
                    <ul className="list-disc space-y-2 pl-5">
                      {(result.prediction.recommendations || []).map((item, idx) => <li key={idx}>{item}</li>)}
                    </ul>
                  )}
                </div>
              ) : (
                <div>No diagnosis result yet. Please upload an image to view recommendations.</div>
              )}
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}

function StatTile({ label, value, tone }) {
  const tones = {
    emerald: 'bg-emerald-50 text-emerald-700',
    amber: 'bg-amber-50 text-amber-700',
    cyan: 'bg-cyan-50 text-cyan-700',
    slate: 'bg-slate-100 text-slate-700',
  };

  return (
    <div className="rounded-[24px] border border-slate-200/80 bg-white/90 p-5 shadow-lg backdrop-blur-sm">
      <div className={`inline-flex rounded-full px-2.5 py-1 text-xs font-semibold uppercase tracking-wide ${tones[tone] || tones.slate}`}>{label}</div>
      <div className="mt-3 text-2xl font-bold text-slate-900">{value}</div>
    </div>
  );
}

function MetricRow({ label, value, accent }) {
  const accents = {
    amber: 'bg-amber-50 text-amber-700',
    cyan: 'bg-cyan-50 text-cyan-700',
    emerald: 'bg-emerald-50 text-emerald-700',
  };

  return (
    <div className="flex items-center justify-between rounded-xl border border-slate-200 bg-slate-50 p-3">
      <span className="text-sm text-slate-600">{label}</span>
      <span className={`rounded-full px-2.5 py-1 text-sm font-semibold ${accents[accent] || accents.emerald}`}>{value}</span>
    </div>
  );
}

export default App;
