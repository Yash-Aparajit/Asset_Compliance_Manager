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

