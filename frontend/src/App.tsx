import {
  BarChart3,
  BrainCircuit,
  Database,
  FileText,
  FileUp,
  KeyRound,
  Layers3,
  LockKeyhole,
  LogOut,
  ScrollText,
  ServerCog,
  MessageSquare,
  RefreshCw,
  Search,
  ShieldCheck,
  Users,
} from "lucide-react";
import { FormEvent, useEffect, useState } from "react";
import {
  clearStoredToken,
  generateFineTuningDataset,
  getAnalyticsSummary,
  getCurrentUser,
  getEvaluationResult,
  getFineTuningDataset,
  listDocuments,
  login,
  runEvaluation,
  sendChat,
  uploadDocument,
  type AnalyticsSummary,
  type ChatResponse,
  type DocumentRecord,
  type EvaluationResult,
  type FineTuningDataset,
  type User,
} from "./api/client";

type Tab = "chat" | "documents" | "analytics" | "fine_tuning" | "admin";
type ChatMode = "qa" | "report";
type ChatMessage = {
  id: string;
  question: string;
  mode: ChatMode;
  response: ChatResponse;
};

export function App() {
  const [tab, setTab] = useState<Tab>("chat");
  const [user, setUser] = useState<User | null>(null);
  const [checkingSession, setCheckingSession] = useState(true);

  useEffect(() => {
    getCurrentUser()
      .then(setUser)
      .catch(() => setUser(null))
      .finally(() => setCheckingSession(false));
  }, []);

  if (checkingSession) {
    return (
      <main className="auth-shell">
        <section className="login-panel">
          <p className="eyebrow">Enterprise AI</p>
          <h1>Checking Session</h1>
          <p className="muted">Preparing your secure workspace.</p>
        </section>
      </main>
    );
  }

  if (!user) {
    return <LoginPage onAuthenticated={setUser} />;
  }

  const canViewAdmin = user.role === "admin";

  return (
    <main className="app-shell">
      <aside className="sidebar">
        <div>
          <p className="eyebrow">Enterprise AI</p>
          <h1>Knowledge Intelligence</h1>
        </div>
        <nav className="nav-list" aria-label="Dashboard">
          <NavButton active={tab === "chat"} icon={<MessageSquare size={18} />} label="Chat" onClick={() => setTab("chat")} />
          <NavButton active={tab === "documents"} icon={<FileUp size={18} />} label="Documents" onClick={() => setTab("documents")} />
          <NavButton active={tab === "analytics"} icon={<BarChart3 size={18} />} label="Analytics" onClick={() => setTab("analytics")} />
          <NavButton active={tab === "fine_tuning"} icon={<BrainCircuit size={18} />} label="Fine-Tuning" onClick={() => setTab("fine_tuning")} />
          {canViewAdmin && <NavButton active={tab === "admin"} icon={<Users size={18} />} label="Admin" onClick={() => setTab("admin")} />}
        </nav>
        <div className="session-card">
          <div>
            <strong>{user.name}</strong>
            <span>
              {user.role} · {user.department}
            </span>
          </div>
          <button
            aria-label="Sign out"
            onClick={() => {
              clearStoredToken();
              setUser(null);
              setTab("chat");
            }}
            type="button"
          >
            <LogOut size={17} />
          </button>
        </div>
      </aside>

      <section className="workspace">
        {tab === "chat" && <ChatPage />}
        {tab === "documents" && <DocumentPage />}
        {tab === "analytics" && <AnalyticsPage />}
        {tab === "fine_tuning" && <FineTuningPage />}
        {tab === "admin" && canViewAdmin && <AdminPage currentUser={user} />}
      </section>
    </main>
  );
}

function LoginPage(props: { onAuthenticated: (user: User) => void }) {
  const [email, setEmail] = useState("atul@enterprise.ai");
  const [password, setPassword] = useState("atul123");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    setError("");
    setLoading(true);
    try {
      const result = await login(email.trim(), password);
      props.onAuthenticated(result.user);
    } catch {
      setError("Invalid email or password.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="auth-shell">
      <section className="login-panel">
        <div className="login-icon">
          <KeyRound size={24} />
        </div>
        <p className="eyebrow">Secure Access</p>
        <h1>Knowledge Intelligence</h1>
        <form className="login-form" onSubmit={onSubmit}>
          <label>
            <span>Email</span>
            <input value={email} onChange={(event) => setEmail(event.target.value)} type="email" />
          </label>
          <label>
            <span>Password</span>
            <input value={password} onChange={(event) => setPassword(event.target.value)} type="password" />
          </label>
          {error && <p className="login-error">{error}</p>}
          <button className="submit-button" disabled={loading} type="submit">
            {loading ? "Signing in..." : "Sign in"}
          </button>
        </form>
        <div className="demo-credentials">
          <strong>Demo users</strong>
          <span>Atul Admin: atul@enterprise.ai / atul123</span>
          <span>Analyst: analyst@enterprise.ai / analyst123</span>
          <span>Employee: employee@enterprise.ai / employee123</span>
          <span>Viewer: viewer@enterprise.ai / viewer123</span>
        </div>
      </section>
    </main>
  );
}

function NavButton(props: { active: boolean; icon: React.ReactNode; label: string; onClick: () => void }) {
  return (
    <button className={props.active ? "nav-button active" : "nav-button"} onClick={props.onClick} type="button">
      {props.icon}
      <span>{props.label}</span>
    </button>
  );
}

function ChatPage() {
  const [question, setQuestion] = useState("How many casual leaves are allowed?");
  const [mode, setMode] = useState<ChatMode>("qa");
  const [response, setResponse] = useState<ChatResponse | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [loading, setLoading] = useState(false);

  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    const askedQuestion = question.trim();
    if (!askedQuestion) return;

    setLoading(true);
    try {
      const nextResponse = await sendChat(askedQuestion, mode);
      setResponse(nextResponse);
      setMessages((current) => [
        {
          id: `${Date.now()}-${Math.random().toString(36).slice(2)}`,
          question: askedQuestion,
          mode,
          response: nextResponse,
        },
        ...current,
      ]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="page-grid">
      <section className="panel primary-panel">
        <div className="panel-header">
          <div>
            <p className="eyebrow">Multi-Agent RAG</p>
            <h2>Enterprise Chat</h2>
          </div>
          <ShieldCheck size={22} />
        </div>
        <div className="segmented-control" aria-label="Response mode">
          <button
            aria-pressed={mode === "qa"}
            className={mode === "qa" ? "selected" : ""}
            onClick={() => setMode("qa")}
            type="button"
          >
            Q&A
          </button>
          <button
            aria-pressed={mode === "report"}
            className={mode === "report" ? "selected" : ""}
            onClick={() => setMode("report")}
            type="button"
          >
            Report
          </button>
        </div>
        <form className="chat-form" onSubmit={onSubmit}>
          <textarea value={question} onChange={(event) => setQuestion(event.target.value)} />
          <button className="submit-button" type="submit" disabled={loading || !question.trim()}>
            {loading ? "Thinking..." : mode === "report" ? "Generate" : "Ask"}
          </button>
        </form>
        <div className="message-list">
          {messages.map((message) => (
            <div className="message-pair" key={message.id}>
              <p className="user-message">
                <span>{message.mode === "report" ? "Report" : "Q&A"}</span>
                {message.question}
              </p>
              <p className="assistant-message">{message.response.answer}</p>
              <span className="status-pill">{message.response.validation_status}</span>
            </div>
          ))}
        </div>
        {response && !messages.length && (
          <div className="answer-block">
            <p>{response.answer}</p>
            <span className="status-pill">{response.validation_status}</span>
          </div>
        )}
      </section>

      <section className="panel">
        <div className="panel-header">
          <h2>Sources</h2>
        </div>
        <div className="source-list">
          {response?.sources.length ? (
            response.sources.map((source) => (
              <article className="source-item" key={source.chunk_id}>
                <strong>{source.document_name}</strong>
                <span>
                  {source.department} · {source.document_type} · {source.access_level}
                </span>
                <span>{source.chunk_id}</span>
                <p>{source.excerpt}</p>
              </article>
            ))
          ) : (
            <p className="muted">Source citations will appear after documents are indexed.</p>
          )}
        </div>
      </section>
    </div>
  );
}

function DocumentPage() {
  const [status, setStatus] = useState("Ready to index PDF, DOCX, TXT, MD, or CSV files.");
  const [documents, setDocuments] = useState<DocumentRecord[]>([]);
  const [documentSearch, setDocumentSearch] = useState("");
  const [department, setDepartment] = useState("HR");
  const [documentType, setDocumentType] = useState("Policy");
  const [accessLevel, setAccessLevel] = useState("internal");

  useEffect(() => {
    refreshDocuments();
  }, []);

  async function onFileChange(event: React.ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (!file) return;

    setStatus("Uploading and indexing...");
    const result = await uploadDocument(file, {
      department,
      document_type: documentType,
      access_level: accessLevel,
    });
    setStatus(`${result.filename} indexed with ${result.chunks_created} chunks.`);
    await refreshDocuments();
    event.target.value = "";
  }

  async function refreshDocuments() {
    try {
      setDocuments(await listDocuments());
    } catch {
      setStatus("Document list is unavailable while the backend is starting.");
    }
  }

  const filteredDocuments = documents.filter((document) => {
    const haystack = [
      document.filename,
      document.department,
      document.document_type,
      document.access_level,
      document.status,
    ]
      .join(" ")
      .toLowerCase();
    return haystack.includes(documentSearch.trim().toLowerCase());
  });

  const totalChunks = documents.reduce((sum, document) => sum + document.chunks_created, 0);
  const restrictedCount = documents.filter((document) => document.access_level === "restricted").length;
  const departments = new Set(documents.map((document) => document.department)).size;

  return (
    <section className="panel full-panel">
      <div className="panel-header">
        <div>
          <p className="eyebrow">Document Store</p>
          <h2>Upload Enterprise Knowledge</h2>
        </div>
        <button className="icon-action-button secondary-action" onClick={refreshDocuments} type="button">
          <RefreshCw size={18} />
          <span>Refresh</span>
        </button>
      </div>
      <div className="document-summary-grid">
        <DocumentSummary icon={<Database size={18} />} label="Documents" value={documents.length.toString()} />
        <DocumentSummary icon={<Layers3 size={18} />} label="Chunks" value={totalChunks.toString()} />
        <DocumentSummary icon={<LockKeyhole size={18} />} label="Restricted" value={restrictedCount.toString()} />
        <DocumentSummary icon={<Users size={18} />} label="Departments" value={departments.toString()} />
      </div>
      <label className="upload-zone">
        <input type="file" accept=".pdf,.docx,.txt,.md,.csv" onChange={onFileChange} />
        <span>
          <FileUp size={18} />
          Select document
        </span>
      </label>
      <div className="metadata-grid">
        <label>
          <span>Department</span>
          <select value={department} onChange={(event) => setDepartment(event.target.value)}>
            <option>HR</option>
            <option>IT</option>
            <option>Security</option>
            <option>Finance</option>
            <option>Operations</option>
            <option>General</option>
          </select>
        </label>
        <label>
          <span>Document Type</span>
          <select value={documentType} onChange={(event) => setDocumentType(event.target.value)}>
            <option>Policy</option>
            <option>SOP</option>
            <option>Technical Manual</option>
            <option>Report</option>
            <option>Knowledge Base</option>
          </select>
        </label>
        <label>
          <span>Access Level</span>
          <select value={accessLevel} onChange={(event) => setAccessLevel(event.target.value)}>
            <option value="internal">Internal</option>
            <option value="restricted">Restricted</option>
            <option value="public">Public</option>
          </select>
        </label>
      </div>
      <p className="muted">{status}</p>
      <div className="document-toolbar">
        <div className="search-box">
          <Search size={18} />
          <input
            aria-label="Search documents"
            placeholder="Search documents"
            type="search"
            value={documentSearch}
            onChange={(event) => setDocumentSearch(event.target.value)}
          />
        </div>
        <span className="status-pill">{filteredDocuments.length} visible</span>
      </div>
      <div className="document-list">
        {filteredDocuments.length ? (
          filteredDocuments.map((document) => (
            <article className="document-row" key={document.id}>
              <FileText size={18} />
              <div className="document-row-main">
                <div className="document-row-title">
                  <strong>{document.filename}</strong>
                  <span className={document.status === "indexed" ? "status-pill compact-pill" : "status-pill warning compact-pill"}>
                    {document.status}
                  </span>
                </div>
                <div className="document-tags">
                  <span>{document.department}</span>
                  <span>{document.document_type}</span>
                  <span>{document.access_level}</span>
                  <span>{document.chunks_created} chunks</span>
                </div>
                <span className="document-path">{document.source_path}</span>
              </div>
              <div className="document-row-meta">
                <span>{formatDateTime(document.uploaded_at)}</span>
              </div>
            </article>
          ))
        ) : documents.length ? (
          <p className="muted">No documents match the current search.</p>
        ) : (
          <p className="muted">Indexed documents will appear here.</p>
        )}
      </div>
    </section>
  );
}

function DocumentSummary(props: { icon: React.ReactNode; label: string; value: string }) {
  return (
    <div className="document-summary-tile">
      {props.icon}
      <span>{props.label}</span>
      <strong>{props.value}</strong>
    </div>
  );
}

function AnalyticsPage() {
  const [summary, setSummary] = useState<AnalyticsSummary | null>(null);
  const [evaluation, setEvaluation] = useState<EvaluationResult | null>(null);
  const [running, setRunning] = useState(false);

  useEffect(() => {
    getAnalyticsSummary().then(setSummary).catch(() => setSummary(null));
    getEvaluationResult().then(setEvaluation).catch(() => setEvaluation(null));
  }, []);

  const metrics = [
    ["Queries", summary?.queries_processed.toString() ?? "0"],
    ["Faithfulness", formatMetric(summary?.faithfulness)],
    ["Context Precision", formatMetric(summary?.context_precision)],
    ["Hallucination Rate", formatMetric(summary?.hallucination_rate)],
  ];

  return (
    <section className="panel full-panel">
      <div className="panel-header">
        <div>
          <p className="eyebrow">RAGAS</p>
          <h2>Evaluation Dashboard</h2>
        </div>
        <button className="icon-action-button" onClick={handleRunEvaluation} type="button" disabled={running}>
          <BarChart3 size={18} />
          <span>{running ? "Running" : "Run Evaluation"}</span>
        </button>
      </div>
      <div className="metric-grid">
        {metrics.map(([label, value]) => (
          <div className="metric-tile" key={label}>
            <span>{label}</span>
            <strong>{value}</strong>
          </div>
        ))}
      </div>
      <section className="evaluation-section">
        <div className="panel-header compact-header">
          <div>
            <p className="eyebrow">Benchmark</p>
            <h2>Evaluation Suite</h2>
          </div>
          <span className="status-pill">{evaluation?.summary.total_cases ?? 0} cases</span>
        </div>
        <div className="metric-grid evaluation-metrics">
          <MetricTile label="Context Recall" value={formatMetric(evaluation?.summary.context_recall)} />
          <MetricTile label="Answer Relevancy" value={formatMetric(evaluation?.summary.answer_relevancy)} />
          <MetricTile label="Pass Rate" value={formatPassRate(evaluation)} />
        </div>
        <div className="evaluation-list">
          {evaluation?.cases.length ? (
            evaluation.cases.map((result) => (
              <article className="evaluation-row" key={result.id}>
                <div>
                  <strong>{result.question}</strong>
                  <span>{result.expected_source} · top source: {result.top_source ?? "none"}</span>
                  <p>{result.answer}</p>
                </div>
                <span className={result.passed ? "status-pill" : "status-pill warning"}>{result.passed ? "passed" : "review"}</span>
              </article>
            ))
          ) : (
            <p className="muted">Run the evaluation suite to generate benchmark scores.</p>
          )}
        </div>
      </section>
    </section>
  );

  async function handleRunEvaluation() {
    setRunning(true);
    try {
      setEvaluation(await runEvaluation());
      setSummary(await getAnalyticsSummary());
    } finally {
      setRunning(false);
    }
  }
}

function formatMetric(value?: number) {
  return value === undefined ? "0.00" : value.toFixed(2);
}

function formatDateTime(value: string) {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "Unknown";

  return new Intl.DateTimeFormat(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(date);
}

function formatPassRate(evaluation: EvaluationResult | null) {
  if (!evaluation?.cases.length) return "0.00";
  const passed = evaluation.cases.filter((result) => result.passed).length;
  return (passed / evaluation.cases.length).toFixed(2);
}

function MetricTile(props: { label: string; value: string }) {
  return (
    <div className="metric-tile">
      <span>{props.label}</span>
      <strong>{props.value}</strong>
    </div>
  );
}

function FineTuningPage() {
  const [dataset, setDataset] = useState<FineTuningDataset | null>(null);
  const [generating, setGenerating] = useState(false);

  useEffect(() => {
    getFineTuningDataset().then(setDataset).catch(() => setDataset(null));
  }, []);

  async function handleGenerate() {
    setGenerating(true);
    try {
      setDataset(await generateFineTuningDataset());
    } finally {
      setGenerating(false);
    }
  }

  return (
    <section className="panel full-panel">
      <div className="panel-header">
        <div>
          <p className="eyebrow">QLoRA Preparation</p>
          <h2>Fine-Tuning Dataset</h2>
        </div>
        <button className="icon-action-button" onClick={handleGenerate} type="button" disabled={generating}>
          <BrainCircuit size={18} />
          <span>{generating ? "Generating" : "Generate Dataset"}</span>
        </button>
      </div>
      <div className="metric-grid fine-tuning-metrics">
        <MetricTile label="Examples" value={(dataset?.examples_count ?? 0).toString()} />
        <MetricTile label="Format" value={dataset?.format ?? "jsonl"} />
        <MetricTile label="Status" value={dataset?.status ?? "not ready"} />
      </div>
      <p className="muted path-text">{dataset?.dataset_path ?? "Dataset will be generated from indexed enterprise documents."}</p>
      <div className="command-panel">
        <span>Training command</span>
        <code>python fine_tuning/train_qlora.py --config fine_tuning/qlora_config.json</code>
      </div>
      <div className="dataset-preview-list">
        {dataset?.preview.length ? (
          dataset.preview.map((example, index) => (
            <article className="dataset-preview-card" key={`${example.instruction}-${index}`}>
              <span>
                {example.metadata.department} · {example.metadata.document_type} · {example.metadata.document_name}
              </span>
              <strong>{example.instruction}</strong>
              <p>{example.output}</p>
            </article>
          ))
        ) : (
          <p className="muted">Generate the dataset to preview instruction-response examples.</p>
        )}
      </div>
    </section>
  );
}

function AdminPage(props: { currentUser: User }) {
  const [summary, setSummary] = useState<AnalyticsSummary | null>(null);
  const [documents, setDocuments] = useState<DocumentRecord[]>([]);

  useEffect(() => {
    getAnalyticsSummary().then(setSummary).catch(() => setSummary(null));
    listDocuments().then(setDocuments).catch(() => setDocuments([]));
  }, []);

  const restrictedDocuments = documents.filter((document) => document.access_level === "restricted").length;
  const indexedDocuments = documents.filter((document) => document.status === "indexed").length;
  const users = [
    { name: "Atul", role: "Admin", department: "IT", status: "Active" },
    { name: "Rahul Mehta", role: "Analyst", department: "Operations", status: "Active" },
    { name: "Priya Shah", role: "Employee", department: "HR", status: "Active" },
    { name: "Karan Iyer", role: "Viewer", department: "Security", status: "Review" },
  ];
  const auditEvents = [
    `${indexedDocuments} indexed documents available for retrieval`,
    `${restrictedDocuments} restricted documents protected by metadata labels`,
    `${summary?.queries_processed ?? 0} enterprise queries processed`,
    `Hallucination rate currently ${formatMetric(summary?.hallucination_rate)}`,
  ];

  return (
    <section className="panel full-panel">
      <div className="panel-header">
        <div>
          <p className="eyebrow">Operations</p>
          <h2>Admin Panel</h2>
          <p className="muted compact-copy">Signed in as {props.currentUser.name}</p>
        </div>
        <ServerCog size={22} />
      </div>
      <div className="admin-summary-grid">
        <DocumentSummary icon={<Users size={18} />} label="Users" value={users.length.toString()} />
        <DocumentSummary icon={<FileText size={18} />} label="Indexed Docs" value={indexedDocuments.toString()} />
        <DocumentSummary icon={<LockKeyhole size={18} />} label="Restricted Docs" value={restrictedDocuments.toString()} />
        <DocumentSummary icon={<ShieldCheck size={18} />} label="Faithfulness" value={formatMetric(summary?.faithfulness)} />
      </div>
      <div className="admin-grid">
        <section className="admin-section">
          <div className="admin-section-header">
            <Users size={18} />
            <strong>User Management</strong>
          </div>
          <div className="admin-table">
            {users.map((user) => (
              <div className="admin-table-row" key={user.name}>
                <div>
                  <strong>{user.name}</strong>
                  <span>{user.department}</span>
                </div>
                <span>{user.role}</span>
                <span className={user.status === "Active" ? "status-pill compact-pill" : "status-pill warning compact-pill"}>
                  {user.status}
                </span>
              </div>
            ))}
          </div>
        </section>
        <section className="admin-section">
          <div className="admin-section-header">
            <ScrollText size={18} />
            <strong>Audit Activity</strong>
          </div>
          <div className="audit-list">
            {auditEvents.map((event) => (
              <div className="audit-row" key={event}>
                <span />
                <p>{event}</p>
              </div>
            ))}
          </div>
        </section>
        <section className="admin-section wide-admin-section">
          <div className="admin-section-header">
            <ShieldCheck size={18} />
            <strong>Governance Controls</strong>
          </div>
          <div className="governance-grid">
            <div>
              <span>Validation Agent</span>
              <strong>Enabled</strong>
              <p>Responses are checked against retrieved context before delivery.</p>
            </div>
            <div>
              <span>Source Citations</span>
              <strong>Required</strong>
              <p>Each answer returns document evidence and metadata labels.</p>
            </div>
            <div>
              <span>Access Metadata</span>
              <strong>Tracked</strong>
              <p>Documents retain department, type, and access-level tags.</p>
            </div>
          </div>
        </section>
      </div>
    </section>
  );
}
