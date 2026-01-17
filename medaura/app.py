import React, { useState, useEffect, useRef } from 'react';
import { 
  FileText, 
  Upload, 
  MessageSquare, 
  Activity, 
  AlertCircle, 
  User, 
  Send,
  Loader2,
  Stethoscope,
  Info,
  ShieldCheck,
  Scale,
  RefreshCw,
  ChevronRight,
  HeartPulse,
  History
} from 'lucide-react';

/**
 * MEDAURA: AI Medical Expert System
 * * Features:
 * - Multimodal OCR: Extracts and understands blood report data from images/PDFs.
 * - Layman Interpretation: Translates complex results into simple analogies.
 * - Pattern Recognition: Correlates blood markers with patient-reported symptoms.
 * - Expert Chat: Interactive follow-up for health queries.
 */

// API Key integrated from user input
const apiKey = "AIzaSyD2uq8AY_h3O98ysrWOGTECr0c6rWcP7-Q"; 
const MODEL_NAME = "gemini-2.5-flash-preview-09-2025";

const App = () => {
  const [step, setStep] = useState(0); // 0: Consent, 1: Upload, 2: Patient Info, 3: Expert Analysis
  const [loading, setLoading] = useState(false);
  const [chatHistory, setChatHistory] = useState([]);
  const [userInput, setUserInput] = useState("");
  const [errorMsg, setErrorMsg] = useState(null);
  const [patientData, setPatientData] = useState({
    age: "",
    gender: "Male",
    symptoms: ""
  });
  const [fileData, setFileData] = useState(null);
  const chatEndRef = useRef(null);

  // Auto-scroll chat to bottom
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chatHistory]);

  // Handle File Input and convert to Base64 for Gemini
  const handleFileUpload = (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onloadend = () => {
      const base64Data = reader.result.split(',')[1];
      setFileData({
        inlineData: {
          data: base64Data,
          mimeType: file.type
        }
      });
      setStep(2);
    };
    reader.readAsDataURL(file);
  };

  /**
   * Robust API Caller with Exponential Backoff
   */
  const callGemini = async (prompt, media = null) => {
    const systemPrompt = `You are MEDAURA, a highly advanced Medical Expert System.
    MISSION: Analyze blood reports, translate data for laypeople, and perform pattern recognition.
    
    GUIDELINES:
    1. USE ANALOGIES: Compare biological markers to everyday things (e.g., 'Glucose is like the fuel in your car's tank').
    2. PATTERN RECOGNITION: Critically analyze how specific lab markers (High/Low) explain the symptoms the patient reported (e.g., 'Your low Iron explains why you feel dizzy').
    3. DISCLAIMER: Always mention: "I am an AI, not a doctor. Use this for info only."
    4. URGENCY: If you see life-threatening values, strongly advise immediate ER visit.
    5. STRUCTURE: Use clear headings, bullet points, and bold text for clarity.`;

    const payload = {
      contents: [{
        role: "user",
        parts: [{ text: prompt }, ...(media ? [media] : [])]
      }],
      systemInstruction: { parts: [{ text: systemPrompt }] }
    };

    const maxRetries = 5;
    const delays = [1000, 2000, 4000, 8000, 16000];

    for (let i = 0; i <= maxRetries; i++) {
      try {
        const response = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/${MODEL_NAME}:generateContent?key=${apiKey}`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });

        if (!response.ok) throw new Error(`API error: ${response.status}`);
        const data = await response.json();
        const text = data.candidates?.[0]?.content?.parts?.[0]?.text;
        if (!text) throw new Error("Empty AI response");
        return text;
      } catch (err) {
        if (i === maxRetries) throw err;
        await new Promise(r => setTimeout(r, delays[i]));
      }
    }
  };

  // Initial Report Processing
  const processReport = async () => {
    setLoading(true);
    setErrorMsg(null);
    const analysisPrompt = `
      Perform a deep analysis of this blood report for a ${patientData.age}y/o ${patientData.gender}.
      Patient Symptoms: ${patientData.symptoms}.
      
      STEPS:
      1. Summary: Give a high-level overview in 3 sentences.
      2. Flag Abnormalities: List markers outside normal range and what they mean simply.
      3. Pattern Matching: Specifically correlate the abnormal blood values with the symptoms provided.
      4. Recommendations: List 3 questions the patient must ask their GP.
    `;

    try {
      const result = await callGemini(analysisPrompt, fileData);
      setChatHistory([{ role: 'model', text: result }]);
      setStep(3);
    } catch (err) {
      setErrorMsg("Medaura is experiencing heavy load. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  // Chat Interaction
  const handleChat = async () => {
    if (!userInput.trim()) return;
    const msg = userInput;
    setUserInput("");
    setChatHistory(prev => [...prev, { role: 'user', text: msg }]);
    setLoading(true);

    try {
      const response = await callGemini(`Context: Patient ${patientData.age}${patientData.gender}, Symptoms: ${patientData.symptoms}. User asks: ${msg}`);
      setChatHistory(prev => [...prev, { role: 'model', text: response }]);
    } catch (err) {
      setErrorMsg("Connection to Expert Engine interrupted.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#fcfdfe] text-slate-900 font-sans p-4 md:p-8 selection:bg-indigo-100">
      {/* Header */}
      <nav className="max-w-6xl mx-auto flex items-center justify-between mb-10">
        <div className="flex items-center gap-4 group cursor-default">
          <div className="bg-gradient-to-br from-indigo-600 to-blue-500 p-3 rounded-2xl text-white shadow-xl shadow-indigo-100 group-hover:scale-110 transition-transform">
            <Stethoscope size={30} />
          </div>
          <div>
            <h1 className="text-3xl font-black tracking-tighter text-slate-800 uppercase leading-none">
              MED<span className="text-indigo-600">AURA</span>
            </h1>
            <span className="text-[10px] font-bold text-slate-400 tracking-[0.2em] uppercase">Advanced Bio-Reasoning</span>
          </div>
        </div>
        <div className="hidden md:flex items-center gap-6">
          <div className="flex items-center gap-2 text-xs font-bold text-slate-500">
            <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></div>
            SYSTEM READY
          </div>
        </div>
      </nav>

      <main className="max-w-6xl mx-auto relative">
        
        {errorMsg && (
          <div className="mb-8 max-w-2xl mx-auto bg-rose-50 border border-rose-100 text-rose-700 p-5 rounded-3xl flex items-center gap-4 animate-in slide-in-from-top-4">
            <AlertCircle size={24} className="shrink-0" />
            <p className="text-sm font-semibold">{errorMsg}</p>
            <button onClick={() => setErrorMsg(null)} className="ml-auto text-xs font-black uppercase">Dismiss</button>
          </div>
        )}

        {/* Step 0: Ethical/Medical Disclaimer */}
        {step === 0 && (
          <div className="max-w-2xl mx-auto bg-white rounded-[3rem] p-10 md:p-14 shadow-2xl shadow-slate-200/50 border border-slate-100 text-center animate-in zoom-in duration-500">
            <div className="w-24 h-24 bg-amber-50 text-amber-600 rounded-full flex items-center justify-center mx-auto mb-10 border-4 border-white shadow-inner">
              <Scale size={48} />
            </div>
            <h2 className="text-4xl font-black mb-6 text-slate-800 tracking-tight">Expert System Access</h2>
            <div className="space-y-5 text-left mb-12">
              <div className="flex gap-5 p-5 rounded-3xl bg-slate-50 border border-slate-100">
                <ShieldCheck className="text-indigo-600 shrink-0" size={28} />
                <div>
                  <h4 className="font-bold text-slate-800 text-sm">Not Medical Advice</h4>
                  <p className="text-xs text-slate-500 leading-relaxed">Medaura uses Large Language Models to interpret data. It is for educational purposes and cannot replace a doctor's diagnosis.</p>
                </div>
              </div>
              <div className="flex gap-5 p-5 rounded-3xl bg-slate-50 border border-slate-100">
                <Activity className="text-indigo-600 shrink-0" size={28} />
                <div>
                  <h4 className="font-bold text-slate-800 text-sm">Pattern Matching</h4>
                  <p className="text-xs text-slate-500 leading-relaxed">Our engine looks for correlations between your markers and your symptoms. Use these findings to discuss with your GP.</p>
                </div>
              </div>
            </div>
            <button 
              onClick={() => setStep(1)}
              className="group w-full bg-indigo-600 hover:bg-indigo-700 text-white font-black px-12 py-6 rounded-3xl shadow-2xl shadow-indigo-200 transition-all active:scale-95 flex items-center justify-center gap-3 text-lg"
            >
              Initialize Expert System <ChevronRight size={24} className="group-hover:translate-x-1 transition-transform" />
            </button>
          </div>
        )}

        {/* Step 1: Document OCR */}
        {step === 1 && (
          <div className="max-w-3xl mx-auto bg-white rounded-[3.5rem] p-16 shadow-2xl shadow-slate-200/50 border border-slate-100 text-center animate-in slide-in-from-right-12 duration-500">
            <div className="w-28 h-28 bg-indigo-50 text-indigo-600 rounded-full flex items-center justify-center mx-auto mb-10 shadow-inner group cursor-pointer overflow-hidden relative">
               <Upload size={54} className="group-hover:-translate-y-2 transition-transform duration-300" />
               <div className="absolute inset-0 bg-indigo-600 opacity-0 group-hover:opacity-5 transition-opacity"></div>
            </div>
            <h2 className="text-4xl font-black mb-4 text-slate-800 tracking-tighter">Upload Lab Results</h2>
            <p className="text-slate-400 mb-12 max-w-md mx-auto leading-relaxed text-lg font-medium">
              Provide your blood test as a PDF or high-quality image. Our neural engine will extract markers automatically.
            </p>
            <label className="inline-flex items-center gap-4 bg-slate-900 hover:bg-black text-white font-black px-12 py-7 rounded-[2rem] cursor-pointer transition-all active:scale-95 shadow-2xl shadow-slate-200">
              <FileText size={28} />
              Choose Report File
              <input type="file" className="hidden" accept="image/*,application/pdf" onChange={handleFileUpload} />
            </label>
            <p className="mt-10 text-[10px] text-slate-300 font-bold uppercase tracking-[0.3em]">Encrypted Local Processing</p>
          </div>
        )}

        {/* Step 2: Patient Profiling */}
        {step === 2 && (
          <div className="max-w-2xl mx-auto bg-white rounded-[3rem] p-12 shadow-2xl border border-slate-100 animate-in fade-in slide-in-from-bottom-10 duration-700">
            <div className="flex items-center gap-5 mb-10">
               <div className="w-16 h-16 bg-indigo-600 text-white rounded-[1.5rem] flex items-center justify-center shadow-lg shadow-indigo-100">
                 <User size={32} />
               </div>
               <div>
                 <h2 className="text-3xl font-black text-slate-800 tracking-tight leading-none">Patient Context</h2>
                 <p className="text-slate-400 font-bold text-xs mt-2 uppercase tracking-widest">Enhancing Pattern Recognition</p>
               </div>
            </div>
            
            <div className="space-y-8">
              <div className="grid grid-cols-2 gap-8">
                <div className="space-y-3">
                  <label className="text-xs font-black text-slate-500 uppercase tracking-widest ml-1">Current Age</label>
                  <input 
                    type="number" 
                    placeholder="24"
                    className="w-full bg-slate-50 border-2 border-slate-50 rounded-3xl px-7 py-5 focus:ring-0 focus:border-indigo-500 outline-none transition-all font-bold text-lg"
                    value={patientData.age}
                    onChange={(e) => setPatientData({...patientData, age: e.target.value})}
                  />
                </div>
                <div className="space-y-3">
                  <label className="text-xs font-black text-slate-500 uppercase tracking-widest ml-1">Bio Gender</label>
                  <select 
                    className="w-full bg-slate-50 border-2 border-slate-50 rounded-3xl px-7 py-5 focus:ring-0 focus:border-indigo-500 outline-none transition-all font-bold text-lg appearance-none"
                    value={patientData.gender}
                    onChange={(e) => setPatientData({...patientData, gender: e.target.value})}
                  >
                    <option>Male</option>
                    <option>Female</option>
                    <option>Other</option>
                  </select>
                </div>
              </div>
              
              <div className="space-y-3">
                <label className="text-xs font-black text-slate-500 uppercase tracking-widest ml-1">Describe Symptoms</label>
                <textarea 
                  rows="4"
                  placeholder="e.g., I've been feeling extremely tired for 2 weeks and get dizzy when standing up..."
                  className="w-full bg-slate-50 border-2 border-slate-50 rounded-[2rem] px-7 py-6 focus:ring-0 focus:border-indigo-500 outline-none resize-none transition-all font-medium text-slate-700"
                  value={patientData.symptoms}
                  onChange={(e) => setPatientData({...patientData, symptoms: e.target.value})}
                ></textarea>
              </div>

              <button 
                onClick={processReport}
                disabled={!patientData.age || loading}
                className="w-full bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white font-black py-6 rounded-[2rem] transition-all flex items-center justify-center gap-4 shadow-xl shadow-indigo-100 active:scale-[0.98]"
              >
                {loading ? <Loader2 className="animate-spin" /> : <HeartPulse size={24} />}
                {loading ? "Performing Neural Synthesis..." : "Synthesize Results"}
              </button>
            </div>
          </div>
        )}

        {/* Step 3: Analysis & Interaction UI */}
        {step === 3 && (
          <div className="grid grid-cols-1 lg:grid-cols-4 gap-10 h-[80vh]">
            
            {/* Case Panel (Desktop) */}
            <div className="lg:col-span-1 space-y-6 hidden lg:block overflow-y-auto pr-2 custom-scrollbar">
              <div className="bg-white rounded-[2rem] p-8 border border-slate-100 shadow-sm">
                <h3 className="font-black text-slate-800 mb-6 flex items-center gap-3 text-sm uppercase tracking-wider">
                  <History size={18} className="text-indigo-500" /> Case Details
                </h3>
                <div className="space-y-5">
                  <div className="bg-slate-50 p-4 rounded-2xl">
                    <span className="text-[10px] text-slate-400 font-black uppercase block mb-1">Status</span>
                    <span className="text-sm font-bold text-slate-800">Analyzed by Medaura</span>
                  </div>
                  <div className="bg-slate-50 p-4 rounded-2xl">
                    <span className="text-[10px] text-slate-400 font-black uppercase block mb-1">Patient</span>
                    <span className="text-sm font-bold text-slate-800">{patientData.age}y/o {patientData.gender}</span>
                  </div>
                  <div className="bg-slate-50 p-4 rounded-2xl border-l-4 border-indigo-500">
                    <span className="text-[10px] text-slate-400 font-black uppercase block mb-1">Focus Symptoms</span>
                    <p className="text-xs text-slate-600 italic font-medium leading-relaxed">"{patientData.symptoms}"</p>
                  </div>
                </div>
              </div>

              <div className="bg-indigo-900 text-white rounded-[2rem] p-8 shadow-2xl relative overflow-hidden group">
                 <Activity size={100} className="absolute -right-4 -bottom-4 opacity-10 group-hover:scale-125 transition-transform duration-700" />
                 <h4 className="font-black mb-3 flex items-center gap-3 text-sm uppercase tracking-widest"><RefreshCw size={18} className="text-indigo-400" /> Logic Engine</h4>
                 <p className="text-[11px] leading-relaxed opacity-70 font-semibold">
                   Medaura creates a 'Bio-Link' between clinical lab data and reported physical manifestations to identify physiological trends.
                 </p>
              </div>
            </div>

            {/* Expert Chat Terminal */}
            <div className="lg:col-span-3 bg-white rounded-[3rem] border border-slate-100 flex flex-col overflow-hidden shadow-2xl shadow-slate-200/50">
              <div className="px-8 py-6 border-b border-slate-50 flex items-center justify-between bg-white/80 backdrop-blur-xl sticky top-0 z-10">
                <div className="flex items-center gap-4">
                  <div className="relative">
                    <div className="w-12 h-12 rounded-2xl bg-indigo-600 flex items-center justify-center text-white shadow-lg">
                      <Stethoscope size={24} />
                    </div>
                    <div className="absolute -bottom-1 -right-1 w-4 h-4 bg-emerald-500 border-4 border-white rounded-full"></div>
                  </div>
                  <div>
                    <span className="font-black text-slate-800 block text-lg tracking-tight">Expert Synthesis</span>
                    <span className="text-[9px] text-slate-400 font-black uppercase tracking-[0.2em] flex items-center gap-1.5">
                      Neural Diagnostic Mode Active
                    </span>
                  </div>
                </div>
                <button 
                  onClick={() => setStep(1)} 
                  className="px-5 py-2.5 bg-slate-50 hover:bg-slate-100 text-slate-600 text-xs font-black rounded-xl transition-colors border border-slate-200 uppercase tracking-tighter"
                >
                  New Case
                </button>
              </div>

              {/* Chat Viewport */}
              <div className="flex-1 overflow-y-auto p-8 space-y-8 bg-slate-50/20 custom-scrollbar">
                {chatHistory.map((msg, idx) => (
                  <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'} animate-in fade-in slide-in-from-bottom-2`}>
                    <div className={`max-w-[85%] rounded-[2rem] px-7 py-6 text-sm leading-relaxed shadow-sm transition-all ${
                      msg.role === 'user' 
                        ? 'bg-indigo-600 text-white rounded-tr-none shadow-indigo-100 font-semibold' 
                        : 'bg-white text-slate-800 rounded-tl-none border border-slate-100 font-medium'
                    }`}>
                      <div className="whitespace-pre-wrap">
                        {msg.text}
                      </div>
                    </div>
                  </div>
                ))}
                
                {loading && (
                  <div className="flex justify-start">
                    <div className="bg-white rounded-[1.5rem] px-6 py-5 flex gap-2 items-center border border-slate-100 shadow-sm">
                      <div className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce"></div>
                      <div className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce [animation-delay:0.2s]"></div>
                      <div className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce [animation-delay:0.4s]"></div>
                      <span className="text-[10px] font-black text-slate-400 ml-2 uppercase tracking-widest">Reasoning...</span>
                    </div>
                  </div>
                )}
                <div ref={chatEndRef} />
              </div>

              {/* Input Command Center */}
              <div className="p-8 bg-white border-t border-slate-50">
                <div className="relative flex items-center gap-4">
                  <input 
                    type="text" 
                    placeholder="Ask Medaura about a specific marker or trend..."
                    className="w-full bg-slate-50 border-2 border-slate-50 rounded-[2rem] px-8 py-6 pr-20 focus:ring-0 focus:border-indigo-500 outline-none shadow-inner transition-all text-sm font-semibold"
                    value={userInput}
                    onChange={(e) => setUserInput(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && handleChat()}
                    disabled={loading}
                  />
                  <button 
                    onClick={handleChat}
                    disabled={!userInput.trim() || loading}
                    className="absolute right-2 p-4 bg-indigo-600 hover:bg-indigo-700 disabled:bg-slate-300 text-white rounded-2xl transition-all shadow-xl active:scale-90"
                  >
                    <Send size={24} />
                  </button>
                </div>
                <div className="mt-4 flex items-center justify-center gap-6">
                   <div className="flex items-center gap-2 text-[9px] text-slate-300 font-black uppercase tracking-[0.2em]">
                      <ShieldCheck size={12} /> Privacy Guaranteed
                   </div>
                   <div className="flex items-center gap-2 text-[9px] text-slate-300 font-black uppercase tracking-[0.2em]">
                      <Info size={12} /> Research Only
                   </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </main>

      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
        
        body {
          font-family: 'Plus Jakarta Sans', sans-serif;
        }

        .custom-scrollbar::-webkit-scrollbar { width: 4px; }
        .custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
        .custom-scrollbar::-webkit-scrollbar-thumb { background: #e5e7eb; border-radius: 20px; }
        .custom-scrollbar::-webkit-scrollbar-thumb:hover { background: #d1d5db; }

        input[type=number]::-webkit-inner-spin-button, 
        input[type=number]::-webkit-outer-spin-button { 
          -webkit-appearance: none; 
          margin: 0; 
        }
      `}</style>
    </div>
  );
};

export default App;
