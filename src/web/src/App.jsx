import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { 
  Brain, 
  Cpu, 
  Send, 
  Settings, 
  Zap, 
  CheckCircle2, 
  XCircle,
  RefreshCcw,
  Clock,
  ChevronRight,
  MessageSquare,
  AlertCircle
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const API_BASE = window.location.origin === "http://localhost:5173" 
  ? "http://localhost:8000" 
  : window.location.origin;

function App() {
  const [problem, setProblem] = useState("");
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [iterations, setIterations] = useState(3);
  const [useParamPlus, setUseParamPlus] = useState(true);
  const [stats, setStats] = useState({ time: 0, steps: 0 });
  const scrollRef = useRef(null);

  const examples = [
    {
      title: "Code Optimization",
      text: "Write a Python function to check if a number is prime, but ensure it uses the O(sqrt(n)) optimization."
    },
    {
      title: "Logic Puzzle",
      text: "A man has to get a fox, a chicken, and a sack of corn across a river. He has a boat, but it can only carry him and one other thing. If the fox and chicken are left alone, the fox will eat the chicken. If the chicken and corn are left alone, the chicken will eat the corn. How does he get them across?"
    }
  ];

  useEffect(() => {
    if (results) {
      scrollRef.current?.scrollIntoView({ behavior: "smooth" });
    }
  }, [results]);

  const handleSolve = async () => {
    if (!problem.trim()) return;
    setLoading(true);
    setResults(null);
    const startTime = Date.now();

    try {
      const response = await axios.post(`${API_BASE}/solve`, {
        problem,
        max_iterations: iterations,
        use_param_plus: useParamPlus
      });
      
      setResults(response.data);
      setStats({
        time: ((Date.now() - startTime) / 1000).toFixed(1),
        steps: response.data.iterations || iterations
      });
    } catch (error) {
      console.error("Solver Error:", error);
      // No alert, just set error state if needed
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-container">
      {/* Sidebar - Configuration */}
      <aside className="sidebar">
        <div className="flex items-center gap-3 mb-4">
          <div className="p-2 bg-gradient-to-br from-[#00f2ff] to-[#7000ff] rounded-xl">
            <Brain className="text-white" size={24} />
          </div>
          <div>
            <h1 className="text-xl font-bold tracking-tight">ParamMem</h1>
            <p className="text-[10px] text-muted-foreground uppercase font-bold tracking-widest opacity-50">v1.0 Dashboard</p>
          </div>
        </div>

        <nav className="flex-grow space-y-8">
          <div className="space-y-4">
            <div className="section-header">
              <Settings size={14} />
              <h2>Agent Settings</h2>
            </div>
            
            <div className="input-group">
              <label className="input-label">Iteration Depth</label>
              <div className="flex items-center gap-4 px-1">
                <input 
                  type="range" 
                  min="1" 
                  max="5" 
                  value={iterations} 
                  onChange={(e) => setIterations(parseInt(e.target.value))}
                  className="flex-grow accent-[#00f2ff]"
                />
                <span className="font-bold text-[#00f2ff] min-w-[12px]">{iterations}</span>
              </div>
            </div>

            <div className="flex items-center justify-between p-4 glass-card bg-white/5 rounded-xl border border-white/5 cursor-pointer hover:bg-white/10 transition-colors" onClick={() => setUseParamPlus(!useParamPlus)}>
              <div className="flex items-center gap-3">
                <Zap size={16} className={useParamPlus ? "text-yellow-400" : "text-muted"} />
                <span className="text-sm font-medium">Cross-Sample Memory</span>
              </div>
              <div className={`w-10 h-5 rounded-full relative transition-colors ${useParamPlus ? 'bg-[#00f2ff]' : 'bg-gray-700'}`}>
                <div className={`absolute top-1 w-3 h-3 bg-white rounded-full transition-all ${useParamPlus ? 'left-6' : 'left-1'}`} />
              </div>
            </div>
          </div>

          <div className="space-y-4">
            <div className="section-header">
              <MessageSquare size={14} />
              <h2>Task Input</h2>
            </div>
            <textarea 
              rows="8"
              value={problem}
              onChange={(e) => setProblem(e.target.value)}
              placeholder="Enter the problem description or reasoning task here..."
              className="resize-none text-sm leading-relaxed"
            ></textarea>

            <div className="space-y-2">
              <label className="input-label">Quick Start Examples</label>
              <div className="grid grid-cols-1 gap-2">
                {examples.map((ex, i) => (
                  <button 
                    key={i}
                    onClick={() => setProblem(ex.text)}
                    className="text-[10px] text-left px-3 py-2 bg-white/5 border border-white/5 rounded-lg hover:bg-white/10 transition-all tech-text uppercase tracking-wider text-muted hover:text-white"
                  >
                    {ex.title}
                  </button>
                ))}
              </div>
            </div>
            
            <button 
              onClick={handleSolve}
              disabled={loading || !problem.trim()}
              className="primary-btn mt-2"
            >
              {loading ? <RefreshCcw size={18} className="animate-spin" /> : <Send size={18} />}
              {loading ? "Analyzing..." : "Initiate Solve"}
            </button>
          </div>
        </nav>

        {/* Engine Status */}
        <div className="mt-auto pt-6 border-t border-white/5">
          <div className="flex items-center justify-between text-[10px] uppercase font-bold tracking-widest text-muted">
            <span>Engine Status</span>
            <span className="flex items-center gap-1 text-green-500">
              <div className="w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse"></div>
              Connected
            </span>
          </div>
        </div>
      </aside>

      {/* Main Content - Results */}
      <main className="main-content">
        <div className="flex justify-between items-end mb-8">
          <div>
            <h2 className="text-2xl font-bold mb-1">Reasoning Environment</h2>
            <p className="text-sm text-muted">Monitor the agent's iterative self-reflection process in real-time.</p>
          </div>
          
          <div className="stat-grid min-w-[300px]">
            <div className="glass-card stat-card">
              <Clock size={16} className="text-[#00f2ff]" />
              <span className="stat-value">{stats.time}s</span>
              <span className="stat-label">Time</span>
            </div>
            <div className="glass-card stat-card">
              <RefreshCcw size={16} className="text-[#7000ff]" />
              <span className="stat-value">{stats.steps}</span>
              <span className="stat-label">Steps</span>
            </div>
          </div>
        </div>

        <section className="min-h-[500px]">
          {!results && !loading && (
            <div className="flex flex-col items-center justify-center py-20 text-center space-y-4 opacity-40">
              <div className="p-8 rounded-full bg-white/5 border border-dashed border-white/20">
                <Cpu size={48} />
              </div>
              <div>
                <h3 className="text-lg font-semibold">Ready for Computation</h3>
                <p className="text-sm max-w-xs mx-auto">Configure the agent parameters on the left and initiate a solve request to begin the process.</p>
              </div>
            </div>
          )}

          {loading && (
            <div className="flex flex-col items-center justify-center py-24 space-y-6">
              <div className="relative">
                <div className="w-20 h-20 border-4 border-[#00f2ff]/20 rounded-full"></div>
                <div className="absolute inset-0 border-4 border-t-[#00f2ff] rounded-full animate-spin"></div>
                <Brain className="absolute inset-0 m-auto text-[#00f2ff] animate-pulse" size={24} />
              </div>
              <div className="text-center">
                <h3 className="text-lg font-bold tracking-tight text-[#00f2ff]">Thinking...</h3>
                <p className="text-xs tech-text text-muted uppercase tracking-widest mt-2">Processing Parametric Memory Weights</p>
              </div>
            </div>
          )}

          <AnimatePresence>
            {results?.history?.map((step, idx) => (
              <motion.div 
                key={idx}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: idx * 0.1 }}
                className="trace-node"
              >
                <div className="node-icon-wrapper shadow-lg">
                  <ChevronRight size={20} />
                </div>
                <div className="node-content space-y-4">
                  <div className="flex items-center gap-3">
                    <span className="text-[10px] font-bold bg-white/5 px-2 py-1 rounded text-muted uppercase tracking-widest">Iteration {idx + 1}</span>
                    <div className="h-[1px] flex-grow bg-white/5"></div>
                  </div>
                  
                  <div className="glass-card">
                    <div className="space-y-4">
                      <div>
                        <h4 className="flex items-center gap-2 text-[10px] uppercase font-bold text-muted mb-2 tracking-wider">
                          <Cpu size={12} /> Proposed Solution
                        </h4>
                        <pre className="code-block">{step.attempt}</pre>
                      </div>
                      
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div className="p-4 bg-red-500/5 border border-red-500/10 rounded-xl">
                          <h4 className="flex items-center gap-2 text-[10px] uppercase font-bold text-red-400 mb-2 tracking-wider">
                            <AlertCircle size={12} /> Error Feedback
                          </h4>
                          <p className="text-xs text-red-200/70 leading-relaxed italic">{step.error}</p>
                        </div>
                        
                        <div className="p-4 bg-[#7000ff]/5 border border-[#7000ff]/10 rounded-xl">
                          <h4 className="flex items-center gap-2 text-[10px] uppercase font-bold text-[#7000ff] mb-2 tracking-wider">
                            <Zap size={12} /> Reflective Correction
                          </h4>
                          <p className="text-xs text-purple-100/70 leading-relaxed">{step.reflection}</p>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </motion.div>
            ))}

            {results && (
              <motion.div 
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                className="mt-12 pt-8 border-t border-white/5"
                ref={scrollRef}
              >
                <div className="flex items-center gap-3 mb-6">
                  <div className={`p-2 rounded-lg ${results.success ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'}`}>
                    {results.success ? <CheckCircle2 size={24} /> : <XCircle size={24} />}
                  </div>
                  <div>
                    <h3 className="text-xl font-bold">{results.success ? 'Task Successfully Optimized' : 'Iteration Limit Reached'}</h3>
                    <p className="text-sm text-muted">Final output generated by the parametric encoding module.</p>
                  </div>
                </div>
                
                <div className="glass-card border-2 border-[#00f2ff]/20 shadow-[0_0_50px_rgba(0,242,255,0.05)]">
                  <pre className="code-block text-base leading-relaxed text-[#00f2ff]/90 min-h-[200px]">
                    {results.solution}
                  </pre>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </section>
      </main>
    </div>
  );
}

export default App;
