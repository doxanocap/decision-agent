import React, { useState, useEffect } from 'react';
import { ChevronDown, Calendar, CheckCircle2, History as HistoryIcon, MessageSquare, Tag, Send, ArrowRight } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { cn } from '../utils/cn';
import { getDecisions, updateOutcome } from '../api';

const HistoryView = () => {
    const [decisions, setDecisions] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [expandedId, setExpandedId] = useState(null);
    const [outcomeData, setOutcomeData] = useState({ outcome: '', variant: '' });

    useEffect(() => {
        fetchDecisions();
    }, []);

    const fetchDecisions = async () => {
        try {
            setLoading(true);
            setError('');
            const data = await getDecisions();
            setDecisions(data.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp)));
        } catch (err) {
            setError(err.userMessage || err.message || 'Failed to load history');
            console.error('Failed to fetch decisions', err);
        } finally {
            setLoading(false);
        }
    };

    const handleConfirm = async (id) => {
        if (!outcomeData.outcome || !outcomeData.variant) return;
        try {
            await updateOutcome(id, {
                outcome: outcomeData.outcome,
                selected_variant: outcomeData.variant,
            });
            setOutcomeData({ outcome: '', variant: '' });
            fetchDecisions();
        } catch (err) {
            setError(err.userMessage || err.message || 'Failed to update outcome');
            console.error('Failed to update outcome', err);
        }
    };

    if (loading) {
        return (
            <div className="flex flex-col items-center justify-center py-32 space-y-8 animate-pulse text-zinc-700">
                <HistoryIcon size={64} strokeWidth={1} className="opacity-20" />
                <p className="font-bold tracking-widest uppercase text-xs">Retrieving Archive</p>
            </div>
        );
    }

    if (error) {
        return (
            <div className="flex flex-col items-center justify-center py-32 space-y-8 text-center">
                <div className="p-6 bg-red-500/10 rounded-full border border-red-500/20">
                    <MessageSquare size={48} className="text-red-400" strokeWidth={1.5} />
                </div>
                <div className="space-y-2">
                    <p className="text-lg font-semibold text-red-400">{error}</p>
                    <button
                        onClick={fetchDecisions}
                        className="text-sm text-zinc-400 hover:text-white transition-colors"
                    >
                        Try again
                    </button>
                </div>
            </div>
        );
    }

    return (
        <div className="space-y-16">
            <header className="space-y-4">
                <h2 className="text-4xl font-bold text-white leading-tight">Archive</h2>
                <p className="text-zinc-500 text-lg max-w-2xl leading-relaxed">
                    Access your historical decision-making logs and track real-world results to refine your intuition over time.
                </p>
            </header>

            {decisions.length === 0 ? (
                <div className="py-24 border border-dashed border-white/5 rounded-[2rem] flex flex-col items-center justify-center text-zinc-600 space-y-4">
                    <MessageSquare size={48} strokeWidth={1} className="opacity-20" />
                    <p className="text-sm font-medium">Your archive is currently empty.</p>
                </div>
            ) : (
                <div className="space-y-4">
                    <AnimatePresence>
                        {decisions.map((d, i) => (
                            <DecisionCard
                                key={d.id}
                                decision={d}
                                index={i}
                                isExpanded={expandedId === d.id}
                                onToggle={() => setExpandedId(expandedId === d.id ? null : d.id)}
                                onConfirm={() => handleConfirm(d.id)}
                                outcomeData={outcomeData}
                                setOutcomeData={setOutcomeData}
                            />
                        ))}
                    </AnimatePresence>
                </div>
            )}
        </div>
    );
};

const DecisionCard = ({ decision, index, isExpanded, onToggle, onConfirm, outcomeData, setOutcomeData }) => {
    const formatDate = (isoStr) => {
        const date = new Date(isoStr);
        return date.toLocaleDateString('en-US', {
            month: 'short',
            day: 'numeric',
            year: 'numeric'
        });
    };

    const variants = Array.isArray(decision.variants)
        ? decision.variants.map(v => typeof v === 'string' ? v : v.name)
        : [];

    return (
        <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.05 }}
            className={cn(
                "group border transition-all duration-500 overflow-hidden",
                isExpanded
                    ? "bg-white/[0.03] border-white/20 rounded-3xl"
                    : "bg-transparent border-white/5 hover:border-white/10 rounded-2xl"
            )}
        >
            <div
                onClick={onToggle}
                className="p-8 cursor-pointer flex items-center justify-between gap-8"
            >
                <div className="flex-1 min-w-0 space-y-2">
                    <div className="flex items-center gap-4">
                        <span className="text-[10px] font-bold text-zinc-600 uppercase tracking-widest font-mono">
                            {formatDate(decision.timestamp)}
                        </span>
                        {decision.outcome && (
                            <span className="flex items-center gap-1.5 text-[9px] font-bold text-emerald-500 bg-emerald-500/10 px-2 py-0.5 rounded-full uppercase tracking-wider border border-emerald-500/20">
                                <CheckCircle2 size={10} /> Consolved
                            </span>
                        )}
                    </div>
                    <h3 className={cn(
                        "text-lg font-semibold transition-colors truncate leading-relaxed",
                        isExpanded ? "text-white" : "text-zinc-400 group-hover:text-zinc-200"
                    )}>
                        {decision.context}
                    </h3>
                </div>
                <div className={cn(
                    "shrink-0 p-2 rounded-full border border-white/5 text-zinc-600 transition-all duration-500",
                    isExpanded ? "rotate-180 bg-white text-black border-white" : "group-hover:text-white group-hover:bg-white/5"
                )}>
                    <ChevronDown size={18} strokeWidth={2.5} />
                </div>
            </div>

            <AnimatePresence>
                {isExpanded && (
                    <motion.div
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: 'auto', opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                        transition={{ duration: 0.4, ease: [0.23, 1, 0.32, 1] }}
                    >
                        <div className="px-8 pb-10 pt-4 space-y-12 border-t border-white/5">
                            {/* Layout: Single Column Stack */}
                            <div className="space-y-12">
                                <section className="space-y-6">
                                    <h4 className="text-[10px] font-bold text-zinc-600 uppercase tracking-[0.2em]">Context Archive</h4>
                                    <p className="text-zinc-300 leading-relaxed text-lg whitespace-pre-wrap">
                                        {decision.context}
                                    </p>
                                </section>

                                <section className="space-y-8">
                                    <h4 className="text-[10px] font-bold text-zinc-600 uppercase tracking-[0.2em]">Evaluated Paths</h4>
                                    <div className="space-y-4">
                                        {decision.arguments?.map((arg, idx) => (
                                            <PathItem key={idx} arg={arg} />
                                        ))}
                                    </div>
                                </section>

                                {decision.llm_analysis && (
                                    <section className="space-y-8">
                                        <h4 className="text-[10px] font-bold text-zinc-600 uppercase tracking-[0.2em]">AI Analysis</h4>
                                        <div className="space-y-6">
                                            {decision.llm_analysis.key_weak_points_to_reconsider && decision.llm_analysis.key_weak_points_to_reconsider.length > 0 && (
                                                <div className="p-6 bg-amber-500/5 border border-amber-500/10 rounded-2xl space-y-3">
                                                    <h5 className="text-xs font-bold text-amber-400 uppercase tracking-wider">Key Weak Points</h5>
                                                    <ul className="space-y-2">
                                                        {decision.llm_analysis.key_weak_points_to_reconsider.map((point, idx) => (
                                                            <li key={idx} className="flex items-start gap-2 text-sm text-zinc-300">
                                                                <span className="text-amber-400 mt-0.5">•</span>
                                                                <span className="leading-relaxed">{point}</span>
                                                            </li>
                                                        ))}
                                                    </ul>
                                                </div>
                                            )}

                                            {decision.llm_analysis.final_note && (
                                                <div className="p-6 bg-white/[0.02] border border-white/5 rounded-2xl">
                                                    <h5 className="text-xs font-bold text-zinc-400 uppercase tracking-wider mb-3">Final Note</h5>
                                                    <p className="text-sm text-zinc-300 leading-relaxed">{decision.llm_analysis.final_note}</p>
                                                </div>
                                            )}
                                        </div>
                                    </section>
                                )}

                                {/* Track Result - Now at the bottom */}
                                <div className="pt-8 border-t border-white/5">
                                    {decision.outcome ? (
                                        <div className="p-8 bg-white/5 border border-white/10 rounded-3xl space-y-6 max-w-2xl">
                                            <div className="flex items-center gap-2 text-xs font-bold text-emerald-400 uppercase tracking-[0.2em]">
                                                <CheckCircle2 size={16} /> Result Logged
                                            </div>
                                            <div className="space-y-4">
                                                {decision.selected_variant && (
                                                    <div className="flex items-center gap-2 mb-4">
                                                        <Tag size={14} className="text-emerald-400" />
                                                        <span className="text-sm font-bold text-emerald-300">{decision.selected_variant}</span>
                                                    </div>
                                                )}
                                                <p className="text-zinc-300 leading-relaxed whitespace-pre-wrap">{decision.outcome}</p>
                                            </div>
                                        </div>
                                    ) : (
                                        <div className="group/track p-8 bg-indigo-600/5 border border-indigo-500/20 rounded-[2rem] space-y-8 max-w-2xl hover:bg-indigo-600/10 transition-colors">
                                            <div className="space-y-2">
                                                <h4 className="text-xs font-bold text-indigo-400 uppercase tracking-[0.2em] group-hover/track:text-indigo-300 transition-colors">Track Result</h4>
                                                <p className="text-zinc-500 text-xs leading-relaxed">Record which path you chose and what happened. This helps improve future recommendations.</p>
                                            </div>

                                            <div className="space-y-6">
                                                <div className="space-y-3">
                                                    <label className="text-[10px] font-bold text-zinc-600 uppercase tracking-widest px-1">Selected Path</label>
                                                    <select
                                                        value={outcomeData.variant}
                                                        onChange={(e) => setOutcomeData({ ...outcomeData, variant: e.target.value })}
                                                        className="w-full bg-black border border-white/10 rounded-xl p-3 text-sm text-zinc-300 focus:outline-none focus:ring-1 focus:ring-white/20 transition-all appearance-none cursor-pointer"
                                                    >
                                                        <option value="">Select Path</option>
                                                        {variants.map(v => <option key={v} value={v}>{v}</option>)}
                                                    </select>
                                                </div>

                                                <div className="space-y-3">
                                                    <label className="text-[10px] font-bold text-zinc-600 uppercase tracking-widest px-1">Outcome & Reasoning</label>
                                                    <textarea
                                                        value={outcomeData.outcome}
                                                        onChange={(e) => setOutcomeData({ ...outcomeData, outcome: e.target.value })}
                                                        placeholder="What happened? Why did you choose this path? What factors influenced your decision? What were the results?"
                                                        className="w-full h-32 bg-black border border-white/10 rounded-xl p-3 text-sm text-zinc-300 placeholder:text-zinc-700 focus:outline-none focus:ring-1 focus:ring-white/20 resize-none custom-scrollbar leading-relaxed"
                                                    />
                                                </div>

                                                <button
                                                    onClick={onConfirm}
                                                    disabled={!outcomeData.outcome || !outcomeData.variant}
                                                    className="w-full py-4 bg-white text-black hover:bg-zinc-200 disabled:bg-zinc-900 disabled:text-zinc-700 rounded-xl text-sm font-bold transition-all flex items-center justify-center gap-3 shadow-xl shadow-white/5 active:scale-[0.98]"
                                                >
                                                    <ArrowRight size={16} strokeWidth={2.5} />
                                                    Log Outcome
                                                </button>
                                            </div>
                                        </div>
                                    )}
                                </div>
                            </div>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </motion.div>
    );
};

const PathItem = ({ arg }) => {
    const [isOpen, setIsOpen] = useState(false);

    return (
        <div
            onClick={() => setIsOpen(!isOpen)}
            className="group/path cursor-pointer border border-white/5 hover:border-white/10 bg-white/[0.02] hover:bg-white/[0.04] rounded-xl transition-all duration-300"
        >
            <div className="p-4 flex items-center justify-between">
                <div className="flex items-center gap-3">
                    <div className="p-2 rounded-lg bg-indigo-500/10 text-indigo-400 group-hover/path:bg-indigo-500/20 group-hover/path:text-indigo-300 transition-colors">
                        <Tag size={16} />
                    </div>
                    <span className="text-sm font-bold text-zinc-300 group-hover/path:text-white transition-colors">{arg.variant_name}</span>
                </div>
                <ChevronDown
                    size={16}
                    className={cn(
                        "text-zinc-500 transition-transform duration-300",
                        isOpen ? "rotate-180 text-zinc-300" : ""
                    )}
                />
            </div>

            <AnimatePresence>
                {isOpen && (
                    <motion.div
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: 'auto', opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                        transition={{ duration: 0.2 }}
                    >
                        <div className="px-4 pb-4 pt-0">
                            <div className="pt-4 border-t border-white/5">
                                <p className="text-sm text-zinc-400 leading-relaxed whitespace-pre-wrap">
                                    {arg.text}
                                </p>
                            </div>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
};

export default HistoryView;
