// ==========================================
// Escape HTML
// ==========================================

function escapeHtml(text) {

    const div = document.createElement("div");

    div.textContent = text;

    return div.innerHTML;

}

// ==========================================
// Scroll
// ==========================================

function scrollToBottom() {

    const container =
        document.getElementById(
            "chat-container"
        );

    if (!container) return;

    container.scrollTop =
        container.scrollHeight;

}

// ==========================================
// DOM Helpers
// ==========================================

function clearElement(element) {

    element.innerHTML = "";

}

function createElement(
    tag,
    className = ""
) {

    const element =
        document.createElement(tag);

    if (className) {

        element.className =
            className;

    }

    return element;

}

// ==========================================
// Date
// ==========================================

function formatDate(dateString) {

    return new Date(dateString)
        .toLocaleString();

}

// ==========================================
// Toast Notification
// ==========================================

function showToast(
    message,
    type = "success"
) {

    let container =
        document.getElementById(
            "toast-container"
        );

    if (!container) {

        container =
            document.createElement("div");

        container.id =
            "toast-container";

        container.style.position =
            "fixed";

        container.style.top =
            "20px";

        container.style.right =
            "20px";

        container.style.zIndex =
            "9999";

        container.style.display =
            "flex";

        container.style.flexDirection =
            "column";

        container.style.gap =
            "12px";

        document.body.appendChild(
            container
        );

    }

    const toast =
        document.createElement("div");

    toast.textContent =
        message;

    toast.style.padding =
        "14px 18px";

    toast.style.borderRadius =
        "12px";

    toast.style.minWidth =
        "260px";

    toast.style.color =
        "white";

    toast.style.boxShadow =
        "0 8px 25px rgba(0,0,0,.35)";

    toast.style.fontWeight =
        "500";

    toast.style.opacity =
        "0";

    toast.style.transform =
        "translateX(20px)";

    toast.style.transition =
        "all .25s ease";

    toast.style.background =
        type === "success"
            ? "#10a37f"
            : "#d9534f";

    container.appendChild(
        toast
    );

    requestAnimationFrame(() => {

        toast.style.opacity = "1";

        toast.style.transform =
            "translateX(0)";

    });

    setTimeout(() => {

        toast.style.opacity = "0";

        toast.style.transform =
            "translateX(20px)";

        setTimeout(() => {

            toast.remove();

        }, 250);

    }, 3000);

}

// ==========================================
// Success
// ==========================================

function showSuccess(message) {

    showToast(
        message,
        "success"
    );

}

// ==========================================
// Error
// ==========================================

function showError(message) {

    showToast(
        message,
        "error"
    );

}