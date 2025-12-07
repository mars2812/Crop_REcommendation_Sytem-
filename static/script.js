document.addEventListener("DOMContentLoaded", function () { 
    let form = document.querySelector("form");

    // Prevent multiple submissions & show confirmation message
    form.addEventListener("submit", function (event) {
        if (form.classList.contains("submitted")) {
            event.preventDefault();
            alert("Your request is already being processed!");
        } else {
            form.classList.add("submitted");
            alert("Your crop prediction request has been submitted successfully!");
        }
    });

    // Ripple Effect for Buttons
    document.querySelectorAll("button").forEach(button => {
        button.addEventListener("click", function (e) {
            let ripple = document.createElement("span");
            ripple.classList.add("ripple");

            let rect = this.getBoundingClientRect();
            let x = e.clientX - rect.left;
            let y = e.clientY - rect.top;

            ripple.style.left = `${x}px`;
            ripple.style.top = `${y}px`;

            this.appendChild(ripple);

            setTimeout(() => {
                ripple.remove();
            }, 600);
        });
    });

    // Smooth Flip Animation for Result Box
    let resultBox = document.querySelector(".result-container");
    if (resultBox) {
        setTimeout(() => {
            resultBox.classList.add("show");
        }, 700); // Slight delay for a better visual effect
    }

    // Scroll Animation for Elements (Fade-in Effect)
    let hiddenElements = document.querySelectorAll(".hidden");

    function revealOnScroll() {
        hiddenElements.forEach(el => {
            let position = el.getBoundingClientRect().top;
            if (position < window.innerHeight - 100) {
                el.classList.add("show");
            }
        });
    }

    window.addEventListener("scroll", revealOnScroll);
    revealOnScroll(); // Run on load

    // Add a loading animation before showing results
    let predictButton = document.querySelector("form button");
    if (predictButton) {
        predictButton.addEventListener("click", function () {
            this.innerHTML = "Processing...";
            setTimeout(() => {
                this.innerHTML = "Predict";
            }, 2000);
        });
    }
});
