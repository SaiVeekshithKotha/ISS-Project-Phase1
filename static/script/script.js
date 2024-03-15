function selectImages() {
    var selectedImages = document.querySelectorAll('.image-checkbox:checked');
    var selectedImagesDiv = document.getElementById('selected-images');
    selectedImagesDiv.innerHTML = '';

    selectedImages.forEach(function (image) {
        var imgElement = document.createElement('img');
        imgElement.src = image.value;
        imgElement.classList.add('selected-image');
        selectedImagesDiv.appendChild(imgElement);
    });
}

var username = "{{ userName }}";
console.log(username) ;

function handleDragOver(event) {
    event.preventDefault();
    event.dataTransfer.dropEffect = 'copy';
    event.target.classList.add('dragover');
}

function handleDrop(event) {
    event.preventDefault();
    event.target.classList.remove('dragover');
    var files = event.dataTransfer.files;
    handleFiles(files);
}


function openFileSelector() {
    document.getElementById('file-input').click();
}


function handleFiles(files) {
    var filename = files.length;
    document.getElementById("filename").innerText = filename;
    uploadFiles(files, username);
}


function uploadFiles(files, username) {
    var form = new FormData();

    for (var i = 0; i < files.length; i++) {
        form.append('images', files[i]);
    }

    form.append('username', username);
    var xhr = new XMLHttpRequest();
    xhr.open('POST', '/upload', true);
    xhr.onload = function () {
        if (xhr.status === 200) {
            displayUploadedImages();
        } else {
            alert('Error uploading images. Please try again.');
        }
    };
    xhr.send(form);
}

function displayUploadedImages() {
    var uploadedImagesDiv = document.getElementById('uploaded-images');
    uploadedImagesDiv.innerHTML = '';  // Clear previous content

    var xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function () {
        if (xhr.readyState == 4) {
            if (xhr.status === 200) {
                var images = xhr.response.images;
                if (images) {
                    images.forEach(function (imageData) {
                        var imageFormat = imageData.format;
                        var imageBlob = new Blob([base64ToArrayBuffer(imageData.data)], { type: 'image/' + imageFormat });

                        var imgElement = document.createElement('img');
                        imgElement.src = URL.createObjectURL(imageBlob);
                        imgElement.classList.add('uploaded-image');  // Apply any additional styling

                        // var checkbox = document.createElement('input');
                        // checkbox.type = 'checkbox';
                        // checkbox.name = 'selected-images';
                        // checkbox.value = imgElement.src;
                        // checkbox.classList.add('image-checkbox');

                        var container = document.createElement('div');
                        container.classList.add('uploaded-image-container');
                        // container.appendChild(checkbox);
                        container.appendChild(imgElement);

                        uploadedImagesDiv.appendChild(container);
                    });
                }
            } else {
                console.error('Error retrieving uploaded images. Please try again.');
            }
        }
    };

    // Retrieve the username directly from the HTML content
    var usernameElement = document.getElementById('username');
    var username = usernameElement.textContent.trim();

    var encodedUsername = encodeURIComponent(username);
    xhr.open('GET', '/display?username=' + encodedUsername, true);
    xhr.responseType = 'json';  // Ensure the response is treated as JSON
    xhr.send();
}

function displayUploadedImages2() {
    var uploadedImagesDiv = document.getElementById('uploaded-images');
    uploadedImagesDiv.innerHTML = '';  // Clear previous content

    var xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function () {
        if (xhr.readyState == 4) {
            if (xhr.status === 200) {
                var images = xhr.response.images;
                if (images) {
                    images.forEach(function (imageData) {
                        var imageFormat = imageData.format;
                        var imageBlob = new Blob([base64ToArrayBuffer(imageData.data)], { type: 'image/' + imageFormat });

                        var imgElement = document.createElement('img');
                        imgElement.src = URL.createObjectURL(imageBlob);
                        imgElement.classList.add('uploaded-image');  // Apply any additional styling
                        console.log('Ravi is revi.')
                        var checkbox = document.createElement('input');
                        checkbox.type = 'checkbox';
                        checkbox.name = 'selected-images';
                        checkbox.value = imgElement.src;
                        checkbox.classList.add('image-checkbox');

                        var container = document.createElement('div');
                        container.classList.add('uploaded-image-container');
                        container.appendChild(checkbox);
                        container.appendChild(imgElement);

                        uploadedImagesDiv.appendChild(container);
                    });
                }
            } else {
                console.error('Error retrieving uploaded images. Please try again.');
            }
        }
    };

    // Retrieve the username directly from the HTML content
    // var usernameElement = document.getElementById('username');
    // var username = usernameElement.textContent.trim();

    // var encodedUsername = encodeURIComponent(username);
    xhr.open('GET', '/display', true);
    xhr.responseType = 'json';  // Ensure the response is treated as JSON
    xhr.send();
}


function base64ToArrayBuffer(base64) {
    var binaryString = window.atob(base64);
    var binaryLen = binaryString.length;
    var bytes = new Uint8Array(binaryLen);
    for (var i = 0; i < binaryLen; i++) {
        var ascii = binaryString.charCodeAt(i);
        bytes[i] = ascii;
    }
    return bytes.buffer;
}


window.onload = function () {
    // Call displayUploadedImages function on window load
    displayUploadedImages();
};

