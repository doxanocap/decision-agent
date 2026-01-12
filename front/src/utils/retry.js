/**
 * Retry utility with exponential backoff
 */

/**
 * Sleep for specified milliseconds
 */
const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));

/**
 * Retry a function with exponential backoff
 * 
 * @param {Function} fn - Async function to retry
 * @param {Object} options - Retry options
 * @param {number} options.maxAttempts - Maximum retry attempts (default: 3)
 * @param {number} options.initialDelay - Initial delay in ms (default: 1000)
 * @param {number} options.maxDelay - Maximum delay in ms (default: 10000)
 * @param {Function} options.onRetry - Callback on retry (attempt, error)
 * @returns {Promise} Result of successful function call
 */
export async function retryWithBackoff(fn, options = {}) {
    const {
        maxAttempts = 3,
        initialDelay = 1000,
        maxDelay = 10000,
        onRetry = null
    } = options;

    let lastError;

    for (let attempt = 1; attempt <= maxAttempts; attempt++) {
        try {
            return await fn();
        } catch (error) {
            lastError = error;

            // Don't retry on client errors (4xx)
            if (error.response?.status >= 400 && error.response?.status < 500) {
                throw error;
            }

            // Last attempt - throw error
            if (attempt === maxAttempts) {
                throw error;
            }

            // Calculate delay with exponential backoff
            const delay = Math.min(
                initialDelay * Math.pow(2, attempt - 1),
                maxDelay
            );

            // Call retry callback
            if (onRetry) {
                onRetry(attempt, error, delay);
            }

            console.warn(`Retry attempt ${attempt}/${maxAttempts} after ${delay}ms`, error.message);

            await sleep(delay);
        }
    }

    throw lastError;
}

/**
 * Check if error is network-related
 */
export function isNetworkError(error) {
    return !error.response || error.code === 'ECONNABORTED' || error.message === 'Network Error';
}

/**
 * Get user-friendly error message
 */
export function getErrorMessage(error) {
    if (isNetworkError(error)) {
        return 'Unable to connect to server. Please check your internet connection.';
    }

    if (error.response) {
        const status = error.response.status;
        const detail = error.response.data?.detail;

        if (status === 400) {
            return detail || 'Invalid request. Please check your input.';
        }
        if (status === 401) {
            return 'Authentication required. Please refresh the page.';
        }
        if (status === 403) {
            return 'Access denied. You don\'t have permission for this action.';
        }
        if (status === 404) {
            return 'Resource not found.';
        }
        if (status === 429) {
            return 'Too many requests. Please try again later.';
        }
        if (status >= 500) {
            return 'Server error. Our team has been notified.';
        }

        if (status === 422) {
            if (Array.isArray(detail)) {
                return detail.map(err => err.msg).join(', ');
            }
            if (typeof detail === 'object') {
                return JSON.stringify(detail);
            }
            return detail || 'Validation error. Please check your input.';
        }

        if (typeof detail === 'object') {
            return JSON.stringify(detail);
        }

        return detail || 'An unexpected error occurred.';
    }

    return error.message || 'An unexpected error occurred.';
}
