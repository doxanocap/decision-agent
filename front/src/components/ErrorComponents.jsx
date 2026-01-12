import React from 'react';
import { WifiOff, ServerCrash, AlertTriangle } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

/**
 * Offline Banner - Shows when internet connection is lost
 */
export const OfflineBanner = ({ isOnline }) => {
    return (
        <AnimatePresence>
            {!isOnline && (
                <motion.div
                    initial={{ y: -100, opacity: 0 }}
                    animate={{ y: 0, opacity: 1 }}
                    exit={{ y: -100, opacity: 0 }}
                    className="fixed top-0 left-0 right-0 z-50 bg-amber-500 text-black px-6 py-3 flex items-center justify-center gap-3 shadow-lg"
                >
                    <WifiOff size={20} strokeWidth={2} />
                    <span className="font-semibold">No internet connection. Some features may be unavailable.</span>
                </motion.div>
            )}
        </AnimatePresence>
    );
};

/**
 * Backend Unavailable Page
 */
export const BackendUnavailable = ({ onRetry }) => {
    return (
        <div className="min-h-screen bg-[#0a0a0a] flex items-center justify-center p-8">
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="max-w-md w-full space-y-8 text-center"
            >
                <div className="space-y-4">
                    <div className="flex justify-center">
                        <div className="p-6 bg-red-500/10 rounded-full border border-red-500/20">
                            <ServerCrash size={48} className="text-red-400" strokeWidth={1.5} />
                        </div>
                    </div>

                    <h1 className="text-3xl font-bold text-white">Service Unavailable</h1>

                    <p className="text-zinc-400 leading-relaxed">
                        We're having trouble connecting to our servers. This might be temporary.
                    </p>
                </div>

                <div className="space-y-4">
                    <button
                        onClick={onRetry}
                        className="w-full py-4 bg-white text-black rounded-xl font-semibold hover:bg-zinc-200 transition-colors"
                    >
                        Try Again
                    </button>

                    <div className="text-xs text-zinc-600 space-y-2">
                        <p>If the problem persists:</p>
                        <ul className="space-y-1">
                            <li>• Check your internet connection</li>
                            <li>• Make sure the backend server is running</li>
                            <li>• Try refreshing the page</li>
                        </ul>
                    </div>
                </div>
            </motion.div>
        </div>
    );
};

/**
 * Error Alert Component
 */
export const ErrorAlert = ({ error, onDismiss, onRetry }) => {
    if (!error) return null;

    return (
        <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="p-5 bg-red-500/5 border border-red-500/10 rounded-2xl"
        >
            <div className="flex items-start gap-4">
                <AlertTriangle size={20} className="text-red-400 mt-0.5 shrink-0" strokeWidth={1.5} />

                <div className="flex-1 space-y-3">
                    <p className="text-sm font-medium text-red-400">{error}</p>

                    {onRetry && (
                        <button
                            onClick={onRetry}
                            className="text-xs font-semibold text-red-300 hover:text-red-200 transition-colors"
                        >
                            Try again
                        </button>
                    )}
                </div>

                {onDismiss && (
                    <button
                        onClick={onDismiss}
                        className="text-zinc-600 hover:text-zinc-400 transition-colors"
                    >
                        ✕
                    </button>
                )}
            </div>
        </motion.div>
    );
};

/**
 * Connection Status Indicator (bottom-right corner)
 */
export const ConnectionStatus = ({ isOnline, isBackendHealthy }) => {
    if (isOnline && isBackendHealthy) return null;

    const status = !isOnline
        ? { label: 'Offline', color: 'bg-amber-500' }
        : { label: 'Server Down', color: 'bg-red-500' };

    return (
        <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            className="fixed bottom-6 right-6 z-40"
        >
            <div className="flex items-center gap-2 px-4 py-2 bg-zinc-900 border border-white/10 rounded-full shadow-lg">
                <div className={`w-2 h-2 rounded-full ${status.color} animate-pulse`} />
                <span className="text-xs font-semibold text-zinc-300">{status.label}</span>
            </div>
        </motion.div>
    );
};
