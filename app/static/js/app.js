document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll(".flash").forEach((el) => {
        setTimeout(() => {
            el.classList.add("hide");
            setTimeout(() => el.remove(), 400);
        }, 4500);
    });

    document.querySelectorAll("input, textarea, select").forEach((field) => {
        field.addEventListener("focus", () => field.closest("label")?.classList.add("focused"));
        field.addEventListener("blur", () => field.closest("label")?.classList.remove("focused"));
    });
});
