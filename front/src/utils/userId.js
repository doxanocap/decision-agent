/**
 * User ID Management
 * 
 * Generates and persists a unique user ID in localStorage.
 * This ties the user to their browser for MVP auth.
 */

const USER_ID_KEY = 'decisions_user_id';

/**
 * Generate a UUID v4
 */
function generateUUID() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
        const r = Math.random() * 16 | 0;
        const v = c === 'x' ? r : (r & 0x3 | 0x8);
        return v.toString(16);
    });
}

/**
 * Get or create user ID
 * 
 * @returns {string} User UUID
 */
export function getUserId() {
    let userId = localStorage.getItem(USER_ID_KEY);

    if (!userId) {
        userId = generateUUID();
        localStorage.setItem(USER_ID_KEY, userId);
        console.log('🆔 New user ID generated:', userId);
    }

    return userId;
}

/**
 * Clear user ID (for testing/reset)
 */
export function clearUserId() {
    localStorage.removeItem(USER_ID_KEY);
    console.log('🗑️ User ID cleared');
}

/**
 * Check if user ID exists
 */
export function hasUserId() {
    return !!localStorage.getItem(USER_ID_KEY);
}
