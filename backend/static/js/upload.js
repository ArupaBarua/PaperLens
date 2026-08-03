// =========================================
// Initialize
// =========================================

function initializeUpload() {

    const modal =
        document.getElementById(
            "upload-modal"
        );

    const uploadButton =
        document.getElementById(
            "upload-paper-btn"
        );

    const closeButton =
        document.getElementById(
            "close-upload-modal"
        );

    const cancelButton =
        document.getElementById(
            "cancel-upload"
        );

    const confirmButton =
        document.getElementById(
            "confirm-upload"
        );

    const fileInput =
        document.getElementById(
            "paper-file"
        );

    const dropZone =
        document.querySelector(
            ".upload-drop-zone"
        );

    uploadButton.addEventListener(
        "click",
        openUploadModal
    );

    closeButton.addEventListener(
        "click",
        closeUploadModal
    );

    cancelButton.addEventListener(
        "click",
        closeUploadModal
    );

    confirmButton.addEventListener(
        "click",
        uploadPaper
    );

    fileInput.addEventListener(
        "change",
        updateSelectedFile
    );

    modal.addEventListener(
        "click",
        event => {

            if (
                event.target === modal
            ) {

                closeUploadModal();

            }

        }
    );

    // Drag & Drop

    dropZone.addEventListener(
        "dragover",
        event => {

            event.preventDefault();

            dropZone.style.borderColor =
                "var(--primary-color)";

        }
    );

    dropZone.addEventListener(
        "dragleave",
        () => {

            dropZone.style.borderColor =
                "";

        }
    );

    dropZone.addEventListener(
        "drop",
        event => {

            event.preventDefault();

            dropZone.style.borderColor =
                "";

            fileInput.files =
                event.dataTransfer.files;

            updateSelectedFile();

        }
    );

}

// =========================================
// Open
// =========================================

async function openUploadModal() {

    try {

        await ensureSession();

    }
    catch (error) {

        showError(
            error.message
        );

        return;

    }

    document
        .getElementById(
            "upload-modal"
        )
        .classList.remove(
            "hidden"
        );

}

// =========================================
// Close
// =========================================

function closeUploadModal() {

    document
        .getElementById(
            "upload-modal"
        )
        .classList.add(
            "hidden"
        );

    const input =
        document.getElementById(
            "paper-file"
        );

    input.value = "";

    resetDropZone();

}

// =========================================
// Update filename
// =========================================

function updateSelectedFile() {

    const input =
        document.getElementById(
            "paper-file"
        );

    const title =
        document.querySelector(
            ".upload-title"
        );

    const subtitle =
        document.querySelector(
            ".upload-subtitle"
        );

    if (
        input.files.length === 0
    ) {

        resetDropZone();

        return;

    }

    title.textContent =
        input.files[0].name;

    subtitle.textContent =
        "Ready to upload";

}

// =========================================
// Reset
// =========================================

function resetDropZone() {

    document.querySelector(
        ".upload-title"
    ).textContent =
        "Click to choose a PDF";

    document.querySelector(
        ".upload-subtitle"
    ).textContent =
        "or drag and drop it here";

}

// =========================================
// Upload
// =========================================

async function uploadPaper() {

    const input =
        document.getElementById(
            "paper-file"
        );

    if (input.files.length === 0) {

        showError(
            "Select a PDF first."
        );

        return;

    }

    try {

        console.log("STEP 1");

        const response =
            await API.uploadPaper(
                appState.currentSessionId,
                input.files[0]
            );

        console.log("STEP 2", response);

        appState.uploadedPapers =
            await API.getPapers(
                appState.currentSessionId
            );

        console.log("STEP 3", appState.uploadedPapers);

        renderPaperList(
            appState.uploadedPapers
        );

        console.log("STEP 4");

        closeUploadModal();

        console.log("STEP 5");

        showSuccess(
            response.message
        );

        console.log("STEP 6");

    }

    catch (error) {

        console.error(error);

        showError(error.message);

    }

}