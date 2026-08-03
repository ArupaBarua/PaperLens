// =========================
// Initialize
// =========================

function initializeSidebar() {

    document
        .getElementById("new-chat-btn")
        .addEventListener(
            "click",
            createNewChat
        );

    document
        .getElementById("session-search")
        .addEventListener(
            "input",
            searchSessions
        );

}

// =========================
// Create New Chat
// =========================

async function createNewChat() {

    console.log("New Chat clicked");

    appState.currentSessionId = null;
    appState.isNewSession = false;

    console.log("currentSessionId =", appState.currentSessionId);

    highlightSession(-1);

    renderPaperList([]);

    showWelcomeScreen();
}

// =========================
// Select Session
// =========================

async function selectSession(
    sessionId
) {

    appState.currentSessionId =
        sessionId;

    highlightSession(
        sessionId
    );

    appState.uploadedPapers =
        await API.getPapers(
            sessionId
        );

    renderPaperList(
        appState.uploadedPapers
    );

    const messages =
        await API.getMessages(
            sessionId
        );

    renderMessages(
        messages
    );

}

// =========================
// Render Sessions
// =========================

function renderSessionList(
    sessions
) {

    const container =
        document.getElementById(
            "session-list"
        );

    container.innerHTML = "";

    sessions.forEach(session => {

        const item =
            document.createElement(
                "div"
            );

        item.className =
            "session-item";

        item.dataset.id =
            session.id;

        item.innerHTML = `

            <span class="session-title">

                ${session.title}

            </span>

            <button
                class="session-delete"
            >
                🗑
            </button>

        `;

        item.onclick = () =>
            selectSession(
                session.id
            );

        item
            .querySelector(
                ".session-delete"
            )
            .onclick = async (event) => {

                event.stopPropagation();

                if (
                    confirm(
                        "Delete this chat?"
                    )
                ) {

                    await deleteSession(
                        session.id
                    );

                }

            };

        container.appendChild(
            item
        );

    });

}

// =========================
// Highlight Active Session
// =========================

function highlightSession(
    sessionId
) {

    document
        .querySelectorAll(
            ".session-item"
        )
        .forEach(item => {

            item.classList.remove(
                "active"
            );

            if (
                Number(
                    item.dataset.id
                ) === sessionId
            ) {

                item.classList.add(
                    "active"
                );

            }

        });

}

// =========================
// Delete Session
// =========================

async function deleteSession(
    sessionId
) {

    try {

        await API.deleteSession(
            sessionId
        );

        appState.sessions =
            appState.sessions.filter(
                session =>
                    session.id !== sessionId
            );

        renderSessionList(
            appState.sessions
        );

        if (
            appState.currentSessionId === sessionId
        ) {

            appState.currentSessionId = null;

            showWelcomeScreen();

        }

    }

    catch (error) {

        showError(
            error.message
        );

    }

}

// =========================
// Search
// =========================

function searchSessions() {

    const keyword =
        document
            .getElementById(
                "session-search"
            )
            .value
            .toLowerCase();

    const filtered =
        appState.sessions.filter(
            session =>
                session.title
                    .toLowerCase()
                    .includes(
                        keyword
                    )
        );

    renderSessionList(
        filtered
    );

}

// =========================
// Papers
// =========================

function renderPaperList(
    papers
) {

    const container =
        document.getElementById(
            "paper-list"
        );

    container.innerHTML = "";

    papers.forEach(
        paper => {

            const item =
                document.createElement(
                    "div"
                );

            item.className =
                "paper-item";

            item.innerHTML = `

                <span class="paper-name">

                    📄 ${paper.filename}

                </span>

            `;

            container.appendChild(
                item
            );

        }
    );

}