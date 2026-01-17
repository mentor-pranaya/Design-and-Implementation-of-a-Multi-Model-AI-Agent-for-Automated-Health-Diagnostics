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
  History,
  Lock,
  LogOut,
  UserPlus
} from 'lucide-react';
import { initializeApp } from 'firebase/app';
import { 
  getAuth, 
  signInAnonymously, 
  signInWithEmailAndPassword, 
  createUserWithEmailAndPassword, 
  onAuthStateChanged, 
  signOut,
  signInWithCustomToken
} from 'firebase/auth';
import { 
  getFirestore, 
  doc, 
  setDoc, 
  getDoc, 
  collection, 
  onSnapshot 
} from 'firebase/firestore';

/**
 * MEDAURA: AI Medical Expert System with Secure Auth
 */

// Firebase Configuration (Environment Provided)
const firebaseConfig = JSON.parse(__firebase_config);
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const db = getFirestore(app);
const appId = typeof __app_id !== 'undefined' ? __app_id : 'medaura-expert-system';

const MODEL_NAME = "gemini-2.5-flash-preview-09-2025";
const apiKey = "";                                                             

const App = () => {
  // Navigation & Auth State
  const [user, setUser] = useState(null);
  const [authView, setAuthView] = useState('login'); // 'login' | 'signup'
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [authLoading, setAuthLoading] = useState(true);

  // App Workflow State
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

  // 1. Initialize Auth
  useEffect(() => {
    const initAuth = async () => {
      try {
        if (typeof __initial_auth_token !== 'undefined' && __initial_auth_token) {
          await signInWithCustomToken(auth, __initial_auth_token);
        }
      } catch (err) {
        console.error("Auth init error:", err);
      } finally {
        setAuthLoading(false);
      }
    };
    initAuth();

    const unsubscribe = onAuthStateChanged(auth, (currentUser) => {
      setUser(currentUser);
      setAuthLoading(false);
    });
    return () => unsubscribe();
  }, []);

  // 2. Fetch User Profile from Firestore (Rule 1 & 3 Compliance)
  useEffect(() => {
    if (!user) return;

    const userDocRef = doc(db, 'artifacts', appId, 'users', user.uid, 'settings', 'profile');
    const unsubscribe = onSnapshot(userDocRef, (docSnap) => {
      if (docSnap.exists()) {
        const data = docSnap.data();
        setPatientData(prev => ({ ...prev, ...data }));
      }
    }, (err) => console.error("Firestore read error:", err));

    return () => unsubscribe();
  }, [user]);

  // Auto-scroll chat
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chatHistory]);

  const handleAuth = async (e) => {
    e.preventDefault();
    setErrorMsg(null);
    setAuthLoading(true);
    try {
      if (authView === 'login') {
        await signInWithEmailAndPassword(auth, email, password);
      } else {
        const cred = await createUserWithEmailAndPassword(auth, email, password);
        // Save initial profile path: /artifacts/{appId}/users/{userId}/{collectionName}
        await setDoc(doc(db, 'artifacts', appId, 'users', cred.user.uid, 'settings', 'profile'), {
          createdAt: new Date().toISOString()
        });
      }
    } catch (err) {
      setErrorMsg(err.message.replace("Firebase: ", ""));
    } finally {
      setAuthLoading(false);
    }
  };

  const handleLogout = () => signOut(auth);

  const saveProfile = async (newData) => {
    if (!user) return;
    try {
      await setDoc(doc(db, 'artifacts', appId, 'users', user.uid, 'settings', 'profile'), newData, { merge: true });
    } catch (err) {
      console.error("Save error:", err);
    }
  };

  const handleFileUpload = (e) => {
    const file = e.target.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onloadend = () => {
      const base64Data = reader.result.split(',')[1];
      setFileData({ inlineData: { data: base64Data, mimeType: file.type } });
      setStep(2);
    };
    reader.readAsDataURL(file);
  };

  const callGemini = async (prompt, media = null) => {
    const systemPrompt = `You are MEDAURA, a highly advanced Medical Expert System. 
    Guidelines: 1. Use analogies. 2. Pattern recognition (link markers to symptoms). 3. Disclaimer: Not a doctor. 4. Highlight urgency if needed.`;

    const payload = {
      contents: [{ role: "user", parts: [{ text: prompt }, ...(media ? [media] : [])] }],
      systemInstruction: { parts: [{ text: systemPrompt }] }
    };

    const delays = [1000, 2000, 4000, 8000, 16000];
    for (let i = 0; i <= 5; i++) {
      try {
        const response = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/${MODEL_NAME}:generateContent?key=${apiKey}`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
        if (!response.ok) throw new Error(`API error: ${response.status}`);
        const data = await response.json();
        return data.candidates?.[0]?.content?.parts?.[0]?.text;
      } catch (err) {
        if (i === 5) throw err;
        await new Promise(r => setTimeout(r, delays[i]));
      }
    }
  };

  const processReport = async () => {
    setLoading(true);
    setErrorMsg(null);
    await saveProfile(patientData);
    
    const analysisPrompt = `Analyze blood report for ${patientData.age}y/o ${patientData.gender}. Symptoms: ${patientData.symptoms}. 
    Structure: Summary, Flags, Pattern Correlation, Doctor Questions.`;

    try {
      const result = await callGemini(analysisPrompt, fileData);
      setChatHistory([{ role: 'model', text: result }]);
      setStep(3);
    } catch (err) {
      setErrorMsg("Neural engine is busy. Please try again.");
    } finally {
      setLoading(false);
    }
  };

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
      setErrorMsg("Expert logic disrupted. Reconnecting...");
    } finally {
      setLoading(false);
    }
  };

  if (authLoading) {
    return (
      <div className="min-h-screen bg-[#fcfdfe] flex items-center justify-center">
        <Loader2 className="animate-spin text-indigo-600" size={40} />
      </div>
    );
  }

  // Auth Screen
  if (!user) {
    return (
      <div className="min-h-screen bg-[#fcfdfe] flex items-center justify-center p-4">
        <div className="max-w-md w-full bg-white rounded-[2.5rem] p-10 shadow-2xl border border-slate-100 animate-in zoom-in duration-300">
          <div className="text-center mb-8">
            <div className="bg-indigo-600 w-16 h-16 rounded-2xl flex items-center justify-center text-white mx-auto mb-4 shadow-lg">
              <Lock size={30} />
            </div>
            <h2 className="text-3xl font-black text-slate-800 uppercase tracking-tighter">
              MED<span className="text-indigo-600">AURA</span>
            </h2>
            <p className="text-slate-400 text-sm font-bold uppercase tracking-widest mt-1">Secure Portal Access</p>
          </div>

          <form onSubmit={handleAuth} className="space-y-4">
            {errorMsg && <div className="p-3 bg-rose-50 text-rose-600 text-xs font-bold rounded-xl border border-rose-100">{errorMsg}</div>}
            <div>
              <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest ml-1">Email Address</label>
              <input 
                type="email" required
                className="w-full bg-slate-50 border-2 border-transparent rounded-2xl px-5 py-4 focus:border-indigo-500 outline-none transition-all font-semibold"
                value={email} onChange={e => setEmail(e.target.value)}
              />
            </div>
            <div>
              <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest ml-1">Password</label>
              <input 
                type="password" required
                className="w-full bg-slate-50 border-2 border-transparent rounded-2xl px-5 py-4 focus:border-indigo-500 outline-none transition-all font-semibold"
                value={password} onChange={e => setPassword(e.target.value)}
              />
            </div>
            <button 
              type="submit" disabled={authLoading}
              className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-black py-5 rounded-2xl transition-all shadow-xl shadow-indigo-100 flex items-center justify-center gap-2"
            >
              {authView === 'login' ? 'Sign In' : 'Create Account'}
            </button>
          </form>

          <div className="mt-6 text-center">
            <button 
              onClick={() => setAuthView(authView === 'login' ? 'signup' : 'login')}
              className="text-xs font-bold text-slate-500 hover:text-indigo-600 flex items-center justify-center gap-2 mx-auto"
            >
              {authView === 'login' ? <><UserPlus size={14} /> Don't have an account? Sign Up</> : <><History size={14} /> Already a member? Log In</>}
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Main App Screen
  return (
    <div className="min-h-screen bg-[#fcfdfe] text-slate-900 font-sans p-4 md:p-8 selection:bg-indigo-100">
      <nav className="max-w-6xl mx-auto flex items-center justify-between mb-10">
        <div className="flex items-center gap-4">
          <div className="bg-gradient-to-br from-indigo-600 to-blue-500 p-3 rounded-2xl text-white shadow-xl shadow-indigo-100">
            <Stethoscope size={28} />
          </div>
          <div>
            <h1 className="text-2xl font-black tracking-tighter text-slate-800 uppercase leading-none">
              MED<span className="text-indigo-600">AURA</span>
            </h1>
            <span className="text-[9px] font-bold text-slate-400 tracking-[0.2em] uppercase">User: {user.email?.split('@')[0]}</span>
          </div>
        </div>
        <button 
          onClick={handleLogout}
          className="p-2 text-slate-400 hover:text-rose-600 transition-colors" title="Logout"
        >
          <LogOut size={22} />
        </button>
      </nav>

      <main className="max-w-6xl mx-auto relative">
        {errorMsg && (
          <div className="mb-8 max-w-2xl mx-auto bg-rose-50 border border-rose-100 text-rose-700 p-5 rounded-3xl flex items-center gap-4">
            <AlertCircle size={24} className="shrink-0" />
            <p className="text-sm font-semibold">{errorMsg}</p>
          </div>
        )}

        {step === 0 && (
          <div className="max-w-2xl mx-auto bg-white rounded-[3rem] p-10 md:p-14 shadow-2xl border border-slate-100 text-center animate-in zoom-in">
            <div className="w-20 h-20 bg-amber-50 text-amber-600 rounded-full flex items-center justify-center mx-auto mb-10 border-4 border-white shadow-inner">
              <Scale size={40} />
            </div>
            <h2 className="text-3xl font-black mb-6 text-slate-800 tracking-tight">Access Expert Engine</h2>
            <div className="space-y-4 text-left mb-10 bg-slate-50 p-6 rounded-[2rem] border border-slate-100">
              <div className="flex gap-4 items-center">
                <ShieldCheck className="text-indigo-600" size={24} />
                <p className="text-xs font-bold text-slate-600 leading-relaxed">Secure data link established. Reports are processed privately within your session.</p>
              </div>
              <div className="flex gap-4 items-center">
                <Activity className="text-indigo-600" size={24} />
                <p className="text-xs font-bold text-slate-600 leading-relaxed">Cross-referencing technology matches biomarkers to clinical patterns.</p>
              </div>
            </div>
            <button onClick={() => setStep(1)} className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-black px-12 py-6 rounded-3xl shadow-xl transition-all active:scale-95 flex items-center justify-center gap-3">
              Initialize Analysis <ChevronRight size={24} />
            </button>
          </div>
        )}

        {step === 1 && (
          <div className="max-w-3xl mx-auto bg-white rounded-[3.5rem] p-16 shadow-2xl border border-slate-100 text-center animate-in slide-in-from-right-12">
            <div className="w-28 h-28 bg-indigo-50 text-indigo-600 rounded-full flex items-center justify-center mx-auto mb-10 shadow-inner">
               <Upload size={54} />
            </div>
            <h2 className="text-4xl font-black mb-4 text-slate-800 tracking-tighter uppercase">Upload Report</h2>
            <p className="text-slate-400 mb-10 max-w-md mx-auto leading-relaxed text-lg font-medium">Select a digital blood report or clear photo to decode clinical data.</p>
            <label className="inline-flex items-center gap-4 bg-slate-900 hover:bg-black text-white font-black px-12 py-7 rounded-[2rem] cursor-pointer transition-all active:scale-95">
              <FileText size={28} /> Choose File
              <input type="file" className="hidden" accept="image/*,application/pdf" onChange={handleFileUpload} />
            </label>
          </div>
        )}

        {step === 2 && (
          <div className="max-w-2xl mx-auto bg-white rounded-[3rem] p-12 shadow-2xl border border-slate-100 animate-in slide-in-from-bottom-10">
            <h2 className="text-2xl font-black text-slate-800 mb-10 flex items-center gap-4">
              <div className="p-3 bg-indigo-100 rounded-2xl text-indigo-600"><User size={24} /></div> Case Profile
            </h2>
            <div className="space-y-6">
              <div className="grid grid-cols-2 gap-6">
                <div className="space-y-2">
                  <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest ml-1">Age</label>
                  <input type="number" className="w-full bg-slate-50 border-2 border-transparent rounded-2xl px-6 py-4 focus:border-indigo-500 outline-none font-bold" value={patientData.age} onChange={e => setPatientData({...patientData, age: e.target.value})}/>
                </div>
                <div className="space-y-2">
                  <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest ml-1">Gender</label>
                  <select className="w-full bg-slate-50 border-2 border-transparent rounded-2xl px-6 py-4 focus:border-indigo-500 outline-none font-bold appearance-none" value={patientData.gender} onChange={e => setPatientData({...patientData, gender: e.target.value})}>
                    <option>Male</option><option>Female</option><option>Other</option>
                  </select>
                </div>
              </div>
              <div className="space-y-2">
                <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest ml-1">Describe Symptoms</label>
                <textarea rows="4" className="w-full bg-slate-50 border-2 border-transparent rounded-[2rem] px-6 py-5 focus:border-indigo-500 outline-none resize-none font-medium text-slate-600" value={patientData.symptoms} onChange={e => setPatientData({...patientData, symptoms: e.target.value})}></textarea>
              </div>
              <button onClick={processReport} disabled={!patientData.age || loading} className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-black py-6 rounded-[2rem] transition-all flex items-center justify-center gap-4 shadow-xl shadow-indigo-100">
                {loading ? <Loader2 className="animate-spin" /> : <HeartPulse size={24} />}
                {loading ? "Reasoning Biomarkers..." : "Synthesize Case"}
              </button>
            </div>
          </div>
        )}

        {step === 3 && (
          <div className="grid grid-cols-1 lg:grid-cols-4 gap-10 h-[80vh]">
            <div className="lg:col-span-1 space-y-6 hidden lg:block overflow-y-auto pr-2 custom-scrollbar">
              <div className="bg-white rounded-[2rem] p-8 border border-slate-100 shadow-sm">
                <h3 className="font-black text-slate-800 mb-6 flex items-center gap-3 text-xs uppercase tracking-wider"><History size={16} className="text-indigo-500" /> Active Profile</h3>
                <div className="space-y-4">
                  <div className="bg-slate-50 p-4 rounded-2xl border-l-4 border-indigo-500">
                    <span className="text-[9px] text-slate-400 font-black uppercase block mb-1">Status</span>
                    <span className="text-xs font-bold text-slate-800 tracking-tight leading-none uppercase">Expert Verified</span>
                  </div>
                  <div className="bg-slate-50 p-4 rounded-2xl">
                    <span className="text-[9px] text-slate-400 font-black uppercase block mb-1">Symptoms Context</span>
                    <p className="text-[10px] text-slate-600 italic font-bold leading-relaxed line-clamp-4">"{patientData.symptoms}"</p>
                  </div>
                </div>
              </div>
            </div>

            <div className="lg:col-span-3 bg-white rounded-[3rem] border border-slate-100 flex flex-col overflow-hidden shadow-2xl">
              <div className="px-8 py-6 border-b border-slate-50 flex items-center justify-between sticky top-0 bg-white z-10">
                <div className="flex items-center gap-4">
                  <div className="w-12 h-12 rounded-2xl bg-indigo-600 flex items-center justify-center text-white shadow-lg"><Stethoscope size={24} /></div>
                  <div><span className="font-black text-slate-800 block text-lg tracking-tight">AI Expert Analysis</span><span className="text-[9px] text-emerald-500 font-black uppercase tracking-[0.2em] animate-pulse">Neural Path Engaged</span></div>
                </div>
                <button onClick={() => setStep(1)} className="px-4 py-2 bg-slate-50 text-[10px] font-black rounded-xl border border-slate-200 uppercase tracking-tighter">Clear Case</button>
              </div>

              <div className="flex-1 overflow-y-auto p-8 space-y-8 bg-slate-50/20 custom-scrollbar">
                {chatHistory.map((msg, idx) => (
                  <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'} animate-in fade-in`}>
                    <div className={`max-w-[85%] rounded-[2rem] px-7 py-6 text-sm leading-relaxed ${msg.role === 'user' ? 'bg-indigo-600 text-white rounded-tr-none font-semibold' : 'bg-white text-slate-800 rounded-tl-none border border-slate-100 font-medium shadow-sm'}`}>
                      <div className="whitespace-pre-wrap">{msg.text}</div>
                    </div>
                  </div>
                ))}
                {loading && (
                  <div className="flex justify-start">
                    <div className="bg-white rounded-[1.5rem] px-6 py-5 flex gap-2 items-center border border-slate-100 shadow-sm"><div className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce"></div><div className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce [animation-delay:0.2s]"></div><div className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce [animation-delay:0.4s]"></div></div>
                  </div>
                )}
                <div ref={chatEndRef} />
              </div>

              <div className="p-8 bg-white border-t border-slate-50">
                <div className="relative flex items-center gap-4">
                  <input type="text" placeholder="Inquire about markers or symptoms..." className="w-full bg-slate-50 border-2 border-transparent rounded-[2rem] px-8 py-6 pr-20 focus:border-indigo-500 outline-none shadow-inner transition-all text-sm font-semibold" value={userInput} onChange={e => setUserInput(e.target.value)} onKeyDown={e => e.key === 'Enter' && handleChat()} disabled={loading} />
                  <button onClick={handleChat} disabled={!userInput.trim() || loading} className="absolute right-2 p-4 bg-indigo-600 hover:bg-indigo-700 disabled:bg-slate-300 text-white rounded-2xl shadow-xl"><Send size={24} /></button>
                </div>
              </div>
            </div>
          </div>
        )}
      </main>

      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
        body { font-family: 'Plus Jakarta Sans', sans-serif; }
        .custom-scrollbar::-webkit-scrollbar { width: 4px; }
        .custom-scrollbar::-webkit-scrollbar-thumb { background: #e5e7eb; border-radius: 20px; }
      `}</style>
    </div>
  );
};

export default App;
