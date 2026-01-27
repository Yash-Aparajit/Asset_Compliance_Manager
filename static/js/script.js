document.addEventListener("DOMContentLoaded", () => {
    // =====================================================
    // 1) IMPORT PREVIEW MODAL (Asset Import Page)
    // =====================================================
    const modal = document.getElementById("importPreviewModal");
    const closeBtns = document.querySelectorAll("[data-close-modal]");

    if (modal) {
        modal.classList.add("active");
        document.body.style.overflow = "hidden";
    }

    closeBtns.forEach((btn) => {
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

    // =====================================================
    // 2) AMC DOCUMENT TYPE: "OTHER" FIELD SHOW/HIDE
    // =====================================================
    const docTypeSelect = document.getElementById("document_type");
    const otherGroup = document.getElementById("other_doc_group");
    const otherInput = document.getElementById("other_document_type");

    if (docTypeSelect && otherGroup && otherInput) {
        docTypeSelect.addEventListener("change", () => {
            const isOther = docTypeSelect.value === "Other";
            otherGroup.style.display = isOther ? "block" : "none";
            otherInput.required = isOther;

            if (!isOther) {
                otherInput.value = "";
            }
        });

        if (docTypeSelect.form) {
            docTypeSelect.form.addEventListener("submit", () => {
                if (docTypeSelect.value === "Other" && otherInput.value.trim()) {
                    docTypeSelect.value = otherInput.value.trim();
                }
            });
        }
    }

    // =====================================================
    // 3) HAMBURGER MENU (Navbar)
    // =====================================================
    const menu = document.getElementById("hamburgerMenu");
    const button = document.querySelector(".hamburger"); 

    function closeMenu() {
        if (menu) menu.style.display = "none";
    }

    function toggleMenu() {
        if (!menu) return;

        const isOpen = menu.style.display === "block";
        menu.style.display = isOpen ? "none" : "block";
    }

    window.toggleMenu = toggleMenu;

    document.addEventListener("click", (e) => {
        if (!menu || !button) return;

        if (!menu.contains(e.target) && !button.contains(e.target)) {
            closeMenu();
        }
    });

    document.addEventListener("keydown", (e) => {
        if (e.key === "Escape") closeMenu();
    });
});
