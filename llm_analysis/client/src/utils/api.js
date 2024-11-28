export const handleApiError = (error) => {
    if (!error.response) {
        // Network error or server not running
        return {
            success: false,
            error: "Cannot connect to server. Please ensure the backend is running.",
        };
    }
    // Handle other types of errors...
    return {
        success: false,
        error: error.message,
    };
};

// Example usage in your API calls:
export const analyzeData = async (data) => {
    try {
        const response = await fetch('/api/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        return handleApiError(error);
    }
}; 