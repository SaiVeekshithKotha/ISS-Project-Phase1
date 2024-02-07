document.addEventListener("DOMContentLoaded", () => {
    const dropContainer = document.getElementById("dropContainer");
    const fileInput = document.getElementById("fileInput");
    const previewContainer = document.getElementById("previewContainer");

    dropContainer.addEventListener("dragover", (e) => {
        e.preventDefault();
        dropContainer.classList.add("drag-over");
    });

    dropContainer.addEventListener("dragleave", () => {
        dropContainer.classList.remove("drag-over");
    });

    dropContainer.addEventListener("drop", (e) => {
        e.preventDefault();
        dropContainer.classList.remove("drag-over");

        const files = e.dataTransfer.files;
        handleFiles(files);
    });

    fileInput.addEventListener("change", () => {
        const files = fileInput.files;
        handleFiles(files);
    });

    function handleFiles(files) {
        for (const file of files) {
            if (file.type.startsWith("image/")) {
                const reader = new FileReader();

                reader.onload = function (e) {
                    const image = new Image();
                    image.src = e.target.result;

                    const previewImage = document.createElement("div");
                    previewImage.classList.add("preview-image");
                    previewImage.style.backgroundImage = `url('${e.target.result}')`;
                    previewContainer.appendChild(previewImage);
                };

                reader.readAsDataURL(file);
            }
        }
    }
});
