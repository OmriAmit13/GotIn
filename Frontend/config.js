async function loadConfig() {
    try {
        const response = await fetch('../config.json');
        if (!response.ok) throw new Error('Failed to load config');
        return await response.json();
    } catch (error) {
        console.error('Error loading config:', error);
        // Fallback configuration
        return {
            ports: {
                hebrew_university: 3002,
                technion: 3003,
                bgu: 3001,
                tel_aviv: 3004
            }
        };
    }
}
