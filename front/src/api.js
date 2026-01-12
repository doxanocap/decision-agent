import axios from 'axios';
import { getUserId } from './utils/userId';
import { retryWithBackoff, getErrorMessage } from './utils/retry';

const api = axios.create({
    baseURL: 'http://localhost:8000',
    timeout: 30000, // 30s timeout
});

// Add user_id to all requests
api.interceptors.request.use(config => {
    const userId = getUserId();
    config.headers['X-User-ID'] = userId;
    return config;
});

// Add response error interceptor
api.interceptors.response.use(
    response => response,
    error => {
        // Enhance error with user-friendly message
        error.userMessage = getErrorMessage(error);
        return Promise.reject(error);
    }
);

/**
 * Get decisions with retry
 */
export const getDecisions = async () => {
    return retryWithBackoff(
        async () => {
            const response = await api.get('/decisions');
            return response.data;
        },
        {
            maxAttempts: 3,
            onRetry: (attempt, error) => {
                console.log(`Retrying getDecisions (attempt ${attempt})...`);
            }
        }
    );
};

/**
 * Analyze decision with retry
 */
export const analyzeDecision = async (payload) => {
    return retryWithBackoff(
        async () => {
            const response = await api.post('/analysis/analyze', payload);
            return response.data;
        },
        {
            maxAttempts: 2, // Less retries for POST
            onRetry: (attempt, error) => {
                console.log(`Retrying analyzeDecision (attempt ${attempt})...`);
            }
        }
    );
};

/**
 * Poll analysis status (no retry - polling handles failures)
 */
export const pollAnalysisStatus = async (decisionId) => {
    const response = await api.get(`/analysis/${decisionId}/status`);
    return response.data;
};

/**
 * Update outcome with retry
 */
export const updateOutcome = async (id, payload) => {
    return retryWithBackoff(
        async () => {
            const response = await api.patch(`/decisions/${id}/outcome`, payload);
            return response.data;
        },
        {
            maxAttempts: 3,
            onRetry: (attempt, error) => {
                console.log(`Retrying updateOutcome (attempt ${attempt})...`);
            }
        }
    );
};

export default api;
