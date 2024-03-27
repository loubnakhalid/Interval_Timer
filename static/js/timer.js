const startButton = document.getElementById("start");
const pauseForm = document.getElementById("pause-form");
const pauseButton = document.getElementById("pause-button");
const startForm = document.getElementById("start-form");

startButton.addEventListener("click", function(event) {
    event.preventDefault();
    pauseForm.style.display = "block";
    startForm.style.display = "none";
});

pauseButton.addEventListener("click", function(event) {
    event.preventDefault();
    startForm.style.display = "block";
    pauseForm.style.display = "none";
});