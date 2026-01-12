import React, { useState, useEffect, useRef } from 'react';
import { PlusCircle, Trash2, Sparkles, AlertCircle, CheckCircle2, ChevronRight } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { cn } from '../utils/cn';
import { analyzeDecision, pollAnalysisStatus } from '../api';

const POLL_INTERVAL = 3000; // 3 seconds
const MAX_POLL_ATTEMPTS = 60; // 3 minutes max

const NewDecision = () => {
    const [context, setContext] = useState('');
    const [variants, setVariants] = useState([{ title: 'Path A', essay: '' }]);
    const [activeVariantIdx, setActiveVariantIdx] = useState(0);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [result, setResult] = useState(null);
    const [analysisStatus, setAnalysisStatus] = useState('');
    const pollIntervalRef = useRef(null);
    const pollAttemptsRef = useRef(0);

    useEffect(() => {
        return () => {
            if (pollIntervalRef.current) {
                clearInterval(pollIntervalRef.current);
            }
        };
    }, []);

    const addVariant = () => {
        const newIdx = variants.length;
        setVariants([...variants, { title: `Path ${String.fromCharCode(65 + newIdx)}`, essay: '' }]);
        setActiveVariantIdx(newIdx);
    };

    const removeVariant = (idx) => {
        if (variants.length <= 1) return;
        const newVariants = variants.filter((_, i) => i !== idx);
        setVariants(newVariants);
        setActiveVariantIdx(Math.max(0, idx - 1));
    };

    const updateVariant = (idx, field, value) => {
        const newVariants = [...variants];
        newVariants[idx][field] = value;
        setVariants(newVariants);
    };

    const startPolling = async (decisionId) => {
        pollAttemptsRef.current = 0;

        pollIntervalRef.current = setInterval(async () => {
            try {
                pollAttemptsRef.current += 1;

                if (pollAttemptsRef.current > MAX_POLL_ATTEMPTS) {
                    clearInterval(pollIntervalRef.current);
                    setError('Analysis is taking longer than expected. Please check the History view later.');
                    setLoading(false);
                    setAnalysisStatus('');
                    return;
                }

                const statusData = await pollAnalysisStatus(decisionId);
                setAnalysisStatus(statusData.status);

                if (statusData.status === 'completed') {
                    clearInterval(pollIntervalRef.current);
                    setResult(statusData.results);
                    setLoading(false);
                    setAnalysisStatus('');
                } else if (statusData.status === 'failed') {
                    clearInterval(pollIntervalRef.current);
                    setError('Analysis failed. Please try again or check your input.');
                    setLoading(false);
                    setAnalysisStatus('');
                }
            } catch (err) {
                console.error('Polling error:', err);
                clearInterval(pollIntervalRef.current);
                setError('Failed to check analysis status. Please refresh and check History.');
                setLoading(false);
                setAnalysisStatus('');
            }
        }, POLL_INTERVAL);
    };

    const handleAnalyze = async () => {
        setError('');
        setResult(null);

        if (context.trim().length < 20) {
            setError('Context must be at least 20 characters long to provide a meaningful analysis.');
            return;
        }

        const validVariants = variants.filter(v => v.title.trim() && v.essay.trim());
        if (validVariants.length < 1) {
            setError('At least one complete path (title and essay) is required.');
            return;
        }

        setLoading(true);
        setAnalysisStatus('pending');

        try {
            const payload = {
                context,
                variants: validVariants.map(v => v.title),
                selected_variant: null,
                arguments: validVariants.map(v => ({
                    variant_name: v.title,
                    type: 'essay',
                    text: v.essay
                }))
            };

            const response = await analyzeDecision(payload);

            if (response.decision_id) {
                setAnalysisStatus('analyzing');
                startPolling(response.decision_id);
            } else {
                setError('Failed to start analysis. Invalid response from server.');
                setLoading(false);
            }
        } catch (err) {
            setError(err.userMessage || err.message || 'Failed to start analysis');
            setLoading(false);
            setAnalysisStatus('');
            console.error(err);
        }
    };

    const getStatusMessage = () => {
        switch (analysisStatus) {
            case 'pending':
                return 'Initializing analysis...';
            case 'analyzing':
                return 'AI is analyzing your decision paths...';
            default:
                return 'Processing...';
        }
    };

    return (
        <div className="space-y-16">
            <header className="space-y-4">
                <h2 className="text-4xl font-bold text-white leading-tight">New Decision</h2>
                <p className="text-zinc-500 text-lg max-w-2xl leading-relaxed">
                    Structure your thoughts by mapping out the context and exploring potential paths. Our AI will help you identify patterns and insights.
                </p>
            </header>

            <div className="space-y-12">
                {/* Context Section */}
                <section className="space-y-6">
                    <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-widest text-zinc-500">
                        <span className="w-1.5 h-1.5 rounded-full bg-indigo-500" />
                        01. Define the Situation
                    </div>
                    <textarea
                        value={context}
                        onChange={(e) => setContext(e.target.value)}
                        placeholder="What is the challenge you're facing? Be as detailed as possible..."
                        className="w-full h-40 bg-white/[0.03] border border-white/10 rounded-2xl p-6 text-zinc-100 placeholder:text-zinc-700 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 transition-all custom-scrollbar resize-none text-lg leading-relaxed"
                        disabled={loading}
                    />
                </section>

                {/* Paths Section */}
                <section className="space-y-8">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-widest text-zinc-500">
                            <span className="w-1.5 h-1.5 rounded-full bg-indigo-500" />
                            02. Map Out Paths
                        </div>
                        <button
                            onClick={addVariant}
                            disabled={loading}
                            className="flex items-center gap-2 text-sm text-indigo-400 hover:text-indigo-300 font-semibold transition-colors py-2 px-4 rounded-xl hover:bg-white/5 disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            <PlusCircle size={20} strokeWidth={1.5} />
                            Add Path
                        </button>
                    </div>

                    <div className="space-y-6">
                        {/* Tabs */}
                        <div className="flex flex-wrap gap-2">
                            {variants.map((v, i) => (
                                <button
                                    key={i}
                                    onClick={() => setActiveVariantIdx(i)}
                                    disabled={loading}
                                    className={cn(
                                        "px-6 py-3 rounded-xl text-sm font-semibold transition-all border shrink-0",
                                        activeVariantIdx === i
                                            ? "bg-white text-black border-white shadow-lg shadow-white/10"
                                            : "bg-transparent text-zinc-500 border-white/10 hover:border-white/30 hover:text-zinc-200",
                                        loading && "opacity-50 cursor-not-allowed"
                                    )}
                                >
                                    {v.title || `Path ${i + 1}`}
                                </button>
                            ))}
                        </div>

                        {/* Path Content */}
                        <div className="bg-white/[0.02] border border-white/5 rounded-3xl p-8 space-y-8">
                            <div className="flex gap-4 items-center">
                                <input
                                    type="text"
                                    value={variants[activeVariantIdx]?.title}
                                    onChange={(e) => updateVariant(activeVariantIdx, 'title', e.target.value)}
                                    placeholder="Path Name (e.g., 'Take the offer')"
                                    className="flex-1 bg-transparent border-none text-2xl font-bold text-white placeholder:text-zinc-800 focus:outline-none"
                                    disabled={loading}
                                />
                                {variants.length > 1 && (
                                    <button
                                        onClick={() => removeVariant(activeVariantIdx)}
                                        disabled={loading}
                                        className="p-3 text-zinc-600 hover:text-red-400 hover:bg-red-400/10 rounded-xl transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                                    >
                                        <Trash2 size={20} strokeWidth={1.5} />
                                    </button>
                                )}
                            </div>
                            <textarea
                                value={variants[activeVariantIdx]?.essay}
                                onChange={(e) => updateVariant(activeVariantIdx, 'essay', e.target.value)}
                                placeholder="Why this path? What values does it support? What do you become? What is the price?"
                                className="w-full h-80 bg-white/[0.02] border border-white/5 rounded-2xl p-6 text-zinc-200 placeholder:text-zinc-700 focus:outline-none focus:ring-1 focus:ring-white/10 transition-all custom-scrollbar text-lg leading-relaxed"
                                disabled={loading}
                            />
                        </div>
                    </div>
                </section>

                {/* Action Section */}
                <section className="space-y-6 pt-12">
                    <AnimatePresence>
                        {error && (
                            <motion.div
                                initial={{ opacity: 0, y: -10 }}
                                animate={{ opacity: 1, y: 0 }}
                                exit={{ opacity: 0, y: -10 }}
                                className="flex items-center gap-4 p-5 bg-red-500/5 border border-red-500/10 rounded-2xl text-red-400"
                            >
                                <AlertCircle size={20} strokeWidth={1.5} />
                                <p className="text-sm font-medium">{error}</p>
                            </motion.div>
                        )}
                    </AnimatePresence>

                    <button
                        onClick={handleAnalyze}
                        disabled={loading}
                        className={cn(
                            "w-full py-6 rounded-2xl flex items-center justify-center gap-4 font-bold text-xl transition-all duration-300",
                            loading
                                ? "bg-zinc-900 text-zinc-600 cursor-not-allowed border border-white/5"
                                : "bg-white text-black hover:scale-[1.01] active:scale-[0.99] shadow-2xl shadow-white/5"
                        )}
                    >
                        {loading ? (
                            <>
                                <div className="w-6 h-6 border-2 border-zinc-700 border-t-white rounded-full animate-spin" />
                                {getStatusMessage()}
                            </>
                        ) : (
                            <>
                                <Sparkles size={24} strokeWidth={1.5} />
                                Analyze Decision
                            </>
                        )}
                    </button>
                </section>
            </div>

            {/* Results Section */}
            <AnimatePresence>
                {result && (
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="space-y-16 pt-16 border-t border-white/5"
                    >
                        <div className="flex items-center gap-4 p-6 bg-emerald-500/5 border border-emerald-500/10 rounded-3xl text-emerald-400">
                            <CheckCircle2 size={24} strokeWidth={1.5} />
                            <div>
                                <p className="font-bold text-lg text-emerald-300">Analysis Complete</p>
                                <p className="text-sm opacity-80 font-medium">Your decision has been analyzed and saved to history</p>
                            </div>
                        </div>

                        {result.ml_scores && (
                            <div className="space-y-8">
                                <h3 className="text-xs font-bold uppercase tracking-widest text-zinc-500">ML Argument Strength Scores</h3>
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                    {Object.entries(result.ml_scores).map(([key, score]) => (
                                        <div key={key} className="p-6 bg-white/[0.02] border border-white/5 rounded-2xl">
                                            <div className="flex items-center justify-between mb-4">
                                                <span className="text-sm font-semibold text-zinc-300">{variants[parseInt(key.split('_')[1])]?.title || key}</span>
                                                <span className="text-2xl font-bold text-white">{score.toFixed(1)}</span>
                                            </div>
                                            <div className="w-full bg-zinc-900 rounded-full h-2">
                                                <div
                                                    className="bg-gradient-to-r from-indigo-600 to-violet-600 h-2 rounded-full transition-all duration-1000"
                                                    style={{ width: `${score}%` }}
                                                />
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}

                        {result.llm_analysis && (
                            <div className="space-y-8">
                                <h3 className="text-xs font-bold uppercase tracking-widest text-zinc-500">AI Analysis</h3>
                                <div className="space-y-6">
                                    {result.llm_analysis.argument_quality_comparison && (
                                        <div className="p-8 bg-white/[0.02] border border-white/5 rounded-3xl space-y-4">
                                            <h4 className="text-sm font-bold text-indigo-400 uppercase tracking-wider">Quality Comparison</h4>
                                            {Object.entries(result.llm_analysis.argument_quality_comparison).map(([variant, analysis]) => (
                                                <div key={variant} className="space-y-2">
                                                    <p className="text-sm font-semibold text-zinc-300">{variant}</p>
                                                    <p className="text-zinc-400 leading-relaxed">{analysis}</p>
                                                </div>
                                            ))}
                                        </div>
                                    )}

                                    {result.llm_analysis.key_weak_points_to_reconsider && (
                                        <div className="p-8 bg-amber-500/5 border border-amber-500/10 rounded-3xl space-y-4">
                                            <h4 className="text-sm font-bold text-amber-400 uppercase tracking-wider">Key Weak Points</h4>
                                            <ul className="space-y-2">
                                                {result.llm_analysis.key_weak_points_to_reconsider.map((point, idx) => (
                                                    <li key={idx} className="flex items-start gap-3 text-zinc-300">
                                                        <span className="text-amber-400 mt-1">•</span>
                                                        <span className="leading-relaxed">{point}</span>
                                                    </li>
                                                ))}
                                            </ul>
                                        </div>
                                    )}

                                    {result.llm_analysis.final_note && (
                                        <div className="p-8 bg-white/[0.02] border border-white/5 rounded-3xl">
                                            <h4 className="text-sm font-bold text-zinc-400 uppercase tracking-wider mb-4">Final Note</h4>
                                            <p className="text-zinc-300 leading-relaxed">{result.llm_analysis.final_note}</p>
                                        </div>
                                    )}
                                </div>
                            </div>
                        )}

                        {result.retrieved_context && result.retrieved_context.length > 0 && (
                            <div className="space-y-8">
                                <h3 className="text-xs font-bold uppercase tracking-widest text-zinc-500">Similar Past Decisions</h3>
                                <div className="grid grid-cols-1 gap-4">
                                    {result.retrieved_context.slice(0, 3).map((context, idx) => (
                                        <div key={idx} className="p-6 bg-white/[0.02] border border-white/5 rounded-2xl hover:border-white/10 transition-colors">
                                            <p className="text-sm text-zinc-400 leading-relaxed">{context}</p>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
};

export default NewDecision;
