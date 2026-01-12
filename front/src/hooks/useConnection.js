import { useState, useEffect } from 'react';

/**
 * Hook to monitor online/offline status
 */
export function useOnlineStatus() {
    const [isOnline, setIsOnline] = useState(navigator.onLine);

    useEffect(() => {
        const handleOnline = () => setIsOnline(true);
        const handleOffline = () => setIsOnline(false);

        window.addEventListener('online', handleOnline);
        window.addEventListener('offline', handleOffline);

        return () => {
            window.removeEventListener('online', handleOnline);
            window.removeEventListener('offline', handleOffline);
        };
    }, []);

    return isOnline;
}

/**
 * Hook to check backend health
 */
export function useBackendHealth(checkInterval = 30000) {
    const [isHealthy, setIsHealthy] = useState(true);
    const [lastCheck, setLastCheck] = useState(null);

    useEffect(() => {
        const checkHealth = async () => {
            try {
                const response = await fetch('http://localhost:8000/health', {
                    method: 'GET',
                    signal: AbortSignal.timeout(5000) // 5s timeout
                });
                setIsHealthy(response.ok);
                setLastCheck(new Date());
            } catch (error) {
                setIsHealthy(false);
                setLastCheck(new Date());
            }
        };

        // Check immediately
        checkHealth();

        // Then check periodically
        const interval = setInterval(checkHealth, checkInterval);

        return () => clearInterval(interval);
    }, [checkInterval]);

    return { isHealthy, lastCheck };
}
