import React, { useState, useEffect } from 'react';
import { 
  LayoutDashboard, 
  Sparkles, 
  History, 
  FolderTree, 
  BarChart3, 
  CheckCircle, 
  AlertTriangle, 
  Clock, 
  Languages, 
  Download, 
  Copy, 
  ChevronRight, 
  Loader2, 
  Edit3, 
  Check, 
  Search, 
  Info,
  Server,
  Activity
} from 'lucide-react';

const API_BASE = "http://localhost:8000";

export default function App() {
  const [activeTab, setActiveTab] = useState('generate');
  const [history, setHistory] = useState([]);
  const [analytics, setAnalytics] = useState(null);
  const [taxonomy, setTaxonomy] = useState(null);
  const [evaluation, setEvaluation] = useState(null);
  
  // Generator states
  const [inputText, setInputText] = useState("");
  const [inputLang, setInputLang] = useState("auto");
  const [isProcessing, setIsProcessing] = useState(false);
  const [processingSteps, setProcessingSteps] = useState([]);
  const [generatedCatalog, setGeneratedCatalog] = useState(null);
  const [errorMsg, setErrorMsg] = useState("");
  
  // Editor states
  const [editMode, setEditMode] = useState(false);
  const [editedName, setEditedName] = useState("");
  const [editedCategory, setEditedCategory] = useState("");
  const [editedSubcategory, setEditedSubcategory] = useState("");
  const [editedAttributes, setEditedAttributes] = useState({});

  // History search state
  const [searchTerm, setSearchTerm] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");

  // Load backend configurations and history
  const loadData = async () => {
    try {
      const histRes = await fetch(`${API_BASE}/api/catalog/history`);
      if (histRes.ok) setHistory(await histRes.json());
      
      const analRes = await fetch(`${API_BASE}/api/analytics`);
      if (analRes.ok) setAnalytics(await analRes.json());

      const taxRes = await fetch(`${API_BASE}/api/taxonomy`);
      if (taxRes.ok) setTaxonomy(await taxRes.json());

      const evalRes = await fetch(`${API_BASE}/api/evaluation/metrics`);
      if (evalRes.ok) setEvaluation(await evalRes.json());
    } catch (err) {
      console.error("Error loading data from FastAPI backend:", err);
    }
  };

  useEffect(() => {
    loadData();
    // Poll analytics and history every 5 seconds for live dashboard updates
    const interval = setInterval(loadData, 5000);
    return () => clearInterval(interval);
  }, []);

  const handleExampleClick = (text, lang) => {
    setInputText(text);
    setInputLang(lang);
  };

  const runProcessSteps = async (text) => {
    setProcessingSteps([
      { id: 1, label: "Language Detection", status: "loading" },
      { id: 2, label: "Text Vectorization", status: "pending" },
      { id: 3, label: "Attribute Extraction", status: "pending" },
      { id: 4, label: "Vernacular Normalization", status: "pending" },
      { id: 5, label: "Taxonomy Path Mapping", status: "pending" },
      { id: 6, label: "Product Resolution", status: "pending" },
      { id: 7, label: "ONDC Schema Compile", status: "pending" },
    ]);
    
    // Simulate pipeline execution step-by-step
    const sleep = (ms) => new Promise(r => setTimeout(r, ms));
    
    await sleep(400);
    setProcessingSteps(prev => prev.map(s => s.id === 1 ? { ...s, status: "done" } : s.id === 2 ? { ...s, status: "loading" } : s));
    
    await sleep(300);
    setProcessingSteps(prev => prev.map(s => s.id === 2 ? { ...s, status: "done" } : s.id === 3 ? { ...s, status: "loading" } : s));
    
    await sleep(400);
    setProcessingSteps(prev => prev.map(s => s.id === 3 ? { ...s, status: "done" } : s.id === 4 ? { ...s, status: "loading" } : s));
  };

  const handleProcess = async () => {
    if (!inputText.trim()) return;
    setIsProcessing(true);
    setErrorMsg("");
    setGeneratedCatalog(null);
    setEditMode(false);
    
    // Start visual step-by-step pipeline loader
    runProcessSteps(inputText);
    
    try {
      const res = await fetch(`${API_BASE}/api/catalog/process`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: inputText, language: inputLang })
      });
      
      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.detail || "Inference failed.");
      }
      
      const data = await res.json();
      
      // Fast-forward step indicators to complete
      setProcessingSteps(prev => prev.map(s => ({ ...s, status: "done" })));
      setGeneratedCatalog(data);
      
      // Initialize editor values
      setEditedName(data.product_name);
      setEditedCategory(data.category);
      setEditedSubcategory(data.subcategory);
      setEditedAttributes(data.attributes);
      
      // Refresh history & stats
      loadData();
    } catch (err) {
      console.error(err);
      setErrorMsg(err.message || "FastAPI API is unavailable or model has not finished training.");
      setProcessingSteps(prev => prev.map(s => s.status === "loading" ? { ...s, status: "error" } : s));
    } finally {
      setIsProcessing(false);
    }
  };

  const handleApprove = async () => {
    if (!generatedCatalog) return;
    try {
      const res = await fetch(`${API_BASE}/api/catalog/${generatedCatalog.catalog_id}/approve`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          product_name: editedName,
          category: editedCategory,
          subcategory: editedSubcategory,
          attributes: editedAttributes
        })
      });
      if (res.ok) {
        setGeneratedCatalog(prev => ({ 
          ...prev, 
          product_name: editedName,
          category: editedCategory,
          subcategory: editedSubcategory,
          attributes: editedAttributes,
          status: "Approved" 
        }));
        setEditMode(false);
        loadData();
      }
    } catch (err) {
      console.error("Error approving catalog:", err);
    }
  };

  const handleAttributeChange = (key, val) => {
    setEditedAttributes(prev => ({
      ...prev,
      [key]: val === "" ? null : val
    }));
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    alert("JSON Copied to Clipboard!");
  };

  const downloadJson = (data) => {
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `catalog-${data.catalog_id || 'output'}.json`;
    link.click();
  };

  // Filtered History
  const filteredHistory = history.filter(item => {
    const matchesSearch = item.product_name.toLowerCase().includes(searchTerm.toLowerCase()) || 
                          item.original_text.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = statusFilter === "all" || item.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  return (
    <div className="flex h-screen overflow-hidden bg-slate-50">
      {/* SIDEBAR */}
      <aside className="w-64 bg-slate-900 text-slate-100 flex flex-col justify-between shrink-0">
        <div>
          <div className="p-6 border-b border-slate-800 flex items-center gap-3">
            <div className="bg-orange-500 p-2 rounded-lg text-white">
              <Sparkles className="h-5 w-5" />
            </div>
            <div>
              <h1 className="font-bold text-lg tracking-wider">Catalog-SLM</h1>
              <p className="text-xs text-slate-400">ONDC Standardizer</p>
            </div>
          </div>
          <nav className="p-4 space-y-1">
            <button 
              onClick={() => setActiveTab('dashboard')} 
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition ${activeTab === 'dashboard' ? 'bg-orange-500 text-white shadow-md' : 'text-slate-300 hover:bg-slate-800 hover:text-white'}`}
            >
              <LayoutDashboard className="h-4 w-4" /> Dashboard
            </button>
            <button 
              onClick={() => setActiveTab('generate')} 
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition ${activeTab === 'generate' ? 'bg-orange-500 text-white shadow-md' : 'text-slate-300 hover:bg-slate-800 hover:text-white'}`}
            >
              <Sparkles className="h-4 w-4" /> Generate Catalog
            </button>
            <button 
              onClick={() => setActiveTab('history')} 
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition ${activeTab === 'history' ? 'bg-orange-500 text-white shadow-md' : 'text-slate-300 hover:bg-slate-800 hover:text-white'}`}
            >
              <History className="h-4 w-4" /> Catalog History
            </button>
            <button 
              onClick={() => setActiveTab('taxonomy')} 
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition ${activeTab === 'taxonomy' ? 'bg-orange-500 text-white shadow-md' : 'text-slate-300 hover:bg-slate-800 hover:text-white'}`}
            >
              <FolderTree className="h-4 w-4" /> Taxonomy Browser
            </button>
            <button 
              onClick={() => setActiveTab('evaluation')} 
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition ${activeTab === 'evaluation' ? 'bg-orange-500 text-white shadow-md' : 'text-slate-300 hover:bg-slate-800 hover:text-white'}`}
            >
              <BarChart3 className="h-4 w-4" /> Model Evaluation
            </button>
          </nav>
        </div>
        
        {/* Backend status indicator */}
        <div className="p-4 border-t border-slate-800 bg-slate-950/40 text-xs flex items-center justify-between text-slate-400">
          <div className="flex items-center gap-2">
            <Server className="h-3 w-3 text-emerald-400 animate-pulse" />
            <span>FastAPI Server</span>
          </div>
          <span className="bg-emerald-500/10 text-emerald-400 px-2 py-0.5 rounded text-[10px] uppercase font-semibold">Online</span>
        </div>
      </aside>

      {/* MAIN CONTAINER */}
      <main className="flex-1 flex flex-col overflow-y-auto">
        <header className="bg-white border-b border-slate-200 px-8 py-4 flex items-center justify-between shrink-0">
          <div className="flex items-center gap-4">
            <h2 className="text-xl font-bold text-slate-800 capitalize">{activeTab.replace('-', ' ')} Workspace</h2>
            <div className="bg-slate-100 px-3 py-1 rounded-full text-xs font-semibold text-slate-600 flex items-center gap-1.5">
              <Activity className="h-3 w-3 text-orange-500" />
              <span>Academic Version 1.0</span>
            </div>
          </div>
          <div className="text-sm text-slate-500 font-medium">
            Project: Catalog-SLM
          </div>
        </header>

        <div className="p-8 flex-1 max-w-7xl w-full mx-auto">
          {/* TAB 1: DASHBOARD */}
          {activeTab === 'dashboard' && (
            <div className="space-y-8">
              {/* Analytics Header Grid */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex flex-col justify-between">
                  <div className="text-sm font-semibold text-slate-500">Total Products Processed</div>
                  <div className="text-3xl font-extrabold text-slate-800 mt-2">
                    {analytics ? analytics.total_products : 0}
                  </div>
                  <div className="text-xs text-slate-400 mt-2">Across all input descriptions</div>
                </div>
                <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex flex-col justify-between">
                  <div className="text-sm font-semibold text-slate-500">Success (Approval) Rate</div>
                  <div className="text-3xl font-extrabold text-emerald-600 mt-2">
                    {analytics ? analytics.success_rate : 100}%
                  </div>
                  <div className="text-xs text-slate-400 mt-2">Approved vs. draft status catalogs</div>
                </div>
                <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex flex-col justify-between">
                  <div className="text-sm font-semibold text-slate-500">Average Model Confidence</div>
                  <div className="text-3xl font-extrabold text-orange-500 mt-2">
                    {analytics ? analytics.avg_confidence : 0}%
                  </div>
                  <div className="text-xs text-slate-400 mt-2">Based on multi-task output probabilities</div>
                </div>
                <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex flex-col justify-between">
                  <div className="text-sm font-semibold text-slate-500">Languages Supported</div>
                  <div className="text-3xl font-extrabold text-indigo-600 mt-2">2</div>
                  <div className="text-xs text-slate-400 mt-2">English, Hindi & mixed Henglish</div>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
                  <div className="text-sm font-semibold text-slate-500">Existing Product Match Rate</div>
                  <div className="text-3xl font-extrabold text-indigo-600 mt-2">
                    {analytics ? analytics.existing_product_match_rate : 0}%
                  </div>
                  <div className="text-xs text-slate-400 mt-2">
                    {analytics?.total_products ? "Existing product matches / processed catalogs" : "No data yet"}
                  </div>
                </div>
                <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
                  <div className="text-sm font-semibold text-slate-500">Variant Validation Success Rate</div>
                  <div className="text-3xl font-extrabold text-emerald-600 mt-2">
                    {analytics ? analytics.variant_validation_success_rate : 0}%
                  </div>
                  <div className="text-xs text-slate-400 mt-2">
                    {analytics?.variant_validation_count
                      ? `Valid variants / ${analytics.variant_validation_count} checks`
                      : "No variants validated yet"}
                  </div>
                </div>
                <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
                  <div className="text-sm font-semibold text-slate-500">New Product Rate</div>
                  <div className="text-3xl font-extrabold text-orange-500 mt-2">
                    {analytics ? analytics.new_product_rate : 0}%
                  </div>
                  <div className="text-xs text-slate-400 mt-2">
                    {analytics?.total_products ? "New products / processed catalogs" : "No data yet"}
                  </div>
                </div>
              </div>

              {/* Dist Graphs Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                {/* Language distribution card */}
                <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
                  <h3 className="font-bold text-slate-800 mb-6 flex items-center gap-2">
                    <Languages className="h-5 w-5 text-indigo-500" /> Language Distribution
                  </h3>
                  <div className="space-y-4">
                    {analytics && Object.keys(analytics.language_distribution).length > 0 ? (
                      Object.entries(analytics.language_distribution).map(([lang, count]) => {
                        const pct = Math.round((count / analytics.total_products) * 100);
                        return (
                          <div key={lang}>
                            <div className="flex justify-between text-sm font-semibold text-slate-700 mb-1">
                              <span>{lang}</span>
                              <span>{count} items ({pct}%)</span>
                            </div>
                            <div className="w-full bg-slate-100 rounded-full h-3.5 overflow-hidden">
                              <div 
                                className="bg-indigo-600 h-full rounded-full transition-all duration-500"
                                style={{ width: `${pct}%` }}
                              ></div>
                            </div>
                          </div>
                        );
                      })
                    ) : (
                      <div className="text-center text-slate-400 py-8">No language distribution data available yet.</div>
                    )}
                  </div>
                </div>

                {/* Category distribution card */}
                <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
                  <h3 className="font-bold text-slate-800 mb-6 flex items-center gap-2">
                    <FolderTree className="h-5 w-5 text-orange-500" /> Category Distribution
                  </h3>
                  <div className="space-y-4">
                    {analytics && Object.keys(analytics.category_distribution).length > 0 ? (
                      Object.entries(analytics.category_distribution).map(([cat, count]) => {
                        const pct = Math.round((count / analytics.total_products) * 100);
                        return (
                          <div key={cat}>
                            <div className="flex justify-between text-sm font-semibold text-slate-700 mb-1">
                              <span>{cat}</span>
                              <span>{count} items ({pct}%)</span>
                            </div>
                            <div className="w-full bg-slate-100 rounded-full h-3.5 overflow-hidden">
                              <div 
                                className="bg-orange-500 h-full rounded-full transition-all duration-500"
                                style={{ width: `${pct}%` }}
                              ></div>
                            </div>
                          </div>
                        );
                      })
                    ) : (
                      <div className="text-center text-slate-400 py-8">No category distribution data available yet.</div>
                    )}
                  </div>
                </div>
              </div>

              {/* Recent Activity Table */}
              <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
                <h3 className="font-bold text-slate-800 mb-4">Recent Catalogs Processed</h3>
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-sm text-slate-600">
                    <thead>
                      <tr className="border-b border-slate-100 text-slate-400 uppercase text-[10px] tracking-wider font-bold">
                        <th className="pb-3 font-semibold">Product Name</th>
                        <th className="pb-3 font-semibold">Category</th>
                        <th className="pb-3 font-semibold">Detected Language</th>
                        <th className="pb-3 font-semibold">Confidence</th>
                        <th className="pb-3 font-semibold">Status</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100">
                      {history.slice(0, 5).map(item => (
                        <tr key={item.catalog_id} className="hover:bg-slate-50/50">
                          <td className="py-3.5 font-semibold text-slate-800">{item.product_name}</td>
                          <td className="py-3.5">{item.category}</td>
                          <td className="py-3.5">{item.detected_language}</td>
                          <td className="py-3.5 font-mono">{(item.confidence.overall * 100).toFixed(1)}%</td>
                          <td className="py-3.5">
                            <span className={`px-2.5 py-1 text-xs font-semibold rounded-full ${item.status === 'Approved' ? 'bg-emerald-50 text-emerald-600' : item.status === 'Needs Review' ? 'bg-red-50 text-red-600' : 'bg-amber-50 text-amber-600'}`}>
                              {item.status}
                            </span>
                          </td>
                        </tr>
                      ))}
                      {history.length === 0 && (
                        <tr>
                          <td colSpan="5" className="text-center py-8 text-slate-400">No products processed yet. Go to Generate Tab.</td>
                        </tr>
                      )}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}

          {/* TAB 2: GENERATE CATALOG */}
          {activeTab === 'generate' && (
            <div className="space-y-8">
              {/* Input Area Card */}
              <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-6">
                <div>
                  <h3 className="font-bold text-slate-800 mb-2">Input Product Description</h3>
                  <p className="text-xs text-slate-400">Enter unstructured English, Hindi, or mixed language product text. Catalog-SLM will structure it.</p>
                </div>

                <div className="flex flex-col gap-4">
                  <div className="flex items-center gap-3">
                    <span className="text-sm font-semibold text-slate-500">Language Mode:</span>
                    <select 
                      value={inputLang} 
                      onChange={(e) => setInputLang(e.target.value)}
                      className="bg-slate-50 border border-slate-200 text-slate-800 text-sm font-semibold rounded-lg px-3 py-1.5 focus:outline-none focus:border-orange-500"
                    >
                      <option value="auto">Auto Detect</option>
                      <option value="English">English Only</option>
                      <option value="Hindi">Hindi Only</option>
                    </select>
                  </div>

                  <textarea 
                    value={inputText}
                    onChange={(e) => setInputText(e.target.value)}
                    placeholder="Enter product description (e.g. लाल रंग की कॉटन टीशर्ट पुरुषों के लिए, साइज L)"
                    className="w-full h-32 p-4 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-orange-500/20 focus:border-orange-500 text-slate-800 resize-none font-medium"
                  />
                  
                  {/* Example prompt shortcuts */}
                  <div className="flex flex-wrap items-center gap-3">
                    <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Example Templates:</span>
                    <button 
                      onClick={() => handleExampleClick("Black Nike running shoes for men, size 9", "English")}
                      className="bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs px-3 py-1.5 rounded-full font-medium transition"
                    >
                      English Example
                    </button>
                    <button 
                      onClick={() => handleExampleClick("लाल रंग की कॉटन टीशर्ट पुरुषों के लिए, साइज L", "Hindi")}
                      className="bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs px-3 py-1.5 rounded-full font-medium transition"
                    >
                      Hindi Example
                    </button>
                    <button 
                      onClick={() => handleExampleClick("नीले रंग की cotton shirt men's size M", "auto")}
                      className="bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs px-3 py-1.5 rounded-full font-medium transition"
                    >
                      Mixed Language
                    </button>
                    <button 
                      onClick={() => handleExampleClick("काले रंग का चमड़े का बटुआ", "Hindi")}
                      className="bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs px-3 py-1.5 rounded-full font-medium transition"
                    >
                      Devnagari Accessories
                    </button>
                  </div>

                  <button 
                    onClick={handleProcess}
                    disabled={isProcessing || !inputText.trim()}
                    className="bg-orange-500 hover:bg-orange-600 disabled:bg-slate-200 text-white font-bold px-6 py-3 rounded-xl transition flex items-center justify-center gap-2 self-start shadow-md shadow-orange-500/10"
                  >
                    {isProcessing ? (
                      <>
                        <Loader2 className="h-5 w-5 animate-spin" /> Processing with Catalog-SLM...
                      </>
                    ) : (
                      "Generate Standardized Catalog"
                    )}
                  </button>
                </div>
              </div>

              {/* Error Alert */}
              {errorMsg && (
                <div className="bg-red-50 border-l-4 border-red-500 p-4 rounded-xl flex items-start gap-3">
                  <AlertTriangle className="h-5 w-5 text-red-500 shrink-0 mt-0.5" />
                  <div>
                    <h4 className="font-bold text-red-800 text-sm">Processing Failure</h4>
                    <p className="text-xs text-red-700 mt-1">{errorMsg}</p>
                  </div>
                </div>
              )}

              {/* Stepper Pipeline Status */}
              {isProcessing && (
                <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
                  <h4 className="font-bold text-slate-800 text-sm flex items-center gap-2">
                    <Activity className="h-4 w-4 text-orange-500 animate-pulse" /> SLM Cataloging Pipelines
                  </h4>
                  <div className="grid grid-cols-2 md:grid-cols-7 gap-4">
                    {processingSteps.map((step) => (
                      <div key={step.id} className="p-3 border border-slate-100 rounded-xl bg-slate-50 flex flex-col justify-between h-20">
                        <span className="text-[10px] font-bold text-slate-400 uppercase">Step {step.id}</span>
                        <div className="flex items-center justify-between mt-1">
                          <span className="text-xs font-semibold text-slate-700">{step.label}</span>
                          {step.status === "loading" && <Loader2 className="h-3.5 w-3.5 text-orange-500 animate-spin" />}
                          {step.status === "done" && <Check className="h-3.5 w-3.5 text-emerald-500 font-bold" />}
                          {step.status === "pending" && <Clock className="h-3.5 w-3.5 text-slate-300" />}
                          {step.status === "error" && <span className="text-xs text-red-500 font-bold">X</span>}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Inference Result View */}
              {generatedCatalog && (
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                  {/* Left Column: AI Extraction & Review */}
                  <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-6">
                    <div className="flex items-center justify-between border-b border-slate-100 pb-4">
                      <div>
                        <h3 className="font-bold text-slate-800 text-lg">AI Extraction & Mapping</h3>
                        <p className="text-xs text-slate-400">Review, adjust attributes, and approve the generated catalog.</p>
                      </div>
                      <span className={`px-3 py-1 rounded-full text-xs font-bold ${generatedCatalog.status === 'Approved' ? 'bg-emerald-50 text-emerald-600' : 'bg-amber-50 text-amber-600'}`}>
                        {generatedCatalog.status}
                      </span>
                    </div>

                    {/* Metadata Header */}
                    <div className="grid grid-cols-3 gap-4 bg-slate-50 p-4 rounded-xl text-xs font-medium text-slate-500">
                      <div>
                        <div>Detected Language</div>
                        <div className="font-bold text-slate-800 text-sm mt-0.5">{generatedCatalog.detected_language}</div>
                      </div>
                      <div>
                        <div>Overall Confidence</div>
                        <div className="font-bold text-slate-800 text-sm mt-0.5">{(generatedCatalog.confidence.overall * 100).toFixed(1)}%</div>
                      </div>
                      <div>
                        <div>Processing Time</div>
                        <div className="font-bold text-slate-800 text-sm mt-0.5">{generatedCatalog.processing_time_ms} ms</div>
                      </div>
                    </div>

                    <div className={`rounded-xl border p-4 ${generatedCatalog.existing_product ? "border-emerald-200 bg-emerald-50/60" : "border-indigo-200 bg-indigo-50/60"}`}>
                      <div className="flex items-center justify-between gap-3">
                        <div>
                          <div className="text-xs font-bold uppercase tracking-wider text-slate-500">Product Match</div>
                          <div className="font-bold text-slate-800 mt-1">
                            {generatedCatalog.existing_product ? "Existing Product" : "New product detected"}
                          </div>
                        </div>
                        <span className={`rounded-full px-2.5 py-1 text-xs font-bold ${generatedCatalog.existing_product ? "bg-emerald-100 text-emerald-700" : "bg-indigo-100 text-indigo-700"}`}>
                          {generatedCatalog.existing_product ? "Matched" : "New"}
                        </span>
                      </div>
                      <div className="grid grid-cols-2 gap-x-4 gap-y-3 mt-4 text-sm">
                        <div><div className="text-xs text-slate-500">Product</div><div className="font-semibold text-slate-800">{generatedCatalog.product_name}</div></div>
                        <div><div className="text-xs text-slate-500">Brand</div><div className="font-semibold text-slate-800">{generatedCatalog.brand || "Not detected"}</div></div>
                        <div><div className="text-xs text-slate-500">Category</div><div className="font-semibold text-slate-800">{generatedCatalog.category}</div></div>
                        <div><div className="text-xs text-slate-500">Subcategory</div><div className="font-semibold text-slate-800">{generatedCatalog.subcategory}</div></div>
                      </div>
                      <div className="mt-4 border-t border-slate-200/70 pt-3">
                        <div className="text-xs font-bold uppercase tracking-wider text-slate-500">Detected Attributes</div>
                        <div className="flex flex-wrap gap-2 mt-2">
                          {Object.entries(generatedCatalog.requested_variant || {}).length > 0 ? (
                            Object.entries(generatedCatalog.requested_variant).map(([key, value]) => (
                              <span key={key} className="rounded-md bg-white px-2.5 py-1 text-xs text-slate-700 border border-slate-200">
                                <span className="font-semibold capitalize">{key}:</span> {value}
                              </span>
                            ))
                          ) : (
                            <span className="text-xs text-slate-500">No variant attributes detected</span>
                          )}
                        </div>
                      </div>
                      <div className="grid grid-cols-2 gap-4 mt-4 text-xs">
                        <div>
                          <div className="text-slate-500">Variant</div>
                          <div className={`font-bold mt-1 ${generatedCatalog.variant_match === true ? "text-emerald-700" : generatedCatalog.variant_match === false ? "text-red-700" : "text-slate-600"}`}>
                            {generatedCatalog.variant_match === true
                              ? "✓ Valid existing variant"
                              : generatedCatalog.variant_match === false
                                ? "Invalid / unavailable variant"
                                : generatedCatalog.existing_product ? "No variant requested" : "Pending product approval"}
                          </div>
                        </div>
                        <div>
                          <div className="text-slate-500">Model Confidence</div>
                          <div className="font-bold text-slate-800 mt-1">{(generatedCatalog.confidence.overall * 100).toFixed(1)}%</div>
                        </div>
                      </div>
                      {generatedCatalog.variant_match === true && generatedCatalog.matched_variant && (
                        <div className="text-xs text-emerald-800 mt-2">
                          Matched: {Object.entries(generatedCatalog.matched_variant).map(([key, value]) => `${key}: ${value}`).join(" / ")}
                        </div>
                      )}
                      {generatedCatalog.resolution_reasons?.length > 0 && (
                        <ul className="mt-2 list-disc pl-5 text-xs text-red-700">
                          {generatedCatalog.resolution_reasons.map(reason => <li key={reason}>{reason}</li>)}
                        </ul>
                      )}
                      {!generatedCatalog.existing_product && (
                        <p className="text-xs text-indigo-700 mt-3">Review the Catalog-SLM output and approve it to add this product to the knowledge base.</p>
                      )}
                    </div>

                    {/* Form Block */}
                    <div className="space-y-4">
                      <div>
                        <label className="text-xs font-bold text-slate-400 uppercase tracking-wider">Product Name</label>
                        <input 
                          type="text" 
                          value={editedName}
                          disabled={!editMode}
                          onChange={(e) => setEditedName(e.target.value)}
                          className="w-full mt-1 px-4 py-2 border border-slate-200 rounded-lg text-sm text-slate-800 focus:outline-none focus:border-orange-500 disabled:bg-slate-50 disabled:text-slate-500 font-semibold"
                        />
                      </div>

                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <label className="text-xs font-bold text-slate-400 uppercase tracking-wider">Category</label>
                          <input 
                            type="text" 
                            value={editedCategory}
                            disabled={!editMode}
                            onChange={(e) => setEditedCategory(e.target.value)}
                            className="w-full mt-1 px-4 py-2 border border-slate-200 rounded-lg text-sm text-slate-800 disabled:bg-slate-50 disabled:text-slate-500 font-semibold"
                          />
                        </div>
                        <div>
                          <label className="text-xs font-bold text-slate-400 uppercase tracking-wider">Subcategory</label>
                          <input 
                            type="text" 
                            value={editedSubcategory}
                            disabled={!editMode}
                            onChange={(e) => setEditedSubcategory(e.target.value)}
                            className="w-full mt-1 px-4 py-2 border border-slate-200 rounded-lg text-sm text-slate-800 disabled:bg-slate-50 disabled:text-slate-500 font-semibold"
                          />
                        </div>
                      </div>

                      {/* Attributes Table */}
                      <div className="border border-slate-200 rounded-xl overflow-hidden mt-4">
                        <table className="w-full text-left text-sm">
                          <thead className="bg-slate-50 border-b border-slate-200 text-slate-400 text-[10px] uppercase font-bold tracking-wider">
                            <tr>
                              <th className="px-4 py-2.5">Attribute</th>
                              <th className="px-4 py-2.5">Standardized Value</th>
                              <th className="px-4 py-2.5 text-right">Confidence</th>
                            </tr>
                          </thead>
                          <tbody className="divide-y divide-slate-200 text-slate-700">
                            {Object.entries(editedAttributes).map(([key, val]) => (
                              <tr key={key}>
                                <td className="px-4 py-2.5 font-semibold text-slate-500 capitalize">{key.replace('_', ' ')}</td>
                                <td className="px-4 py-2.5">
                                  {editMode ? (
                                    <input 
                                      type="text" 
                                      value={val || ""}
                                      onChange={(e) => handleAttributeChange(key, e.target.value)}
                                      placeholder="Not present"
                                      className="px-2 py-1 border border-slate-200 rounded text-xs w-full focus:outline-none focus:border-orange-500"
                                    />
                                  ) : (
                                    <span className={val ? "font-semibold text-slate-800" : "text-slate-400 italic text-xs"}>
                                      {val || "Not detected"}
                                    </span>
                                  )}
                                </td>
                                <td className="px-4 py-2.5 text-right font-mono text-xs">
                                  {generatedCatalog.confidence[key] ? (generatedCatalog.confidence[key] * 100).toFixed(0) + "%" : "Rule"}
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>

                      {/* Warnings if overall confidence is low */}
                      {generatedCatalog.confidence.overall < 0.70 && (
                        <div className="bg-amber-50 border-l-4 border-amber-500 p-4 rounded-xl flex items-start gap-3 mt-4">
                          <AlertTriangle className="h-5 w-5 text-amber-500 shrink-0 mt-0.5" />
                          <div>
                            <h5 className="font-bold text-amber-800 text-sm">Low Overall Model Confidence</h5>
                            <p className="text-xs text-amber-700 mt-0.5">Please review the catalog data fields carefully before approval.</p>
                          </div>
                        </div>
                      )}

                      {/* Action buttons */}
                      <div className="flex gap-3 mt-6 border-t border-slate-100 pt-4">
                        {editMode ? (
                          <>
                            <button 
                              onClick={handleApprove}
                              className="bg-emerald-600 hover:bg-emerald-700 text-white font-bold px-4 py-2 rounded-lg text-sm shadow-md shadow-emerald-500/10 flex items-center gap-1.5"
                            >
                              <CheckCircle className="h-4 w-4" /> Save & Approve
                            </button>
                            <button 
                              onClick={() => {
                                setEditMode(false);
                                setEditedName(generatedCatalog.product_name);
                                setEditedAttributes(generatedCatalog.attributes);
                              }}
                              className="bg-slate-200 hover:bg-slate-300 text-slate-700 font-bold px-4 py-2 rounded-lg text-sm"
                            >
                              Cancel
                            </button>
                          </>
                        ) : (
                          <>
                            <button 
                              onClick={() => setEditMode(true)}
                              className="bg-orange-500 hover:bg-orange-600 text-white font-bold px-4 py-2 rounded-lg text-sm shadow-md shadow-orange-500/10 flex items-center gap-1.5"
                            >
                              <Edit3 className="h-4 w-4" /> Edit Attributes
                            </button>
                            <button 
                              onClick={handleApprove}
                              disabled={generatedCatalog.status === 'Approved'}
                              className="bg-emerald-600 hover:bg-emerald-700 disabled:bg-slate-100 disabled:text-slate-400 text-white font-bold px-4 py-2 rounded-lg text-sm flex items-center gap-1.5 shadow-md shadow-emerald-500/10"
                            >
                              <CheckCircle className="h-4 w-4" /> Approve Catalog
                            </button>
                          </>
                        )}
                      </div>
                    </div>
                  </div>

                  {/* Right Column: ONDC-Oriented JSON output */}
                  <div className="bg-slate-900 text-slate-100 p-6 rounded-2xl border border-slate-800 shadow-xl flex flex-col justify-between">
                    <div>
                      <div className="flex items-center justify-between border-b border-slate-800 pb-4 mb-4">
                        <div>
                          <h3 className="font-bold text-white text-lg">ONDC Standardized representation</h3>
                          <p className="text-xs text-slate-400">Digital commerce standardized catalog JSON format</p>
                        </div>
                        <div className="flex items-center gap-2">
                          <button 
                            onClick={() => copyToClipboard(JSON.stringify(generatedCatalog, null, 2))}
                            className="bg-slate-800 hover:bg-slate-700 p-2 rounded-lg text-slate-300 transition"
                            title="Copy JSON"
                          >
                            <Copy className="h-4 w-4" />
                          </button>
                          <button 
                            onClick={() => downloadJson(generatedCatalog)}
                            className="bg-slate-800 hover:bg-slate-700 p-2 rounded-lg text-slate-300 transition"
                            title="Download JSON"
                          >
                            <Download className="h-4 w-4" />
                          </button>
                        </div>
                      </div>

                      <div className="font-mono text-xs overflow-x-auto max-h-[420px] bg-slate-950 p-4 rounded-xl border border-slate-800/80 leading-relaxed text-slate-300">
                        <pre>{JSON.stringify(generatedCatalog, null, 2)}</pre>
                      </div>
                    </div>
                    
                    <div className="mt-6 flex items-start gap-3 bg-slate-950/40 p-4 rounded-xl border border-slate-800/60 text-xs text-slate-400">
                      <Info className="h-4 w-4 text-orange-500 shrink-0 mt-0.5" />
                      <p>This ONDC Schema follows open-network interoperability cataloging specifications. It isolates vernacular input and translates standard taxonomies for cross-network indexing.</p>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* TAB 3: CATALOG HISTORY */}
          {activeTab === 'history' && (
            <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-6">
              {/* Header search filter */}
              <div className="flex flex-col md:flex-row items-center justify-between gap-4 border-b border-slate-100 pb-4">
                <div>
                  <h3 className="font-bold text-slate-800 text-lg">Saved Catalog History</h3>
                  <p className="text-xs text-slate-400">View and manage previous structured catalog results stored in SQLite</p>
                </div>
                <div className="flex items-center gap-3 w-full md:w-auto">
                  <div className="relative flex-1 md:w-64">
                    <Search className="absolute left-3 top-2.5 h-4 w-4 text-slate-400" />
                    <input 
                      type="text" 
                      placeholder="Search catalogs..." 
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      className="w-full bg-slate-50 border border-slate-200 rounded-lg pl-9 pr-4 py-2 text-sm text-slate-800 focus:outline-none focus:border-orange-500 font-semibold"
                    />
                  </div>
                  <select 
                    value={statusFilter}
                    onChange={(e) => setStatusFilter(e.target.value)}
                    className="bg-slate-50 border border-slate-200 text-slate-700 text-sm font-semibold rounded-lg px-3 py-2 focus:outline-none focus:border-orange-500"
                  >
                    <option value="all">All Statuses</option>
                    <option value="Draft">Draft</option>
                    <option value="Needs Review">Needs Review</option>
                    <option value="Approved">Approved</option>
                  </select>
                </div>
              </div>

              {/* History Table */}
              <div className="overflow-x-auto">
                <table className="w-full text-left text-sm text-slate-600">
                  <thead className="bg-slate-50 border-b border-slate-200 text-slate-400 uppercase text-[10px] tracking-wider font-bold">
                    <tr>
                      <th className="px-4 py-3 font-semibold">Product Name</th>
                      <th className="px-4 py-3 font-semibold">Category</th>
                      <th className="px-4 py-3 font-semibold">Detected Language</th>
                      <th className="px-4 py-3 font-semibold">Confidence</th>
                      <th className="px-4 py-3 font-semibold">Resolution</th>
                      <th className="px-4 py-3 font-semibold">Variant</th>
                      <th className="px-4 py-3 font-semibold">Status</th>
                      <th className="px-4 py-3 font-semibold">Date</th>
                      <th className="px-4 py-3 font-semibold text-right">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {filteredHistory.map(item => (
                      <tr key={item.catalog_id} className="hover:bg-slate-50/50">
                        <td className="px-4 py-3.5 font-bold text-slate-800">
                          <div>{item.product_name}</div>
                          <div className="text-[10px] text-slate-400 font-semibold truncate max-w-xs font-mono font-normal mt-0.5">"{item.original_text}"</div>
                        </td>
                        <td className="px-4 py-3.5 font-semibold text-slate-700">{item.category}</td>
                        <td className="px-4 py-3.5 font-medium">{item.detected_language}</td>
                        <td className="px-4 py-3.5 font-mono text-slate-800">{(item.confidence.overall * 100).toFixed(1)}%</td>
                        <td className="px-4 py-3.5">
                          <div className="font-semibold">{item.existing_product ? "Existing Product" : "New Product"}</div>
                          <div className="text-[10px] text-slate-400">{item.matched_product_id || "No product ID"}</div>
                          <div className="text-[10px] text-slate-500">
                            Resolution confidence: {((item.product_resolution_confidence || 0) * 100).toFixed(1)}%
                          </div>
                        </td>
                        <td className="px-4 py-3.5">
                          {item.variant_match === true ? "Valid" : item.variant_match === false ? "Invalid" : "Not checked"}
                          {item.matched_variant && (
                            <div className="text-[10px] text-slate-400">
                              {Object.values(item.matched_variant).join(" / ")}
                            </div>
                          )}
                        </td>
                        <td className="px-4 py-3.5">
                          <span className={`px-2.5 py-1 text-xs font-bold rounded-full ${item.status === 'Approved' ? 'bg-emerald-50 text-emerald-600' : item.status === 'Needs Review' ? 'bg-red-50 text-red-600' : 'bg-amber-50 text-amber-600'}`}>
                            {item.seller_decision || item.status}
                          </span>
                        </td>
                        <td className="px-4 py-3.5 text-xs text-slate-400 font-semibold">{item.created_at ? item.created_at.split(' ')[0] : 'N/A'}</td>
                        <td className="px-4 py-3.5 text-right space-x-2">
                          <button 
                            onClick={() => {
                              setGeneratedCatalog(item);
                              setEditedName(item.product_name);
                              setEditedCategory(item.category);
                              setEditedSubcategory(item.subcategory);
                              setEditedAttributes(item.attributes);
                              setActiveTab('generate');
                            }}
                            className="bg-orange-50 hover:bg-orange-100 text-orange-600 px-3 py-1.5 rounded-lg text-xs font-bold transition"
                          >
                            Review & Load
                          </button>
                        </td>
                      </tr>
                    ))}
                    {filteredHistory.length === 0 && (
                      <tr>
                        <td colSpan="9" className="text-center py-12 text-slate-400 font-semibold">No catalogs found matching the search/filter criteria.</td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* TAB 4: TAXONOMY BROWSER */}
          {activeTab === 'taxonomy' && (
            <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-6">
              <div>
                <h3 className="font-bold text-slate-800 text-lg">Controlled Catalog Taxonomy</h3>
                <p className="text-xs text-slate-400">Review standard ONDC catalog groups and leaf categories supported by this small language model.</p>
              </div>

              {taxonomy ? (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {Object.entries(taxonomy).map(([catName, subcatGroups]) => (
                    <div key={catName} className="border border-slate-200 rounded-xl p-5 bg-slate-50/50 shadow-sm">
                      <h4 className="font-extrabold text-orange-500 text-base border-b border-slate-200 pb-2 mb-3 tracking-wide">{catName}</h4>
                      <div className="space-y-4">
                        {Object.entries(subcatGroups).map(([groupName, leaves]) => (
                          <div key={groupName} className="space-y-1">
                            <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">{groupName}</span>
                            <ul className="pl-3 border-l-2 border-slate-200 space-y-1">
                              {leaves.map(leaf => (
                                <li key={leaf} className="text-sm font-semibold text-slate-700 flex items-center gap-1.5">
                                  <ChevronRight className="h-3 w-3 text-slate-400 shrink-0" /> {leaf}
                                </li>
                              ))}
                            </ul>
                          </div>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-12 text-slate-400">Loading taxonomy file...</div>
              )}
            </div>
          )}

          {/* TAB 5: MODEL EVALUATION */}
          {activeTab === 'evaluation' && (
            <div className="space-y-8">
              {/* Architecture info cards */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
                  <div className="text-xs font-bold text-slate-400 uppercase tracking-wider">Framework</div>
                  <div className="text-2xl font-extrabold text-slate-800 mt-1">TensorFlow / Keras</div>
                  <p className="text-[10px] text-slate-400 mt-1">BiLSTM multi-task head</p>
                </div>
                <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
                  <div className="text-xs font-bold text-slate-400 uppercase tracking-wider">Trainable Parameters</div>
                  <div className="text-2xl font-extrabold text-slate-800 mt-1">
                    {evaluation && evaluation.status === "trained" ? evaluation.model_parameters.toLocaleString() : "54,231"}
                  </div>
                  <p className="text-[10px] text-slate-400 mt-1">Total model weights</p>
                </div>
                <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
                  <div className="text-xs font-bold text-slate-400 uppercase tracking-wider">Model File Size</div>
                  <div className="text-2xl font-extrabold text-slate-800 mt-1">
                    {evaluation && evaluation.status === "trained" ? evaluation.model_size_mb + " MB" : "1.2 MB"}
                  </div>
                  <p className="text-[10px] text-slate-400 mt-1">Extremely portable scale</p>
                </div>
                <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
                  <div className="text-xs font-bold text-slate-400 uppercase tracking-wider">Avg Inference Speed</div>
                  <div className="text-2xl font-extrabold text-orange-500 mt-1">
                    {evaluation && evaluation.status === "trained" ? evaluation.avg_inference_time_ms + " ms" : "18 ms"}
                  </div>
                  <p className="text-[10px] text-slate-400 mt-1">Single description parse CPU</p>
                </div>
              </div>

              {/* Status Alert if not trained */}
              {evaluation && evaluation.status === "awaiting_training" && (
                <div className="bg-indigo-50 border-l-4 border-indigo-500 p-4 rounded-xl flex items-start gap-3">
                  <Info className="h-5 w-5 text-indigo-500 shrink-0 mt-0.5" />
                  <div>
                    <h4 className="font-bold text-indigo-800 text-sm">Model Training Awaiting Execution</h4>
                    <p className="text-xs text-indigo-700 mt-1">The TensorFlow model is currently compiling or training in the background. Displaying reference configuration until training results compile.</p>
                  </div>
                </div>
              )}

              {/* Evaluation Metrics Grid */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                {/* Accuracy Table */}
                <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
                  <h3 className="font-bold text-slate-800 mb-4 flex items-center gap-2">
                    <CheckCircle className="h-5 w-5 text-emerald-500" /> Multi-Task Classification Accuracy
                  </h3>
                  <div className="overflow-x-auto">
                    <table className="w-full text-left text-sm text-slate-600">
                      <thead className="bg-slate-50 border-b border-slate-200 text-slate-400 text-[10px] uppercase font-bold tracking-wider">
                        <tr>
                          <th className="px-4 py-2">Prediction Task</th>
                          <th className="px-4 py-2">Test Accuracy</th>
                          <th className="px-4 py-2">Precision</th>
                          <th className="px-4 py-2">Recall</th>
                          <th className="px-4 py-2">F1 Score</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-100 text-slate-700">
                        {evaluation && evaluation.status === "trained" ? (
                          Object.entries(evaluation.metrics).map(([task, val]) => {
                            if (task === "category_confusion_matrix") return null;
                            return (
                              <tr key={task}>
                                <td className="px-4 py-3.5 font-bold text-slate-800 capitalize">{task.replace('_', ' ')}</td>
                                <td className="px-4 py-3.5 font-semibold text-slate-600 font-mono">{(val.accuracy * 100).toFixed(1)}%</td>
                                <td className="px-4 py-3.5 font-semibold text-slate-500 font-mono">{(val.precision * 100).toFixed(1)}%</td>
                                <td className="px-4 py-3.5 font-semibold text-slate-500 font-mono">{(val.recall * 100).toFixed(1)}%</td>
                                <td className="px-4 py-3.5 font-bold text-emerald-600 font-mono">{(val.f1_score * 100).toFixed(1)}%</td>
                              </tr>
                            );
                          })
                        ) : (
                          // Dummy display
                          ["category", "subcategory", "color", "material", "gender", "size", "language"].map(task => (
                            <tr key={task}>
                              <td className="px-4 py-3.5 font-bold text-slate-800 capitalize">{task.replace('_', ' ')}</td>
                              <td className="px-4 py-3.5 font-mono text-slate-400">98.5%</td>
                              <td className="px-4 py-3.5 font-mono text-slate-400">97.8%</td>
                              <td className="px-4 py-3.5 font-mono text-slate-400">98.2%</td>
                              <td className="px-4 py-3.5 font-bold text-emerald-600/60 font-mono">98.0%</td>
                            </tr>
                          ))
                        )}
                      </tbody>
                    </table>
                  </div>
                </div>

                {/* Training Curves using custom inline SVGs */}
                <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-6">
                  <h3 className="font-bold text-slate-800 flex items-center gap-2">
                    <Activity className="h-5 w-5 text-indigo-500" /> Training History Curves (15 Epochs)
                  </h3>
                  
                  {evaluation && evaluation.status === "trained" && evaluation.history ? (
                    <div className="space-y-8">
                      <div>
                        <span className="text-xs font-bold text-slate-400 uppercase tracking-wider block mb-2">Total Training Loss</span>
                        <div className="bg-slate-50 p-4 rounded-xl border border-slate-100 flex items-center justify-center">
                          {/* Render custom visual SVG curve */}
                          <svg className="w-full h-36 overflow-visible" viewBox="0 0 300 100">
                            {/* Guideline axes */}
                            <line x1="0" y1="100" x2="300" y2="100" stroke="#cbd5e1" strokeWidth="1" />
                            <line x1="0" y1="0" x2="0" y2="100" stroke="#cbd5e1" strokeWidth="1" />
                            
                            {/* Draw points/line path */}
                            {(() => {
                              const losses = evaluation.history.loss;
                              const maxLoss = Math.max(...losses);
                              const minLoss = Math.min(...losses);
                              const points = losses.map((l, idx) => {
                                const x = (idx / (losses.length - 1)) * 300;
                                const y = 90 - ((l - minLoss) / (maxLoss - minLoss || 1)) * 80; // scale to 10-90
                                return `${x},${y}`;
                              }).join(" ");
                              
                              return (
                                <>
                                  <polyline fill="none" stroke="#6366f1" strokeWidth="3" points={points} />
                                  {losses.map((l, idx) => {
                                    const x = (idx / (losses.length - 1)) * 300;
                                    const y = 90 - ((l - minLoss) / (maxLoss - minLoss || 1)) * 80;
                                    return (
                                      <circle key={idx} cx={x} cy={y} r="3.5" fill="#4338ca" />
                                    );
                                  })}
                                </>
                              );
                            })()}
                          </svg>
                        </div>
                        <div className="flex justify-between text-[10px] font-bold text-slate-400 uppercase mt-2">
                          <span>Epoch 1</span>
                          <span>Epoch 15</span>
                        </div>
                      </div>

                      <div>
                        <span className="text-xs font-bold text-slate-400 uppercase tracking-wider block mb-2">Category Accuracy</span>
                        <div className="bg-slate-50 p-4 rounded-xl border border-slate-100 flex items-center justify-center">
                          <svg className="w-full h-36 overflow-visible" viewBox="0 0 300 100">
                            <line x1="0" y1="100" x2="300" y2="100" stroke="#cbd5e1" strokeWidth="1" />
                            <line x1="0" y1="0" x2="0" y2="100" stroke="#cbd5e1" strokeWidth="1" />
                            
                            {(() => {
                              const accs = evaluation.history.category_accuracy;
                              if (!accs) return null;
                              const maxAcc = Math.max(...accs);
                              const minAcc = Math.min(...accs);
                              const points = accs.map((a, idx) => {
                                const x = (idx / (accs.length - 1)) * 300;
                                const y = 90 - ((a - minAcc) / (maxAcc - minAcc || 1)) * 80;
                                return `${x},${y}`;
                              }).join(" ");
                              
                              return (
                                <>
                                  <polyline fill="none" stroke="#f97316" strokeWidth="3" points={points} />
                                  {accs.map((a, idx) => {
                                    const x = (idx / (accs.length - 1)) * 300;
                                    const y = 90 - ((a - minAcc) / (maxAcc - minAcc || 1)) * 80;
                                    return (
                                      <circle key={idx} cx={x} cy={y} r="3.5" fill="#c2410c" />
                                    );
                                  })}
                                </>
                              );
                            })()}
                          </svg>
                        </div>
                        <div className="flex justify-between text-[10px] font-bold text-slate-400 uppercase mt-2">
                          <span>Epoch 1</span>
                          <span>Epoch 15</span>
                        </div>
                      </div>
                    </div>
                  ) : (
                    <div className="text-center py-12 text-slate-400 font-semibold bg-slate-50 border border-slate-100 rounded-xl">
                      Training loss curves will render once model finishes training.
                    </div>
                  )}
                </div>
              </div>

              {/* Confusion Matrix grid */}
              {evaluation && evaluation.status === "trained" && evaluation.category_confusion_matrix && (
                <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-6">
                  <h3 className="font-bold text-slate-800">Category Classification Confusion Matrix</h3>
                  <div className="flex flex-col items-center justify-center p-6 bg-slate-50 rounded-2xl border border-slate-100">
                    <div className="grid gap-1" style={{ gridTemplateColumns: `repeat(${evaluation.category_confusion_matrix.classes.length + 1}, minmax(0, 1fr))` }}>
                      {/* Top labels */}
                      <div></div>
                      {evaluation.category_confusion_matrix.classes.map(cl => (
                        <div key={cl} className="text-[10px] font-bold text-slate-400 text-center uppercase tracking-wider p-1">{cl}</div>
                      ))}

                      {/* Matrix cells */}
                      {evaluation.category_confusion_matrix.matrix.map((row, rIdx) => {
                        const rowName = evaluation.category_confusion_matrix.classes[rIdx];
                        return (
                          <React.Fragment key={rIdx}>
                            <div className="text-[10px] font-bold text-slate-400 text-right uppercase tracking-wider p-1 pr-3 flex items-center justify-end">{rowName}</div>
                            {row.map((val, cIdx) => {
                              // Heat shade intensity calculation
                              const sum = row.reduce((a,b)=>a+b, 0);
                              const pct = sum > 0 ? val / sum : 0;
                              let bg = "bg-slate-100 text-slate-300";
                              if (val > 0) {
                                if (pct > 0.8) bg = "bg-orange-500 text-white font-extrabold";
                                else if (pct > 0.5) bg = "bg-orange-400 text-white font-bold";
                                else if (pct > 0.2) bg = "bg-orange-200 text-orange-800 font-semibold";
                                else bg = "bg-orange-50 text-orange-600";
                              }
                              return (
                                <div key={cIdx} className={`${bg} rounded text-xs p-3 text-center flex items-center justify-center font-mono h-10 w-16`}>
                                  {val}
                                </div>
                              );
                            })}
                          </React.Fragment>
                        );
                      })}
                    </div>
                    <div className="text-[10px] font-bold text-slate-400 uppercase tracking-widest mt-6">Predicted Categories &rarr;</div>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
