const API_BASE_URL = "";

async function request(endpoint, options = {}) {

    const response = await fetch(
        `${API_BASE_URL}${endpoint}`,
        options
    );

    if (!response.ok) {

        let message = "Request failed.";

        try {

            const error = await response.json();

            message = error.detail ?? message;

        }
        catch (e) {}

        throw new Error(message);

    }

    if (response.status === 204) {

        return null;

    }

    return response.json();

}

const API = {

    // ===========================
    // Sessions
    // ===========================

    async createSession(title) {

        return request("/sessions/", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                title
            })

        });

    },

    async getSessions() {

        return request("/sessions/");

    },

    async getSession(sessionId) {

        return request(`/sessions/${sessionId}`);

    },

    async renameSession(sessionId, title) {

        return request(`/sessions/${sessionId}`, {

            method: "PUT",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                title
            })

        });

    },

    async deleteSession(sessionId) {

        return request(`/sessions/${sessionId}`, {

            method: "DELETE"

        });

    },

    // ===========================
    // Papers
    // ===========================

    async uploadPaper(sessionId, file) {

        const formData = new FormData();

        formData.append(
            "file",
            file
        );

        return request(`/upload/${sessionId}`, {

            method: "POST",

            body: formData

        });

    },

    async getPapers(sessionId) {

        return request(`/upload/${sessionId}`);

    },

    async deletePaper(paperId) {

        return request(`/upload/${paperId}`, {

            method: "DELETE"

        });

    },

    // ===========================
    // Chat
    // ===========================

    async sendMessage(sessionId, content) {

        return request(`/chat/${sessionId}`, {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                content
            })

        });

    },

    async getMessages(sessionId) {

        return request(`/chat/${sessionId}/messages`);

    }

};