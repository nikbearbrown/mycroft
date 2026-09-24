import { useState, useEffect, useRef } from 'react';
import './App.css';

const API_BASE = import.meta.env.VITE_API_BASE || 'http://127.0.0.1:8000';
const OUTCOMES = ['approve', 'deny', 'manual_review'];
const JSON_HEADERS = { 'Content-Type': 'application/json' };
const OUTCOME_TONE = { approve: 'good', deny: 'bad', manual_review: 'warn' };

/* ---------- tiny fetch helper (throws on non-OK so callers can show errors) ---------- */
async function api(path, options, signal) {
  const res = await fetch(`${API_BASE}${path}`, { ...options, signal });
  if (!res.ok) {
    let detail = res.statusText;
    try { const j = await res.json(); detail = j.detail || j.error || detail; } catch { /* ignore */ }
    throw new Error(detail);
  }
  return res.status === 204 ? null : res.json();
}

/* ---------- helpers ---------- */
function cap(s) {
  if (!s) return s;
  return s.charAt(0).toUpperCase() + s.slice(1).replace(/_/g, ' ');
}
function outcomeTone(o) { return OUTCOME_TONE[(o || '').toLowerCase()] || 'warn'; }
function coerce(v) {
  const t = v.trim();
  if (t === '') return t;
  if (t === 'true') return true;
  if (t === 'false') return false;
  if (!isNaN(Number(t))) return Number(t);
  return t;
}
function fmtVal(v) {
  if (typeof v === 'number') return v.toLocaleString();
  if (typeof v === 'boolean') return v ? 'yes' : 'no';
  return String(v);
}
function slugify(text) {
  return text.toLowerCase().trim().replace(/[^a-z0-9\s]/g, '').replace(/\s+/g, '_').slice(0, 40);
}

// Join the two independent checks per applicant.
function mergeChecks(rawResults) {
  const byApplicant = {};
  for (const r of rawResults) {
    const row = byApplicant[r.applicant_id] || { applicant_id: r.applicant_id, expected: r.oracle_expected };
    if (r.check_type === 'validation') {
      row.codeObserved = r.agent_observed;
      row.codeMatch = r.match;
    } else if (r.check_type === 'simulation') {
      row.reasonObserved = r.agent_observed;
      row.reasonMatch = r.match;
      row.reasonRationale = r.rationale;
    }
    byApplicant[r.applicant_id] = row;
  }
  return Object.values(byApplicant);
}

// The 2x2: where the two checks agree/disagree tells us what's wrong.
function diagnose(row) {
  if (row.codeObserved === 'unrunnable') {
    return { label: "Code wouldn't run", tone: 'bad', explanation: "The AI produced code that isn't valid Python, so it couldn't be tested at all." };
  }
  const { codeMatch, reasonMatch } = row;
  if (codeMatch && reasonMatch) {
    return { label: 'Trustworthy', tone: 'good', explanation: 'The code, the rule, and your answer all agree.' };
  }
  if (!codeMatch && reasonMatch) {
    return { label: 'Code bug caught', tone: 'bad', explanation: "The rule was clear, but the AI's code got this one wrong." };
  }
  if (codeMatch && !reasonMatch) {
    return { label: 'Rule may be ambiguous', tone: 'warn', explanation: 'The code matches your answer, but reading the rule plainly gives a different outcome — the wording may be unclear.' };
  }
  return { label: 'Answer key looks wrong', tone: 'bad', explanation: 'Both checks disagree with your answer — your expected outcome or the rule itself is probably off.' };
}

/* ---------- one-click demo rules (the 5 canonical rules + example answers) ---------- */
const DEMO_RULES = [
  { rule_id: 'dti_43', rule_text: 'If debt is more than 43 percent of income, deny the loan.', cases: [
    { applicant_id: 'Raj', applicant_data: { income: 100000, debt: 50000 }, expected_outcome: 'deny' },
    { applicant_id: 'Meera', applicant_data: { income: 100000, debt: 30000 }, expected_outcome: 'approve' },
    { applicant_id: 'Alex', applicant_data: { income: 100000, debt: 43000 }, expected_outcome: 'approve' },
  ] },
  { rule_id: 'loan_over_50k', rule_text: 'If the loan amount requested is more than $50,000, send the application for manual review.', cases: [
    { applicant_id: 'Priya', applicant_data: { loan_amount: 60000 }, expected_outcome: 'manual_review' },
    { applicant_id: 'Tom', applicant_data: { loan_amount: 30000 }, expected_outcome: 'approve' },
    { applicant_id: 'Sam', applicant_data: { loan_amount: 50000 }, expected_outcome: 'approve' },
  ] },
  { rule_id: 'credit_score_750', rule_text: 'If the applicant credit score is above 750, approve the loan.', cases: [
    { applicant_id: 'Nina', applicant_data: { credit_score: 780 }, expected_outcome: 'approve' },
    { applicant_id: 'Leo', applicant_data: { credit_score: 720 }, expected_outcome: 'deny' },
    { applicant_id: 'Maya', applicant_data: { credit_score: 750 }, expected_outcome: 'deny' },
  ] },
  { rule_id: 'recent_late_payment', rule_text: 'If the applicant has had a recent late payment, deny the loan.', cases: [
    { applicant_id: 'Ravi', applicant_data: { days_since_late_payment: 10 }, expected_outcome: 'deny' },
    { applicant_id: 'Sara', applicant_data: { days_since_late_payment: 400 }, expected_outcome: 'approve' },
    { applicant_id: 'Jay', applicant_data: { days_since_late_payment: 90 }, expected_outcome: 'deny' },
  ] },
  { rule_id: 'compound_income_credit_debt', rule_text: 'Approve the loan if income is above 80000 and credit score is above 700, or if they have no existing debt.', cases: [
    { applicant_id: 'Ken', applicant_data: { income: 90000, credit_score: 720, existing_debt: 5000 }, expected_outcome: 'approve' },
    { applicant_id: 'Ana', applicant_data: { income: 40000, credit_score: 650, existing_debt: 0 }, expected_outcome: 'approve' },
    { applicant_id: 'Rav', applicant_data: { income: 40000, credit_score: 650, existing_debt: 3000 }, expected_outcome: 'deny' },
  ] },
];

/* ---------- app ---------- */
function App() {
  const [rules, setRules] = useState([]);
  const [selectedRuleId, setSelectedRuleId] = useState(null);
  const [testCases, setTestCases] = useState([]);
  const [results, setResults] = useState(null);
  const [isRunning, setIsRunning] = useState(false);
  const [isFreezing, setIsFreezing] = useState(false);
  const [loadingDemo, setLoadingDemo] = useState(false);
  const [showCode, setShowCode] = useState(false);
  const [showLegend, setShowLegend] = useState(false);
  const [error, setError] = useState(null);
  const [editingRule, setEditingRule] = useState(false);
  const [editRuleText, setEditRuleText] = useState('');

  const [newRuleText, setNewRuleText] = useState('');
  const [showAddExample, setShowAddExample] = useState(false);

  const [tcName, setTcName] = useState('');
  const [tcExpected, setTcExpected] = useState('approve');
  const [tcFields, setTcFields] = useState([{ id: 1, key: '', value: '' }]);
  const [tcError, setTcError] = useState('');
  const nextFieldId = useRef(2);

  useEffect(() => { fetchRules(); }, []);

  // Fetch test cases + results when the selected rule changes; abort on switch to avoid races.
  useEffect(() => {
    if (!selectedRuleId) return;
    const ctrl = new AbortController();
    setShowAddExample(false);
    setShowCode(false);
    setEditingRule(false);
    (async () => {
      try {
        const [tc, res] = await Promise.all([
          api(`/test-cases/${selectedRuleId}`, {}, ctrl.signal),
          api(`/results/${selectedRuleId}`, {}, ctrl.signal),
        ]);
        setTestCases(Array.isArray(tc) ? tc : []);
        setResults(res && res.generated_code ? res : null);
      } catch (e) {
        if (e.name !== 'AbortError') setError(e.message);
      }
    })();
    return () => ctrl.abort();
  }, [selectedRuleId]);

  async function fetchRules() {
    try { setRules(await api('/rules')); }
    catch (e) { setError(e.message); }
  }
  async function refreshSelected() {
    if (!selectedRuleId) return;
    try {
      const [tc, res] = await Promise.all([
        api(`/test-cases/${selectedRuleId}`),
        api(`/results/${selectedRuleId}`),
      ]);
      setTestCases(Array.isArray(tc) ? tc : []);
      setResults(res && res.generated_code ? res : null);
    } catch (e) { setError(e.message); }
  }

  async function handleNewRule(e) {
    e.preventDefault();
    if (!newRuleText.trim()) return;
    const cleanText = newRuleText.trim();
    const generatedId = slugify(cleanText) + '_' + Date.now().toString().slice(-4);
    try {
      await api('/rules', { method: 'POST', headers: JSON_HEADERS, body: JSON.stringify({ rule_id: generatedId, rule_text: cleanText }) });
      setNewRuleText('');
      setError(null);
      fetchRules();
    } catch (e) { setError(e.message); }
  }

  async function loadDemoRules() {
    setLoadingDemo(true); setError(null);
    try {
      for (const d of DEMO_RULES) {
        let created;
        try {
          created = await api('/rules', { method: 'POST', headers: JSON_HEADERS, body: JSON.stringify({ rule_id: d.rule_id, rule_text: d.rule_text }) });
        } catch { continue; } // already loaded — skip its cases
        for (const c of d.cases) {
          await api('/test-cases', { method: 'POST', headers: JSON_HEADERS, body: JSON.stringify({ oracle_id: created.id, ...c }) });
        }
      }
      await fetchRules();
    } catch (e) { setError(e.message); }
    finally { setLoadingDemo(false); }
  }

  /* key/value field editing */
  function updateField(id, prop, val) {
    setTcFields((prev) => prev.map((f) => (f.id === id ? { ...f, [prop]: val } : f)));
  }
  function addField() {
    setTcFields((prev) => [...prev, { id: nextFieldId.current++, key: '', value: '' }]);
  }
  function removeField(id) {
    setTcFields((prev) => (prev.length === 1 ? prev : prev.filter((f) => f.id !== id)));
  }
  function resetExampleForm() {
    setTcName(''); setTcExpected('approve'); setTcFields([{ id: nextFieldId.current++, key: '', value: '' }]); setTcError('');
    setShowAddExample(false);
  }

  async function handleSubmitTestCase(e) {
    e.preventDefault();
    setTcError('');
    if (!tcName.trim()) { setTcError('Please enter a name.'); return; }
    const data = {};
    for (const f of tcFields) {
      if (f.key.trim() === '') continue;
      data[f.key.trim()] = coerce(f.value);
    }
    if (Object.keys(data).length === 0) { setTcError('Add at least one field (e.g. income = 80000).'); return; }
    const rule = rules.find((r) => r.rule_id === selectedRuleId);
    try {
      await api('/test-cases', { method: 'POST', headers: JSON_HEADERS, body: JSON.stringify({
        oracle_id: rule.id, applicant_id: tcName.trim(), applicant_data: data, expected_outcome: tcExpected }) });
      resetExampleForm();
      refreshSelected();
    } catch (e) { setTcError(e.message); }
  }

  async function handleFreeze() {
    setIsFreezing(true); setError(null);
    try {
      await api(`/rules/${selectedRuleId}/freeze`, { method: 'POST' });
      await fetchRules();
      await refreshSelected();
    } catch (e) { setError(e.message); }
    finally { setIsFreezing(false); }
  }

  async function handleUnfreeze() {
    if (!window.confirm('Unlock to edit? This clears the current AI results for this rule.')) return;
    try {
      await api(`/rules/${selectedRuleId}/unfreeze`, { method: 'POST' });
      setError(null);
      await fetchRules();
      await refreshSelected();
    } catch (e) { setError(e.message); }
  }

  async function handleSaveRuleText() {
    const t = editRuleText.trim();
    if (!t) return;
    try {
      await api(`/rules/${selectedRuleId}`, { method: 'PATCH', headers: JSON_HEADERS, body: JSON.stringify({ rule_text: t }) });
      setEditingRule(false);
      setError(null);
      await fetchRules();
    } catch (e) { setError(e.message); }
  }

  async function handleRun() {
    setIsRunning(true); setError(null);
    try {
      await api(`/run/${selectedRuleId}`, { method: 'POST' });
      await refreshSelected();
    } catch (e) { setError(e.message); }
    finally { setIsRunning(false); }
  }

  async function handleDeleteExample(id) {
    try {
      await api(`/test-cases/${id}`, { method: 'DELETE' });
      setError(null);
      refreshSelected();
    } catch (err) { setError(err.message); }
  }

  async function handleDeleteRule(ruleId, e) {
    e.stopPropagation();
    if (!window.confirm('Delete this rule and its answers/results?')) return;
    try {
      await api(`/rules/${ruleId}`, { method: 'DELETE' });
      if (ruleId === selectedRuleId) setSelectedRuleId(null);
      setError(null);
      fetchRules();
    } catch (err) { setError(err.message); }
  }

  async function handleDecision(decision) {
    try {
      await api(`/decision/${selectedRuleId}`, { method: 'POST', headers: JSON_HEADERS, body: JSON.stringify({ decision }) });
      await fetchRules();
      await refreshSelected();
    } catch (e) { setError(e.message); }
  }

  const selectedRule = rules.find((r) => r.rule_id === selectedRuleId);
  const frozen = !!selectedRule?.frozen;
  const showResults = frozen && !!results;

  // results summary
  const rows = results ? mergeChecks(results.results) : [];
  const summary = { total: rows.length, good: 0, caught: 0, other: 0 };
  rows.forEach((r) => {
    const d = diagnose(r);
    if (d.label === 'Trustworthy') summary.good++;
    else if (d.label === 'Code bug caught' || d.label === "Code wouldn't run") summary.caught++;
    else summary.other++;
  });
  const status = results?.status;

  return (
    <div className="app">
      <header className="app-header">
        <h1 className="app-title">Can you trust AI to turn rules into code?</h1>
        <p className="app-subtitle">
          You lock in the correct answers for a few examples <b>first</b>. Then AI writes the code, and two
          independent checkers verify it — one <b>runs the code</b>, the other <b>reasons from the rule</b>.
          Where they disagree, a mistake gets caught.
        </p>
      </header>

      {error && (
        <div className="flow-error" role="alert">
          <span>{error}</span>
          <button className="ghost" onClick={() => setError(null)} aria-label="Dismiss error">Dismiss</button>
        </div>
      )}

      <div className="layout">
        {/* ---------------- Sidebar ---------------- */}
        <aside className="sidebar">
          <div className="sidebar-top">
            <p className="sidebar-label">Your rules</p>
            <button className="ghost demo-btn" onClick={loadDemoRules} disabled={loadingDemo}>
              {loadingDemo ? 'Loading…' : 'Load 5 examples'}
            </button>
          </div>
          <div className="rule-list">
            {rules.length === 0 && <span className="hint">No rules yet — load the 5 examples or write one below.</span>}
            {rules.map((r) => (
              <div className={`rule-row ${r.rule_id === selectedRuleId ? 'active' : ''}`} key={r.id}>
                <button className="rule-card" onClick={() => setSelectedRuleId(r.rule_id)}>
                  {r.frozen && <span className="mini-lock" aria-hidden="true">🔒</span>}
                  {r.rule_text}
                </button>
                <button className="rule-del" onClick={(e) => handleDeleteRule(r.rule_id, e)} aria-label="Delete rule" title="Delete rule">×</button>
              </div>
            ))}
          </div>

          <div className="new-rule">
            <span className="field-label">Write a new rule</span>
            <textarea
              rows={3}
              placeholder='e.g. "If income is below $40,000, send for manual review."'
              value={newRuleText}
              onChange={(e) => setNewRuleText(e.target.value)}
              style={{ marginBottom: '0.7rem' }}
            />
            <button className="full" onClick={handleNewRule}>Add rule</button>
          </div>
        </aside>

        {/* ---------------- Main panel ---------------- */}
        <main className="panel">
          {!selectedRule && (
            <div className="panel-empty">
              <div className="panel-empty-icon" aria-hidden="true">📋</div>
              Pick a rule on the left, or load the 5 examples to get started.
            </div>
          )}

          {selectedRule && (
            <>
              {editingRule ? (
                <div className="rule-edit">
                  <textarea rows={2} value={editRuleText} onChange={(e) => setEditRuleText(e.target.value)} />
                  <div className="form-actions">
                    <button onClick={handleSaveRuleText}>Save rule</button>
                    <button className="secondary" onClick={() => setEditingRule(false)}>Cancel</button>
                  </div>
                </div>
              ) : (
                <div className="rule-heading">
                  <span>{selectedRule.rule_text}</span>
                  {!frozen && (
                    <button className="edit-rule-btn" onClick={() => { setEditRuleText(selectedRule.rule_text); setEditingRule(true); }}>Edit</button>
                  )}
                </div>
              )}

              {/* progress stepper — shows what to do next */}
              <div className="stepper">
                <div className={`stepper-item ${frozen ? 'done' : 'active'}`}><span className="dot">1</span> Lock answers</div>
                <div className="stepper-line" />
                <div className={`stepper-item ${!frozen ? 'todo' : (showResults ? 'done' : 'active')}`}><span className="dot">2</span> Check</div>
                <div className="stepper-line" />
                <div className={`stepper-item ${showResults ? 'active' : 'todo'}`}><span className="dot">3</span> Review</div>
              </div>

              {/* Step 1 — examples + freeze */}
              <section className={`step ${frozen ? 'is-done' : 'is-active'}`}>
                <div className="step-head">
                  <span className="step-num">1</span>
                  <span className="step-title">Lock the correct answers</span>
                  {frozen && <span className="lock-badge" title={selectedRule.frozen_at}>🔒 Locked</span>}
                </div>
                <p className="step-sub">
                  Write a few example applicants and the outcome you say is right — then freeze them.
                  Freezing first is what makes the check honest.
                </p>

                {testCases.length > 0 && (
                  <div className="example-list">
                    {testCases.map((tc) => (
                      <div className="example-item" key={tc.id ?? tc.applicant_id}>
                        <div className="chip-row">
                          <span className="example-name">{tc.applicant_id}</span>
                          {Object.entries(tc.applicant_data).map(([k, v]) => (
                            <span className="chip" key={k}>{k} <b>{fmtVal(v)}</b></span>
                          ))}
                        </div>
                        <div className="example-right">
                          <span className={`verdict ${outcomeTone(tc.expected_outcome)}`}>{cap(tc.expected_outcome)}</span>
                          {!frozen && (
                            <button className="ex-del" onClick={() => handleDeleteExample(tc.id)} aria-label="Delete example" title="Delete example">×</button>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                )}

                {testCases.length === 0 && (
                  <p className="hint" style={{ marginBottom: '0.85rem' }}>No examples yet. Add at least one, then freeze.</p>
                )}

                {/* add-example is only possible before freezing */}
                {!frozen && !showAddExample && (
                  <div className="step1-actions">
                    <button className="secondary" onClick={() => setShowAddExample(true)}>+ Add an example</button>
                    <button className="btn-freeze" onClick={handleFreeze} disabled={isFreezing || testCases.length === 0}>
                      {isFreezing ? 'Freezing…' : '🔒 Freeze answer key'}
                    </button>
                  </div>
                )}
                {frozen && (
                  <div className="locked-note">
                    <p className="hint">Answer key is locked — this is what you check against. To change the rule or examples, unlock first (this clears the current AI results).</p>
                    <button className="secondary" onClick={handleUnfreeze}>Unlock to edit</button>
                  </div>
                )}

                {!frozen && showAddExample && (
                  <form className="example-form" onSubmit={handleSubmitTestCase}>
                    <div className="form-grid-2">
                      <div>
                        <span className="field-label">Name</span>
                        <input value={tcName} onChange={(e) => setTcName(e.target.value)} placeholder="e.g. Raj" />
                      </div>
                      <div>
                        <span className="field-label">Correct answer</span>
                        <select value={tcExpected} onChange={(e) => setTcExpected(e.target.value)}>
                          {OUTCOMES.map((o) => <option key={o} value={o}>{cap(o)}</option>)}
                        </select>
                      </div>
                    </div>
                    <span className="field-label">Their details</span>
                    {tcFields.map((f) => (
                      <div className="kv-row" key={f.id}>
                        <input placeholder="field (e.g. income)" value={f.key} onChange={(e) => updateField(f.id, 'key', e.target.value)} />
                        <input placeholder="value (e.g. 80000)" value={f.value} onChange={(e) => updateField(f.id, 'value', e.target.value)} />
                        <button type="button" className="kv-remove" onClick={() => removeField(f.id)} aria-label="Remove field">×</button>
                      </div>
                    ))}
                    <button type="button" className="ghost" onClick={addField}>+ Add field</button>
                    {tcError && <div className="field-error">{tcError}</div>}
                    <div className="form-actions">
                      <button type="submit">Save example</button>
                      <button type="button" className="secondary" onClick={resetExampleForm}>Cancel</button>
                    </div>
                  </form>
                )}
              </section>

              {/* Step 2 — check (locked until frozen) */}
              <section className={`step ${!frozen ? 'is-todo' : (showResults ? 'is-done' : 'is-active')}`}>
                <div className="step-head">
                  <span className="step-num">2</span>
                  <span className="step-title">Let AI write the code, then check it</span>
                </div>
                <div className="check-cta">
                  <button className="btn-lg" onClick={handleRun} disabled={isRunning || !frozen}>
                    {isRunning ? <><span className="spinner" />Checking…</> : (showResults ? 'Check again' : 'Check this rule')}
                  </button>
                  {!frozen && <span className="hint">Freeze the answer key first to unlock this.</span>}
                </div>
              </section>

              {/* Step 3 — results (only meaningful once frozen) */}
              {showResults && (
                <section className="step is-active" aria-live="polite">
                  <div className="step-head">
                    <span className="step-num">3</span>
                    <span className="step-title">What the two checkers found</span>
                    <button className="legend-toggle" onClick={() => setShowLegend((s) => !s)}>
                      {showLegend ? 'Hide guide' : 'How to read this'}
                    </button>
                  </div>

                  {showLegend && (
                    <div className="legend">
                      <div><b>Ran code ✓ · Read rule ✓</b> → Trustworthy</div>
                      <div><b>Ran code ✕ · Read rule ✓</b> → Code bug caught</div>
                      <div><b>Ran code ✓ · Read rule ✕</b> → Rule may be ambiguous</div>
                      <div><b>Ran code ✕ · Read rule ✕</b> → Your answer key looks wrong</div>
                    </div>
                  )}

                  {/* summary bar */}
                  <div className="summary-bar">
                    <span className="summary-stat">{summary.total} checked</span>
                    <span className="summary-stat good">{summary.good} trustworthy</span>
                    {summary.caught > 0 && <span className="summary-stat bad">{summary.caught} bug caught</span>}
                    {summary.other > 0 && <span className="summary-stat warn">{summary.other} to review</span>}
                  </div>

                  {summary.caught > 0 && (
                    <div className="callout bad">
                      The code looked reasonable but <b>failed {summary.caught} case{summary.caught > 1 ? 's' : ''}</b> that
                      an independent reading of the rule got right — exactly the kind of mistake blind trust would miss.
                    </div>
                  )}

                  {rows.map((row) => {
                    const d = diagnose(row);
                    const unrunnable = row.codeObserved === 'unrunnable';
                    return (
                      <div className="result-card" key={row.applicant_id}>
                        <div className="result-head">
                          <div className="result-who">
                            <b>{row.applicant_id}</b> <span className="exp">· you expected {cap(row.expected)}</span>
                          </div>
                          <span className={`verdict ${d.tone}`}>{d.label}</span>
                        </div>
                        <div className="checks">
                          <div className={`check-tile ${unrunnable ? 'unrunnable' : ''}`}>
                            <div className="check-label">Ran the AI's code</div>
                            <div className="check-outcome">{unrunnable ? "Wouldn't run" : (cap(row.codeObserved) ?? '—')}</div>
                            {!unrunnable && (
                              <span className={`check-flag ${row.codeMatch ? 'ok' : 'no'}`}>
                                {row.codeMatch ? '✓ matches your answer' : '✕ differs from your answer'}
                              </span>
                            )}
                          </div>
                          <div className="check-tile">
                            <div className="check-label">Read the rule by hand</div>
                            <div className="check-outcome">{cap(row.reasonObserved) ?? '—'}</div>
                            <span className={`check-flag ${row.reasonMatch ? 'ok' : 'no'}`}>
                              {row.reasonMatch ? '✓ matches your answer' : '✕ differs from your answer'}
                            </span>
                          </div>
                        </div>
                        <div className={`diagnosis ${d.tone}`}>
                          <span className="diagnosis-label">{d.label}.</span>{d.explanation}
                        </div>
                        {row.reasonRationale && <div className="reasoning">{row.reasonRationale}</div>}
                      </div>
                    );
                  })}

                  <button className="secondary" style={{ marginTop: '0.5rem' }} onClick={() => setShowCode(!showCode)}>
                    {showCode ? 'Hide the code AI wrote' : 'Show the code AI wrote'}
                  </button>
                  {showCode && <div className="code-box">{results.generated_code}</div>}

                  {/* human decision */}
                  <div className="decision-bar">
                    <div className="decision-label">
                      Your call{status && status !== 'draft' && <span className={`status-badge ${status}`}>{cap(status)}</span>}
                    </div>
                    <div className="decision-actions">
                      <button className="btn-approve" onClick={() => handleDecision('approved')}>Approve code</button>
                      <button className="btn-review" onClick={() => handleDecision('in_review')}>Needs review</button>
                      <button className="btn-reject" onClick={() => handleDecision('rejected')}>Reject</button>
                    </div>
                  </div>
                </section>
              )}
            </>
          )}
        </main>
      </div>
    </div>
  );
}

export default App;
