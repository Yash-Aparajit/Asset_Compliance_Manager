document.addEventListener("DOMContentLoaded", () => {
    console.log("IMPORT MODAL SCRIPT LOADED");

    const modal = document.getElementById("importPreviewModal");
    const closeBtns = document.querySelectorAll("[data-close-modal]");

    if (modal) {
        console.log("IMPORT MODAL FOUND → OPENING");
        modal.classList.add("active");
        document.body.style.overflow = "hidden";
    }

    closeBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            modal.classList.remove("active");
            document.body.style.overflow = "";
        });
    });

    document.addEventListener("keydown", (e) => {
        if (e.key === "Escape" && modal?.classList.contains("active")) {
            modal.classList.remove("active");
            document.body.style.overflow = "";
        }
    });
});

document.addEventListener("DOMContentLoaded", () => {
    const docTypeSelect = document.getElementById("document_type");
    const otherGroup = document.getElementById("other_doc_group");
    const otherInput = document.getElementById("other_document_type");

    if (!docTypeSelect) return;

    docTypeSelect.addEventListener("change", () => {
        if (docTypeSelect.value === "Other") {
            otherGroup.style.display = "block";
            otherInput.required = true;
        } else {
            otherGroup.style.display = "none";
            otherInput.required = false;
            otherInput.value = "";
        }
    });

    // Before submit → override value cleanly
    docTypeSelect.form.addEventListener("submit", () => {
        if (docTypeSelect.value === "Other" && otherInput.value.trim()) {
            docTypeSelect.value = otherInput.value.trim();
        }
    });
});
