document.querySelectorAll(".imageCheckbox").forEach(function(checkbox) {
    checkbox.addEventListener("change", function() {
        var img = checkbox.previousElementSibling;
        if (checkbox.checked) {
            img.style.border = "2px solid blue"; // Visual indication of selection
        } else {
            img.style.border = "none";
        }
    });
});

document.getElementById("submitBtn").addEventListener("click", function() {
    var selectedImages = [];
    var checkboxes = document.querySelectorAll('.imageCheckbox:checked');
    checkboxes.forEach(function(checkbox) {
        selectedImages.push(checkbox.value);
    });
    // Send selectedImages to backend (e.g., using fetch)
    console.log(selectedImages); // Just for demonstration
    var submissionMessage = "Number of images submitted: " + checkboxes.length;
    alert(submissionMessage);
});
