// =========================================
// Initialize Chat
// =========================================

function initializeChat() {

    const input =
        document.getElementById(
            "message-input"
        );

    const sendButton =
        document.getElementById(
            "send-btn"
        );

    sendButton.addEventListener(
        "click",
        sendMessage
    );

    input.addEventListener(
        "keydown",
        event => {

            if (
                event.key === "Enter" &&
                !event.shiftKey
            ) {

                event.preventDefault();

                sendMessage();

            }

        }
    );

    input.addEventListener(
        "input",
        autoResizeTextarea
    );

}

// =========================================
// Auto Resize
// =========================================

function autoResizeTextarea() {

    const textarea =
        document.getElementById(
            "message-input"
        );

    textarea.style.height = "auto";

    textarea.style.height =
        textarea.scrollHeight + "px";

}

// =========================================
// Send Message
// =========================================

async function sendMessage() {

    // Automatically create a session if none exists
    if (appState.currentSessionId === null) {

        try {

            const session =
                await API.createSession(
                    "New Chat"
                );

            appState.sessions.unshift(
                session
            );

            renderSessionList(
                appState.sessions
            );

            appState.currentSessionId =
                session.id;

            highlightSession(
                session.id
            );

            showWelcomeScreen();

        }

        catch (error) {

            showError(
                error.message
            );

            return;

        }

    }

    if (
        appState.isWaitingForResponse
    ) {

        return;

    }

    const input =
        document.getElementById(
            "message-input"
        );

    const message =
        input.value.trim();

    if (message === "") {

        return;

    }

    input.value = "";

    input.style.height = "48px";

    addMessageToUI(
        "user",
        message
    );

    showTypingIndicator();

    appState.isWaitingForResponse = true;

    try {

        const response =
            await API.sendMessage(
                appState.currentSessionId,
                message
            );

        removeTypingIndicator();

        addMessageToUI(
            "assistant",
            response.content
        );

    }

    catch (error) {

        removeTypingIndicator();

        showError(
            error.message
        );

    }

    finally {

        appState.isWaitingForResponse = false;

    }

}

// =========================================
// Render Messages
// =========================================

function renderMessages(messages) {

    const container =
        document.getElementById(
            "chat-container"
        );

    if (messages.length === 0) {

        showWelcomeScreen();

        return;

    }

    container.innerHTML = "";

    messages.forEach(message => {

        addMessageToUI(
            message.role,
            message.content,
            false
        );

    });

}

// =========================================
// Add Message
// =========================================

function addMessageToUI(
    role,
    content,
    scroll = true
) {

    const container =
        document.getElementById(
            "chat-container"
        );

    const wrapper =
        document.createElement(
            "div"
        );

    wrapper.className =
        `message ${role}`;

    const bubble =
        document.createElement(
            "div"
        );

    bubble.className =
        "message-bubble";

    bubble.innerHTML =
        renderMarkdown(
            content
        );

    wrapper.appendChild(
        bubble
    );

    container.appendChild(
        wrapper
    );

    if (scroll) {

        scrollToBottom();

    }

}

// =========================================
// Typing Indicator
// =========================================

function showTypingIndicator() {

    const container =
        document.getElementById(
            "chat-container"
        );

    const typing =
        document.createElement(
            "div"
        );

    typing.id =
        "typing-indicator";

    typing.className =
        "message assistant";

    typing.innerHTML = `

        <div class="typing">

            <span></span>

            <span></span>

            <span></span>

        </div>

    `;

    container.appendChild(
        typing
    );

    scrollToBottom();

}

function removeTypingIndicator() {

    const typing =
        document.getElementById(
            "typing-indicator"
        );

    if (typing) {

        typing.remove();

    }

}

// =========================================
// Scroll
// =========================================

function scrollToBottom() {

    const container =
        document.getElementById(
            "chat-container"
        );

    container.scrollTop =
        container.scrollHeight;

}