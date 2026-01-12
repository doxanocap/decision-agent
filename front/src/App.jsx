import React, { useState } from 'react';
import { PencilLine, History as HistoryIcon, LayoutDashboard } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { cn } from './utils/cn';
import NewDecision from './components/NewDecision';
import HistoryView from './components/History';
import { useOnlineStatus, useBackendHealth } from './hooks/useConnection';
import { OfflineBanner, BackendUnavailable, ConnectionStatus } from './components/ErrorComponents';

const NAV_ITEMS = [
  { id: 'new', label: 'New Decision', icon: PencilLine },
  { id: 'history', label: 'History', icon: HistoryIcon },
];

function App() {
  const [activePage, setActivePage] = useState('new');
  const isOnline = useOnlineStatus();
  const { isHealthy: isBackendHealthy } = useBackendHealth();

  // Show backend unavailable page if offline or backend down
  if (!isOnline || !isBackendHealthy) {
    return (
      <>
        <OfflineBanner isOnline={isOnline} />
        <BackendUnavailable onRetry={() => window.location.reload()} />
      </>
    );
  }

  return (
    <div className="flex h-screen bg-[#0a0a0a] text-zinc-100 font-sans selection:bg-indigo-500/30 overflow-hidden">
      {/* Offline Banner */}
      <OfflineBanner isOnline={isOnline} />

      {/* Connection Status Indicator */}
      <ConnectionStatus isOnline={isOnline} isBackendHealthy={isBackendHealthy} />

      {/* Sidebar */}
      <aside className="w-72 border-r border-white/5 bg-[#0f0f0f] flex flex-col shrink-0">
        <div className="p-8">
          <div className="flex items-center gap-4 mb-12">
            <span className="text-4xl">🔬</span>
            <div>
              <h1 className="text-2xl font-bold tracking-tight">Decisions</h1>
              <p className="text-xs text-zinc-500 font-medium mt-1">AI Decision Analysis</p>
            </div>
          </div>

          <nav className="space-y-2">
            {NAV_ITEMS.map((item) => {
              const Icon = item.icon;
              const isActive = activePage === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => setActivePage(item.id)}
                  className={cn(
                    "w-full flex items-center gap-4 px-4 py-3 rounded-xl transition-all duration-200 group text-sm font-medium",
                    isActive
                      ? "bg-white/10 text-white shadow-sm"
                      : "text-zinc-500 hover:text-zinc-200 hover:bg-white/5"
                  )}
                >
                  <Icon size={20} strokeWidth={1.5} className={cn(isActive ? "text-indigo-400" : "group-hover:text-zinc-200")} />
                  <span>{item.label}</span>
                </button>
              );
            })}
          </nav>
        </div>

        <div className="mt-auto p-8 border-t border-white/5 space-y-4">
          <div className="flex items-center gap-4 px-4 py-2 text-zinc-500 text-xs">
            <div className="w-2 h-2 rounded-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)]" />
            <span className="font-medium tracking-wide">SYSTEM ONLINE</span>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-y-auto custom-scrollbar bg-[#0a0a0a]">
        <div className="max-w-4xl mx-auto px-8 py-16 lg:px-12">
          <AnimatePresence mode="wait">
            <motion.div
              key={activePage}
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -16 }}
              transition={{ duration: 0.3, ease: 'easeOut' }}
            >
              {activePage === 'new' ? <NewDecision /> : <HistoryView />}
            </motion.div>
          </AnimatePresence>
        </div>
      </main>
    </div>
  );
}

export default App;
