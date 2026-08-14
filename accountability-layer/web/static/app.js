/* ── app.js — Accountability Layer Test Interface ──────────────────────────── */
'use strict';

(function () {

  // ── Markdown renderer ─────────────────────────────────────────────────────────
  if (typeof marked !== 'undefined') {
    marked.setOptions({ breaks: true, gfm: true });
  }
  function renderMd(text) {
    if (!text) return '';
    return typeof marked !== 'undefined'
      ? marked.parse(text)
      : esc(text).replace(/\n/g, '<br>');
  }

  // ── State ────────────────────────────────────────────────────────────────────
  let currentScope = 'auditor';
  let isRunning    = false;
  let activeTab    = 'runs';

  // SEC-02: one JWT per scope, cached in memory (8h TTL on server)
  const _tokens = { auditor: null, investor: null };

  // ── DOM refs ─────────────────────────────────────────────────────────────────
  const $ = id => document.getElementById(id);

  const statusDot      = $('statusDot');
  const statusLabel    = $('statusLabel');
  const btnDirective   = $('btnDirective');
  const btnClear       = $('btnClear');

  const scopeAuditor  = $('scopeAuditor');
  const scopeInvestor = $('scopeInvestor');
  const scopeHint     = $('scopeHint');

  const cfgProvider    = $('cfgProvider');
  const geminiFields   = $('geminiFields');
  const ollamaFields   = $('ollamaFields');
  const cfgOllamaModel = $('cfgOllamaModel');
  const cfgSeed        = $('cfgSeed');
  const cfgSeedLabel   = $('cfgSeedLabel');
  const cfgModel       = $('cfgModel');
  const cfgTemp        = $('cfgTemp');
  const cfgTempLabel   = $('cfgTempLabel');
  const cfgAgentId     = $('cfgAgentId');
  const cfgConf        = $('cfgConf');
  const cfgConfLabel   = $('cfgConfLabel');
  const confClassHint  = $('confClassHint');
  const cfgFailureMode      = $('cfgFailureMode');
  const failureHint         = $('failureHint');
  const cfgConsistencyProbe = $('cfgConsistencyProbe');
  const directiveBadge      = $('directiveBadge');

  const chatMessages = $('chatMessages');
  const btnToggleCtx = $('btnToggleContext');
  const contextInput = $('contextInput');
  const messageInput = $('messageInput');
  const btnSend      = $('btnSend');
  const sendLabel    = $('sendLabel');
  const sendSpinner  = $('sendSpinner');

  const tabRuns        = $('tabRuns');
  const tabSessions    = $('tabSessions');
  const runCountBadge  = $('runCount');
  const sessCountBadge = $('sessionCount');
  const auditRuns      = $('auditRuns');
  const auditSessions  = $('auditSessions');

  const directiveModal    = $('directiveModal');
  const mdlDirVersion     = $('modalDirectiveVersion');
  const mdlDirText        = $('modalDirectiveText');
  const btnCloseDirective = $('btnCloseDirective');

  const detailModal      = $('detailModal');
  const detailModalTitle = $('detailModalTitle');
  const detailModalId    = $('detailModalId');
  const detailModalJson  = $('detailModalJson');
  const btnCloseDetail   = $('btnCloseDetail');

  // ── Helpers ───────────────────────────────────────────────────────────────────

  function esc(v) {
    return String(v == null ? '' : v)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;')
      .replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }

  function confLabel(score) {
    return score < 0.4 ? 'HIGH_UNCERTAINTY' : 'STANDARD';
  }

  function confHint(score) {
    return score < 0.4
      ? 'HIGH_UNCERTAINTY — score < 0.4 (speculative)'
      : 'STANDARD — score ≥ 0.4';
  }

  function failureHintText(mode) {
    return {
      none:          'Agent responds correctly every time.',
      retry_success: 'First call fails (parse error), retry succeeds.',
      halt:          'Both calls fail — pipeline halts (ADR-07).',
    }[mode] || '';
  }

  function srcClass(status) {
    return { simulated: 'simulated', cached: 'cached', live: 'live', failed: 'failed' }[status] || 'cached';
  }

  // ── SEC-02: JWT token management ──────────────────────────────────────────────

  /**
   * Ensure a valid JWT exists for the given scope.
   * Issues one from the server if not cached (tokens live 8 h).
   */
  async function ensureToken(scope) {
    if (_tokens[scope]) return _tokens[scope];
    const res  = await fetch('/api/auth/token', {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify({ scope }),
    });
    if (!res.ok) throw new Error(`Failed to obtain ${scope} token: ${res.statusText}`);
    const { access_token } = await res.json();
    _tokens[scope] = access_token;
    return access_token;
  }

  async function authHeader(scope) {
    const token = await ensureToken(scope);
    return { Authorization: `Bearer ${token}` };
  }

  // ── Status dot ────────────────────────────────────────────────────────────────

  function setStatus(state) {
    statusDot.className = 'status-dot ' + state;
    statusLabel.textContent = { ok: 'Online', err: 'Error', connecting: 'Connecting…' }[state] || state;
  }

  // ── Config ────────────────────────────────────────────────────────────────────

  async function loadConfig() {
    const cfg = await fetch('/api/config').then(r => r.json());
    cfgProvider.value        = cfg.provider       || 'mock';
    cfgModel.value           = cfg.model          || 'gemini-2.5-flash';
    cfgTemp.value            = cfg.temperature    ?? 0.0;
    cfgTempLabel.textContent = cfg.temperature    ?? 0.0;
    if (cfgOllamaModel) cfgOllamaModel.value = cfg.ollama_model || 'llama3.2';
    if (cfgSeed) { cfgSeed.value = cfg.seed ?? 42; cfgSeedLabel.textContent = cfg.seed ?? 42; }
    cfgAgentId.value         = cfg.agent_id       || 'external';
    cfgFailureMode.value     = cfg.failure_mode   || 'none';
    cfgConf.value            = cfg.confidence_score ?? 0.75;
    cfgConfLabel.textContent = cfg.confidence_score ?? 0.75;
    confClassHint.textContent = confHint(cfg.confidence_score ?? 0.75);
    failureHint.textContent   = failureHintText(cfg.failure_mode || 'none');
    geminiFields.style.display = cfg.provider === 'gemini' ? '' : 'none';
    if (ollamaFields) ollamaFields.style.display = cfg.provider === 'ollama' ? '' : 'none';
    cfgConsistencyProbe.checked = cfg.consistency_probe ?? false;
  }

  async function pushConfig(patch) {
    try {
      await fetch('/api/config', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(patch),
      });
    } catch (e) {
      console.warn('Config push failed:', e);
    }
  }

  // ── Directive ─────────────────────────────────────────────────────────────────

  async function loadDirective() {
    const d = await fetch('/api/directive').then(r => r.json());
    directiveBadge.textContent = d.version;
    mdlDirVersion.textContent  = d.version;
    mdlDirText.textContent     = d.text;
  }

  // ── Config event listeners ────────────────────────────────────────────────────

  cfgProvider.addEventListener('change', () => {
    geminiFields.style.display = cfgProvider.value === 'gemini' ? '' : 'none';
    if (ollamaFields) ollamaFields.style.display = cfgProvider.value === 'ollama' ? '' : 'none';
    pushConfig({ provider: cfgProvider.value });
  });
  cfgModel.addEventListener('change', () => pushConfig({ model: cfgModel.value }));
  if (cfgOllamaModel) cfgOllamaModel.addEventListener('change', () => pushConfig({ ollama_model: cfgOllamaModel.value }));
  if (cfgSeed) cfgSeed.addEventListener('input', () => {
    const v = parseInt(cfgSeed.value, 10);
    cfgSeedLabel.textContent = v;
    pushConfig({ seed: v });
  });
  cfgTemp.addEventListener('input', () => {
    const v = parseFloat(cfgTemp.value);
    cfgTempLabel.textContent = v;
    pushConfig({ temperature: v });
  });
  cfgAgentId.addEventListener('change', () => pushConfig({ agent_id: cfgAgentId.value }));
  cfgConf.addEventListener('input', () => {
    const v = parseFloat(cfgConf.value);
    cfgConfLabel.textContent  = v;
    confClassHint.textContent = confHint(v);
    pushConfig({ confidence_score: v });
  });
  cfgFailureMode.addEventListener('change', () => {
    failureHint.textContent = failureHintText(cfgFailureMode.value);
    pushConfig({ failure_mode: cfgFailureMode.value });
  });
  cfgConsistencyProbe.addEventListener('change', () => {
    pushConfig({ consistency_probe: cfgConsistencyProbe.checked });
  });

  // ── Scope toggle ──────────────────────────────────────────────────────────────

  function setScope(scope) {
    currentScope = scope;
    scopeAuditor.classList.toggle('active',  scope === 'auditor');
    scopeInvestor.classList.toggle('active', scope === 'investor');
    scopeHint.textContent = scope === 'auditor'
      ? 'Full record — thought_log visible.'
      : 'Investor view — thought_log structurally excluded (SEC-01).';
    // Pre-warm token for the new scope
    ensureToken(scope).catch(() => {});
  }

  scopeAuditor.addEventListener('click',  () => setScope('auditor'));
  scopeInvestor.addEventListener('click', () => setScope('investor'));

  // ── Context drawer ────────────────────────────────────────────────────────────

  btnToggleCtx.addEventListener('click', () => {
    const hidden = contextInput.classList.toggle('hidden');
    btnToggleCtx.textContent = hidden ? '+ Add context' : '− Hide context';
  });

  // ── Chat rendering ────────────────────────────────────────────────────────────

  function clearEmpty(container) {
    const el = container.querySelector('.chat-empty');
    if (el) el.remove();
  }

  function scrollChat() {
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }

  function showThinking() {
    const el = document.createElement('div');
    el.id = 'thinkingIndicator';
    el.className = 'msg-thinking';
    el.innerHTML = '<div class="msg-thinking-dot"></div>'
                 + '<div class="msg-thinking-dot"></div>'
                 + '<div class="msg-thinking-dot"></div>';
    chatMessages.appendChild(el);
    scrollChat();
  }

  function hideThinking() {
    const el = document.getElementById('thinkingIndicator');
    if (el) el.remove();
  }

  function appendUserBubble(text) {
    clearEmpty(chatMessages);
    const div = document.createElement('div');
    div.className   = 'msg-user';
    div.textContent = text;
    chatMessages.appendChild(div);
    scrollChat();
  }

  function sourcesHtml(sources) {
    if (!sources || sources.length === 0) return '';
    const rows = sources.map(s => {
      const cls  = srcClass(s.status);
      const note = s.provenance_note
        ? `<span class="msg-source-note">${esc(s.provenance_note)}</span>` : '';
      return `<div class="msg-source-row">
        <span class="source-status ${cls}">${esc(s.status)}</span>
        <span class="msg-source-name">${esc(s.source)}</span>${note}
      </div>`;
    }).join('');
    return `<div class="msg-sources">
      <div class="msg-sources-title">Data Sources</div>
      ${rows}
    </div>`;
  }

  function confLineHtml(data) {
    const score    = data.confidence_score;
    const label    = data.confidence_classification || confLabel(score || 0);
    const badgeCls = data.high_uncertainty ? 'badge badge-uncertainty' : 'badge-neutral';
    const degraded = data.confidence_degraded
      ? ` <span class="badge-degraded" title="ADR-04: degraded by simulated/failed data sources">↓ degraded</span>`
      : '';
    return `<div class="msg-confidence">
      Confidence <strong>${esc(String(score))}</strong>
      <span class="${badgeCls}">${esc(label)}</span>${degraded}
    </div>`;
  }

  // ── Consistency badge ─────────────────────────────────────────────────────────

  function consistencyHtml(c) {
    if (!c) return '';
    if (c.agreement === 'UNKNOWN') {
      return `<div class="msg-consistency">
        <span class="badge badge-neutral">Consistency</span>
        <span class="badge-neutral">UNKNOWN</span>
        ${c.probe_error ? `<span class="consistency-note">${esc(c.probe_error)}</span>` : ''}
      </div>`;
    }
    const cls = { HIGH: 'badge-success', MEDIUM: 'badge-warning', LOW: 'badge-halt' }[c.agreement] || 'badge-neutral';
    const diverged = c.divergent_numbers && c.divergent_numbers.length
      ? ` <span class="consistency-note">divergent: ${c.divergent_numbers.map(esc).join(', ')}</span>` : '';
    return `<div class="msg-consistency">
      <span class="badge-neutral">Consistency</span>
      <span class="badge ${cls}">${esc(c.agreement)}</span>
      <span class="consistency-score">${esc(String(c.score))}</span>${diverged}
    </div>`;
  }

  // ── Claims summary ────────────────────────────────────────────────────────────

  const CLAIM_ICONS = { citation: '🔗', quantitative: '📊', hedge: '⚠', causal: '→' };
  const CLAIM_CLS   = { citation: 'claim-citation', quantitative: 'claim-quant', hedge: 'claim-hedge', causal: 'claim-causal' };

  function verifiedBadge(v) {
    if (v === true)  return '<span class="badge badge-success" title="Source confirmed">✓</span>';
    if (v === false) return '<span class="badge badge-halt"    title="Source checked, not found">✗</span>';
    return '';
  }

  function claimsHtml(claims, verificationRate) {
    if (!claims || claims.length === 0) return '';
    const pills = claims.map(c => {
      const icon = CLAIM_ICONS[c.claim_type] || '·';
      const cls  = CLAIM_CLS[c.claim_type]   || '';
      const tip  = esc(c.context || c.text);
      const vb   = (c.claim_type === 'citation') ? verifiedBadge(c.verified) : '';
      return `<span class="claim-pill ${cls}" title="${tip}">${icon} ${esc(c.text.slice(0, 40))}${c.text.length > 40 ? '…' : ''}${vb}</span>`;
    }).join('');
    const vRateHtml = (verificationRate != null)
      ? ` <span class="badge-neutral" title="Citation verification rate">${Math.round(verificationRate * 100)}% verified</span>`
      : '';
    return `<details class="msg-claims">
      <summary>Claims <span class="badge-neutral">${claims.length}</span>${vRateHtml} <span class="claims-hint">ADR-06</span></summary>
      <div class="claims-pills">${pills}</div>
    </details>`;
  }

  function appendAgentBubble(data) {
    clearEmpty(chatMessages);
    const outer = document.createElement('div');
    outer.className = 'msg-agent';

    let header = '';
    let body   = '';

    if (data.high_uncertainty) {
      const banner = document.createElement('div');
      banner.className = 'msg-uncertainty-banner';
      banner.innerHTML = `⚠ HIGH_UNCERTAINTY — confidence ${esc(String(data.confidence_score))} &lt; 0.4. `
        + `Conclusions are speculative and require human review before acting.`;
      chatMessages.appendChild(banner);
    }

    if (data.halted) {
      header = `<span class="badge badge-halt">⛔ HALTED</span>
                <span class="badge-neutral">ADR-07</span>`;
    } else {
      const attempts = (data.reasoning_objects || []).length;
      const retried  = attempts > 1;
      header = retried
        ? `<span class="badge badge-warning">⚠ Retried</span><span class="badge-neutral">Attempt ${attempts}</span>`
        : `<span class="badge badge-success">✓ OK</span>`;
      if (data.scope) header += ` <span class="badge-neutral">${esc(data.scope)}</span>`;
    }

    if (data.halted) {
      body = `<div class="msg-halt-title">Pipeline Halted</div>
              <div class="msg-halt-body">${esc(data.error || 'Double structural parse failure.')}</div>`;
    } else {
      if (data.conclusion) {
        body += `<div class="msg-conclusion md">${renderMd(data.conclusion)}</div>`;
      }
      if (data.thought_log) {
        body += `<details class="msg-thought-log">
          <summary>Thought Log <span class="badge-neutral">ADR-06 — unverified</span></summary>
          <div class="msg-thought-body md">${renderMd(data.thought_log)}</div>
        </details>`;
      } else if (currentScope === 'investor' && !data.halted) {
        body += `<div class="msg-scope-notice">thought_log excluded — Investor scope (SEC-01)</div>`;
      }
    }

    body += confLineHtml(data);
    body += consistencyHtml(data.consistency);
    body += claimsHtml(data.claims, data.verification_rate);
    body += sourcesHtml(data.data_sources);

    if (data.run_id) {
      body += `<div class="msg-meta">
        Run <a class="run-link" data-id="${esc(data.run_id)}" href="#">${esc(data.run_id.slice(0, 8))}…</a>
      </div>`;
    }

    outer.innerHTML = `
      <div class="msg-agent-header">${header}</div>
      <div class="msg-agent-body">${body}</div>`;

    outer.querySelectorAll('.run-link').forEach(a => {
      a.addEventListener('click', e => { e.preventDefault(); openRunDetail(a.dataset.id); });
    });

    chatMessages.appendChild(outer);
    scrollChat();
  }

  function appendNetworkError(msg) {
    clearEmpty(chatMessages);
    const div = document.createElement('div');
    div.className = 'msg-agent';
    div.innerHTML = `
      <div class="msg-agent-header"><span class="badge badge-danger">Error</span></div>
      <div class="msg-agent-body">
        <div class="msg-halt-body">${esc(msg)}</div>
      </div>`;
    chatMessages.appendChild(div);
    scrollChat();
  }

  // ── Send (SEC-02: Bearer token instead of ?scope= query param) ────────────────

  async function sendMessage() {
    const text = messageInput.value.trim();
    if (!text || isRunning) return;

    isRunning = true;
    btnSend.disabled = true;
    sendLabel.textContent = 'Running…';
    sendSpinner.classList.remove('hidden');

    appendUserBubble(text);
    messageInput.value = '';
    showThinking();

    try {
      const headers = {
        'Content-Type': 'application/json',
        ...(await authHeader(currentScope)),
      };

      const res = await fetch('/api/chat', {
        method:  'POST',
        headers,
        body:    JSON.stringify({ message: text, context: contextInput.value.trim() }),
      });

      hideThinking();
      if (res.status === 401) {
        // Token expired — clear cache and retry once
        _tokens[currentScope] = null;
        const retryHeaders = {
          'Content-Type': 'application/json',
          ...(await authHeader(currentScope)),
        };
        const retry = await fetch('/api/chat', {
          method:  'POST',
          headers: retryHeaders,
          body:    JSON.stringify({ message: text, context: contextInput.value.trim() }),
        });
        if (!retry.ok) {
          const err = await retry.json().catch(() => ({ detail: retry.statusText }));
          appendNetworkError(err.detail || `HTTP ${retry.status}`);
        } else {
          appendAgentBubble(await retry.json());
          refreshAuditBoth();
        }
      } else if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: res.statusText }));
        appendNetworkError(err.detail || `HTTP ${res.status}`);
      } else {
        appendAgentBubble(await res.json());
        refreshAuditBoth();
      }
    } catch (err) {
      hideThinking();
      appendNetworkError('Network error: ' + err.message);
    } finally {
      isRunning = false;
      btnSend.disabled = false;
      sendLabel.textContent = 'Send';
      sendSpinner.classList.add('hidden');
    }
  }

  btnSend.addEventListener('click', sendMessage);
  messageInput.addEventListener('keydown', e => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); }
  });

  // ── Audit panel ───────────────────────────────────────────────────────────────

  function switchTab(tab) {
    activeTab = tab;
    tabRuns.classList.toggle('active',       tab === 'runs');
    tabSessions.classList.toggle('active',   tab === 'sessions');
    auditRuns.classList.toggle('hidden',     tab !== 'runs');
    auditSessions.classList.toggle('hidden', tab !== 'sessions');
    if (tab === 'sessions') refreshSessions();
    else refreshRuns();
  }

  tabRuns.addEventListener('click',     () => switchTab('runs'));
  tabSessions.addEventListener('click', () => switchTab('sessions'));

  function sourcePills(sources) {
    if (!sources || sources.length === 0) return '';
    return sources.map(s =>
      `<span class="audit-source-pill pill-${srcClass(s.status)}">${esc(s.source)}</span>`
    ).join('');
  }

  function renderRunCard(run) {
    const card = document.createElement('div');
    card.className = 'audit-card' + (run.halted ? ' audit-card-halted' : '');

    const label    = run.confidence_classification || confLabel(run.confidence_score || 0);
    const badgeCls = run.high_uncertainty ? 'badge badge-uncertainty' : 'badge-neutral';
    const degraded = run.confidence_degraded
      ? `<span class="badge-neutral" title="ADR-04 degraded">↓</span> ` : '';
    const statusBadge = run.halted
      ? `<span class="badge badge-halt">HALTED</span>`
      : `<span class="badge badge-success">DONE</span>`;

    card.innerHTML = `
      <div class="audit-card-header">
        ${statusBadge}
        <span class="audit-run-id">${esc((run.run_id || '').slice(0, 8))}…</span>
      </div>
      <div class="audit-subject" title="${esc(run.subject || '')}">${esc(run.subject || '—')}</div>
      <div class="audit-meta">
        ${degraded}<span class="${badgeCls}">${esc(label)}</span>
        <span class="badge-neutral">${esc(run.scope || 'auditor')}</span>
        ${sourcePills(run.data_sources)}
      </div>`;

    card.addEventListener('click', () => openRunDetail(run.run_id));
    return card;
  }

  function renderSessionCard(session) {
    const card = document.createElement('div');
    card.className = 'audit-card' + (session.status === 'HALTED' ? ' audit-card-halted' : '');

    const ver = session.directive_version || '—';
    const cls = session.confidence_classification;
    const statusBadge = session.status === 'HALTED'
      ? `<span class="badge badge-halt">HALTED</span>`
      : `<span class="badge badge-success">DONE</span>`;

    card.innerHTML = `
      <div class="audit-card-header">
        ${statusBadge}
        <span class="audit-run-id">${esc(session.ticker || 'RUN')}</span>
      </div>
      <div class="audit-subject">${esc((session.run_id || '').slice(0, 8))}…</div>
      <div class="audit-meta">
        <span class="badge-neutral">directive ${esc(ver)}</span>
        ${cls ? `<span class="badge-neutral">${esc(cls)}</span>` : ''}
      </div>`;

    card.addEventListener('click', () => openSessionDetail(session.run_id));
    return card;
  }

  async function refreshRuns() {
    try {
      const runs = await fetch('/api/runs').then(r => r.json());
      runCountBadge.textContent = runs.length;
      auditRuns.innerHTML = '';
      if (runs.length === 0) {
        auditRuns.innerHTML = '<div class="audit-empty">No runs yet.</div>';
      } else {
        runs.forEach(r => auditRuns.appendChild(renderRunCard(r)));
      }
    } catch { /* silent */ }
  }

  async function refreshSessions() {
    try {
      const sessions = await fetch('/api/sessions').then(r => r.json());
      sessCountBadge.textContent = sessions.length;
      auditSessions.innerHTML = '';
      if (sessions.length === 0) {
        auditSessions.innerHTML = '<div class="audit-empty">No sessions yet.</div>';
      } else {
        sessions.forEach(s => auditSessions.appendChild(renderSessionCard(s)));
      }
    } catch { /* silent */ }
  }

  function refreshAuditBoth() {
    fetch('/api/runs').then(r => r.json()).then(d => {
      runCountBadge.textContent = d.length;
      if (activeTab === 'runs') {
        auditRuns.innerHTML = '';
        if (d.length === 0) {
          auditRuns.innerHTML = '<div class="audit-empty">No runs yet.</div>';
        } else {
          d.forEach(r => auditRuns.appendChild(renderRunCard(r)));
        }
      }
    }).catch(() => {});

    fetch('/api/sessions').then(r => r.json()).then(d => {
      sessCountBadge.textContent = d.length;
      if (activeTab === 'sessions') {
        auditSessions.innerHTML = '';
        if (d.length === 0) {
          auditSessions.innerHTML = '<div class="audit-empty">No sessions yet.</div>';
        } else {
          d.forEach(s => auditSessions.appendChild(renderSessionCard(s)));
        }
      }
    }).catch(() => {});
  }

  // ── Detail modal rendering ────────────────────────────────────────────────────

  function detailSection(title, contentHtml) {
    return `<div class="detail-section">
      <div class="detail-section-title">${esc(title)}</div>
      <div class="detail-section-body">${contentHtml}</div>
    </div>`;
  }

  function detailRow(label, valueHtml) {
    return `<div class="detail-row">
      <span class="detail-label">${esc(label)}</span>
      <span class="detail-value">${valueHtml}</span>
    </div>`;
  }

  function renderRunDetailHtml(run, flags) {
    const statusBadge = run.halted
      ? `<span class="badge badge-halt">HALTED</span>`
      : `<span class="badge badge-success">COMPLETE</span>`;
    const cl       = run.confidence_classification || confLabel(run.confidence_score || 0);
    const confCls  = run.high_uncertainty ? 'badge badge-uncertainty' : 'badge-neutral';
    const degraded = run.confidence_degraded
      ? ` <span class="badge-degraded">↓ degraded</span>` : '';

    let html = '';

    // ── Meta ──
    html += detailSection('Run', [
      detailRow('ID',     `<code>${esc(run.run_id)}</code>`),
      detailRow('Status', statusBadge),
      detailRow('Scope',  `<span class="badge-neutral">${esc(run.scope || '—')}</span>`),
      detailRow('Agent',  `<span class="badge-neutral">${esc(run.config_snapshot?.agent_id || '—')}</span>`),
      detailRow('Model',  `<span class="badge-neutral">${esc(run.config_snapshot?.model || '—')}</span>`),
      detailRow('Confidence',
        `<span class="${confCls}">${esc(String(run.confidence_score))}</span> ` +
        `<span class="${confCls}">${esc(cl)}</span>${degraded}`),
    ].join(''));

    // ── Error ──
    if (run.error) {
      html += detailSection('Error', `<div class="detail-error">${esc(run.error)}</div>`);
    }

    // ── Conclusion ──
    if (run.conclusion) {
      html += detailSection('Conclusion',
        `<div class="detail-md md">${renderMd(run.conclusion)}</div>`);
    }

    // ── Thought log ──
    if (run.thought_log) {
      html += detailSection('Thought Log',
        `<div class="detail-adrnote badge-neutral" style="margin-bottom:8px">ADR-06 — structure ≠ truth</div>
         <div class="detail-md md">${renderMd(run.thought_log)}</div>`);
    } else if (run.scope === 'investor') {
      html += detailSection('Thought Log',
        `<div class="detail-adrnote">Excluded — Investor scope (SEC-01)</div>`);
    }

    // ── Data sources ──
    if (run.data_sources && run.data_sources.length) {
      const rows = run.data_sources.map(s =>
        detailRow(s.source,
          `<span class="source-status ${srcClass(s.status)}">${esc(s.status)}</span>` +
          (s.provenance_note ? ` <span class="detail-note">${esc(s.provenance_note)}</span>` : ''))
      ).join('');
      html += detailSection('Data Sources', rows);
    }

    // ── Reasoning objects ──
    if (run.reasoning_objects && run.reasoning_objects.length) {
      const objs = run.reasoning_objects.map(ro => {
        const statusCls = ro.parse_status === 'SUCCESS' ? 'badge-success'
                        : ro.parse_status === 'HALT'    ? 'badge-halt'
                        : 'badge-warning';
        return `<div class="detail-attempt">
          <div class="detail-attempt-header">
            <span class="badge ${statusCls}">Attempt ${ro.attempt_number}</span>
            <span class="badge-neutral">${esc(ro.parse_status)}</span>
            <code class="detail-ro-id">${esc((ro.reasoning_id || '').slice(0, 8))}…</code>
          </div>
          ${ro.raw_output?.text ? `
            <details class="detail-raw">
              <summary>Raw output</summary>
              <pre>${esc(ro.raw_output.text)}</pre>
            </details>` : ''}
        </div>`;
      }).join('');
      html += detailSection('Reasoning Objects', objs);
    }

    // ── Directive ──
    if (run.session?.directive_version) {
      html += detailSection('Directive',
        detailRow('Version', `<span class="badge-neutral">${esc(run.session.directive_version)}</span>`)
      );
    }

    // ── Consistency probe (ADR-06) ──
    if (run.consistency) {
      const c   = run.consistency;
      const cls = { HIGH: 'badge-success', MEDIUM: 'badge-warning', LOW: 'badge-halt' }[c.agreement] || 'badge-neutral';
      const flagRow = c.number_divergence_flag
        ? detailRow('Number divergence', `<span class="badge badge-halt">FLAGGED — value appears in one run only</span>`)
        : detailRow('Number divergence', `<span class="badge-neutral">none</span>`);
      let cHtml = [
        detailRow('Agreement', `<span class="badge ${cls}">${esc(c.agreement)}</span>`),
        detailRow('Score',     `<span class="badge-neutral">${esc(String(c.score))}</span>`),
        flagRow,
        detailRow('Word overlap',   `<span class="badge-neutral">${esc(String(c.word_overlap))}</span>`),
        detailRow('Number overlap', `<span class="badge-neutral">${esc(String(c.number_overlap))}</span>`),
      ].join('');
      if (c.divergent_numbers && c.divergent_numbers.length) {
        cHtml += detailRow('Divergent values', `<span class="detail-error-inline">${c.divergent_numbers.map(esc).join(', ')}</span>`);
      }
      if (c.probe_conclusion) {
        cHtml += `<div class="detail-probe-conclusion">
          <div class="detail-label" style="margin-bottom:4px">Probe conclusion</div>
          <div class="detail-md md">${renderMd(c.probe_conclusion)}</div>
        </div>`;
      }
      if (c.probe_error) {
        cHtml += detailRow('Error', `<span class="detail-error-inline">${esc(c.probe_error)}</span>`);
      }
      html += detailSection('Consistency Probe — ADR-06', cHtml);
    }

    // ── Claims (ADR-06) ──
    if (run.claims && run.claims.length) {
      const vRateLabel = (run.verification_rate != null)
        ? ` — <span class="badge-neutral">${Math.round(run.verification_rate * 100)}% citations verified</span>` : '';
      const claimRows = run.claims.map(c => {
        const icon = { citation: '🔗', quantitative: '📊', hedge: '⚠', causal: '→' }[c.claim_type] || '·';
        const cls  = { citation: 'claim-citation', quantitative: 'claim-quant', hedge: 'claim-hedge', causal: 'claim-causal' }[c.claim_type] || '';
        let vBadge = '';
        if (c.claim_type === 'citation') {
          if (c.verified === true)       vBadge = `<span class="badge badge-success">verified</span>`;
          else if (c.verified === false) vBadge = `<span class="badge badge-halt">not found</span>`;
          else                           vBadge = `<span class="badge-neutral">unattainable</span>`;
        }
        const urlLink = c.source_url && c.source_url !== 'N/A'
          ? ` <a class="claim-url" href="${esc(c.source_url)}" target="_blank" rel="noopener">${esc(c.source_url.slice(0, 50))}…</a>` : '';
        return `<div class="detail-claim">
          <span class="claim-pill ${cls}">${icon} ${esc(c.claim_type)}</span>
          <span class="detail-claim-text">${esc(c.text)}</span>
          ${vBadge}${urlLink}
          <div class="detail-claim-context">${esc(c.context)}</div>
        </div>`;
      }).join('');
      html += detailSection(`Claims — ${run.claims.length} extracted${vRateLabel}`, claimRows);
    }

    // ── Reviewer Flags (UN-05) ──
    const existingFlags = (flags || []).map(f =>
      `<div class="detail-flag">
        <span class="badge badge-warning">${esc(f.flag_type)}</span>
        <span class="detail-flag-ts">${esc(f.flagged_at)}</span>
        ${f.reviewer_note ? `<div class="detail-flag-note">${esc(f.reviewer_note)}</div>` : ''}
      </div>`
    ).join('') || '<div class="detail-note">No flags.</div>';

    // Flag form — only shown for auditor scope
    const flagForm = currentScope === 'auditor'
      ? `<form class="flag-form" id="flagForm" data-run-id="${esc(run.run_id)}">
          <select class="field-select flag-type-select" name="flag_type">
            <option value="Hallucinated">Hallucinated</option>
            <option value="Incorrect">Incorrect</option>
            <option value="Other">Other</option>
          </select>
          <textarea class="flag-note-input" name="reviewer_note"
                    placeholder="Optional reviewer note…" rows="2"></textarea>
          <button type="submit" class="btn-ghost small">Add Flag</button>
          <span class="flag-form-msg" id="flagFormMsg"></span>
        </form>`
      : `<div class="detail-note">Switch to Auditor scope to add flags.</div>`;

    html += detailSection('Reviewer Flags',
      existingFlags + '<div class="detail-flag-divider"></div>' + flagForm
    );

    return html;
  }

  function renderSessionDetailHtml(s) {
    const statusBadge = s.status === 'HALTED'
      ? `<span class="badge badge-halt">HALTED</span>`
      : `<span class="badge badge-success">COMPLETE</span>`;

    let html = '';
    html += detailSection('Session', [
      detailRow('Run ID',    `<code>${esc(s.run_id)}</code>`),
      detailRow('Ticker',    `<span class="badge-neutral">${esc(s.ticker || '—')}</span>`),
      detailRow('Status',    statusBadge),
      detailRow('Directive', `<span class="badge-neutral">${esc(s.directive_version || '—')}</span>`),
      detailRow('Confidence', s.run_confidence_score != null
        ? `<span class="badge-neutral">${esc(String(s.run_confidence_score))}</span> <span class="badge-neutral">${esc(s.confidence_classification || '—')}</span>`
        : '—'),
      detailRow('Initiated',  `<span class="detail-note">${esc(s.initiated_at || '—')}</span>`),
      detailRow('Completed',  `<span class="detail-note">${esc(s.completed_at || '—')}</span>`),
    ].join(''));

    if (s.directive_text) {
      html += detailSection('Directive Text',
        `<pre class="detail-directive">${esc(s.directive_text)}</pre>`);
    }

    return html;
  }

  // ── Detail modals ─────────────────────────────────────────────────────────────

  function showDetailModal(title, idText, bodyHtml) {
    detailModalTitle.textContent = title;
    detailModalId.textContent    = idText;
    detailModalJson.className    = 'modal-body detail-body';
    detailModalJson.innerHTML    = bodyHtml;
    detailModal.classList.remove('hidden');

    // Attach flag form handler after DOM is ready
    const form = detailModalJson.querySelector('#flagForm');
    if (form) {
      form.addEventListener('submit', async e => {
        e.preventDefault();
        const fd        = new FormData(form);
        const run_id    = form.dataset.runId;
        const flag_type = fd.get('flag_type');
        const note      = fd.get('reviewer_note') || null;
        const msgEl     = document.getElementById('flagFormMsg');

        try {
          const headers = {
            'Content-Type': 'application/json',
            ...(await authHeader('auditor')),
          };
          const res = await fetch(`/api/runs/${run_id}/flags`, {
            method:  'POST',
            headers,
            body:    JSON.stringify({ flag_type, reviewer_note: note }),
          });
          if (!res.ok) {
            const err = await res.json().catch(() => ({}));
            msgEl.textContent = '✗ ' + (err.detail || `HTTP ${res.status}`);
            msgEl.className   = 'flag-form-msg flag-form-err';
          } else {
            msgEl.textContent = '✓ Flag added';
            msgEl.className   = 'flag-form-msg flag-form-ok';
            form.querySelector('textarea').value = '';
            // Refresh the flags section without closing the modal
            const flags = await fetch(`/api/runs/${run_id}/flags`).then(r => r.json());
            const flagsContainer = form.closest('.detail-section-body');
            const existing = flagsContainer.querySelector('.detail-flag, .detail-note');
            // Re-render existing flags list
            const newFlagsHtml = flags.map(f =>
              `<div class="detail-flag">
                <span class="badge badge-warning">${esc(f.flag_type)}</span>
                <span class="detail-flag-ts">${esc(f.flagged_at)}</span>
                ${f.reviewer_note ? `<div class="detail-flag-note">${esc(f.reviewer_note)}</div>` : ''}
              </div>`
            ).join('') || '<div class="detail-note">No flags.</div>';

            // Replace everything before the divider
            const divider = flagsContainer.querySelector('.detail-flag-divider');
            if (divider) {
              let node = flagsContainer.firstChild;
              while (node && node !== divider) {
                const next = node.nextSibling;
                node.remove();
                node = next;
              }
              divider.insertAdjacentHTML('beforebegin', newFlagsHtml);
            }
          }
        } catch (err) {
          const msgEl2 = document.getElementById('flagFormMsg');
          if (msgEl2) { msgEl2.textContent = '✗ ' + err.message; msgEl2.className = 'flag-form-msg flag-form-err'; }
        }
      });
    }
  }

  async function openRunDetail(id) {
    showDetailModal('Run Record', (id || '').slice(0, 8) + '…', '<div class="detail-loading">Loading…</div>');
    try {
      const [run, flags] = await Promise.all([
        fetch(`/api/runs/${id}`).then(r => r.json()),
        fetch(`/api/runs/${id}/flags`).then(r => r.json()).catch(() => []),
      ]);
      showDetailModal('Run Record', (run.run_id || id).slice(0, 8) + '…', renderRunDetailHtml(run, flags));
    } catch (e) {
      detailModalJson.innerHTML = `<div class="detail-error">Failed to load: ${esc(e.message)}</div>`;
    }
  }

  async function openSessionDetail(id) {
    showDetailModal('Session Record', (id || '').slice(0, 8) + '…', '<div class="detail-loading">Loading…</div>');
    try {
      const s = await fetch(`/api/sessions/${id}`).then(r => r.json());
      showDetailModal('Session Record', s.ticker || (id || '').slice(0, 8) + '…', renderSessionDetailHtml(s));
    } catch (e) {
      detailModalJson.innerHTML = `<div class="detail-error">Failed to load: ${esc(e.message)}</div>`;
    }
  }

  function closeDetailModal()    { detailModal.classList.add('hidden'); }
  function closeDirectiveModal() { directiveModal.classList.add('hidden'); }

  btnCloseDetail.addEventListener('click',    closeDetailModal);
  btnCloseDirective.addEventListener('click', closeDirectiveModal);
  detailModal.addEventListener('click',    e => { if (e.target === detailModal)    closeDetailModal(); });
  directiveModal.addEventListener('click', e => { if (e.target === directiveModal) closeDirectiveModal(); });
  document.addEventListener('keydown', e => {
    if (e.key === 'Escape') { closeDetailModal(); closeDirectiveModal(); }
  });

  btnDirective.addEventListener('click', () => directiveModal.classList.remove('hidden'));

  // ── Clear runs ────────────────────────────────────────────────────────────────

  btnClear.addEventListener('click', async () => {
    try {
      await fetch('/api/runs', { method: 'DELETE' });
      auditRuns.innerHTML     = '<div class="audit-empty">No runs yet.</div>';
      auditSessions.innerHTML = '<div class="audit-empty">No sessions yet.</div>';
      runCountBadge.textContent  = '0';
      sessCountBadge.textContent = '0';
    } catch { /* silent */ }
  });

  // ── Init ──────────────────────────────────────────────────────────────────────

  (async function init() {
    setStatus('connecting');
    try {
      // Pre-warm both tokens so the UI is ready before first message
      await Promise.all([
        loadConfig(),
        loadDirective(),
        ensureToken('auditor'),
        ensureToken('investor'),
      ]);
      await refreshRuns();
      setStatus('ok');
    } catch (e) {
      console.error('Init failed:', e);
      setStatus('err');
    }
  })();

})();
