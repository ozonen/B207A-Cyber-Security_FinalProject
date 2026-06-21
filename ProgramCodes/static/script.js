document.addEventListener("DOMContentLoaded", function () {
    var generateBtn = document.getElementById("generate-btn");
    if (generateBtn) {
        generateBtn.addEventListener("click", function () {
            fetch("/generate-password?length=16")
                .then(function (response) {
                    return response.json();
                })
                .then(function (data) {
                    document.getElementById("site_password").value = data.password;
                });
        });
    }

    document.querySelectorAll(".reveal-btn").forEach(function (button) {
        button.addEventListener("click", function () {
            var span = button.previousElementSibling;
            if (span.textContent === "••••••••") {
                span.textContent = span.getAttribute("data-password");
                button.textContent = "Hide";
            } else {
                span.textContent = "••••••••";
                button.textContent = "Show";
            }
        });
    });

    document.querySelectorAll(".copy-btn").forEach(function (button) {
        button.addEventListener("click", function () {
            var span = button.parentElement.querySelector(".password-value");
            navigator.clipboard.writeText(span.getAttribute("data-password")).then(function () {
                var original = button.textContent;
                button.textContent = "Copied";
                setTimeout(function () {
                    button.textContent = original;
                }, 1200);
            });
        });
    });
});
