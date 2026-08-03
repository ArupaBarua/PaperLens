// =========================================
// Global Application State
// =========================================

const appState = {

    currentSessionId: null,

    sessions: [],

    uploadedPapers: [],

    isWaitingForResponse: false,

    isNewSession: false

};

// =========================================
// Application Startup
// =========================================

document.addEventListener(
    "DOMContentLoaded",
    initializeApp
);

async function initializeApp() {

    try {

        initializeSidebar();

        initializeChat();

        initializeUpload();

        await loadSessions();

    }

    catch (error) {

        console.error(error);

        showError(
            "Failed to initialize PaperLens."
        );

    }

}

// =========================================
// Load Sessions
// =========================================

async function loadSessions() {

    appState.sessions =
        await API.getSessions();

    renderSessionList(
        appState.sessions
    );

    // Don't automatically open the first session.
    // Leave the welcome screen visible.

}

// =========================================
// Refresh Papers
// =========================================

async function refreshPapers() {

    if (
        appState.currentSessionId === null
    ) {

        renderPaperList([]);

        return;

    }

    appState.uploadedPapers =
        await API.getPapers(
            appState.currentSessionId
        );

    renderPaperList(
        appState.uploadedPapers
    );

}

// =========================================
// Refresh Messages
// =========================================

async function refreshMessages() {

    if (
        appState.currentSessionId === null
    ) {

        return;

    }

    const messages =
        await API.getMessages(
            appState.currentSessionId
        );

    renderMessages(
        messages
    );

}

// =========================================
// Reset Chat Window
// =========================================

function showWelcomeScreen() {

    document
        .getElementById(
            "chat-container"
        )
        .innerHTML = `

        <div class="welcome">

            <h1>
                Welcome to PaperLens!
            </h1>

            <p>
                Upload research papers and ask questions about them.
            </p>

        </div>

    `;

}


async function ensureSession() {

    console.log("Before:", appState.currentSessionId);

    if (appState.currentSessionId !== null) {

        console.log("Returning early");

        return;

    }

    console.log("Creating session");

    const session = await API.createSession("New Chat");

    console.log("Created:", session.id);

    appState.sessions.unshift(session);

    renderSessionList(appState.sessions);

    appState.currentSessionId = session.id;

    appState.isNewSession = true;

    console.log("After:", appState.currentSessionId);
    console.log("isNewSession:", appState.isNewSession);

    highlightSession(session.id);

    renderPaperList([]);
}