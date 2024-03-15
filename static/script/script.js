var selectedImagesUrls = [];

function selectImages() {
    var selectedImages = document.querySelectorAll('.image-checkbox:checked');
    var selectedImagesDiv = document.getElementById('selected-images');
    selectedImagesDiv.innerHTML = '';

    selectedImages.forEach(function (image) {
        var imgElement = document.createElement('img');
        imgElement.src = image.value;
        selectedImagesUrls.push(imgElement.src);
        imgElement.classList.add('selected-image');
        selectedImagesDiv.appendChild(imgElement);
    });
    console.log(selectedImagesFileNames);
}


var username = "";
// console.log(username) ;

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
                        var fileName = imageData.filename;
                        var imageFormat = imageData.format;
                        var imageBlob = new Blob([base64ToArrayBuffer(imageData.data)], { type: 'image/' + imageFormat });

                        var imgElement = document.createElement('img');
                        imgElement.src = URL.createObjectURL(imageBlob);
                        imgElement.classList.add('uploaded-image'); 

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
    username = usernameElement.textContent.trim();

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
                        var fileName = imageData.filename;
                        var imageFormat = imageData.format;
                        var imageBlob = new Blob([base64ToArrayBuffer(imageData.data)], { type: 'image/' + imageFormat });

                        var imgElement = document.createElement('img');
                        imgElement.src = URL.createObjectURL(imageBlob);
                        imgElement.classList.add('uploaded-image');
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
                    console.log(displayedImages);
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
///////////////////////////////////

// window.onload = function () {
//     // Call displayUploadedImages function on window load
//     // displayUploadedImages();
//     fetchAudio();
// };



//////////// AUDIO ////////////////

var selectedAudioFilesIds = [];


document.addEventListener('DOMContentLoaded',function(){ // To wait untill the whole html page loaded, only then the function can execute
    document.getElementById("submitBtn").addEventListener("click", function () {
        var selectedAudios = [];
        var selectedAudioFiles = [] ;
        var checkboxes = document.querySelectorAll('.audioCheckbox:checked');
        checkboxes.forEach(function (checkbox) {
            selectedAudios.push(checkbox.value);
            selectedAudioFilesIds.push(audioID[checkbox.value]);
        });
        
    
        
        
        console.log(selectedAudios); // Just for demonstration
        console.log(selectedAudioFilesIds) ; // Just for checking the working of the selection
        var submissionMessage = "Number of audio files submitted: " + checkboxes.length;
        alert(submissionMessage);
    });
})

var audioArray = [];
var audioID = [];

async function fetchAudio() {
    try {
        // Fetch audio data from the server
        const response = await fetch('/get_audio_from_database');
        const data = await response.json();

        // Extract audio IDs from the data
        const audioIds = data.id;

        // Load audio files asynchronously
        const audioPromises = audioIds.map(async (Audio_id) => {
            // Fetch audio file
            audioID.push(Audio_id);
            const response = await fetch(`/audio/${Audio_id}`);
            const blob = await response.blob();
            return blob;
        });

        // Wait for all audio files to be loaded
         audioArray = await Promise.all(audioPromises);

        // Display audio files
        displayAudio(audioArray);
    } catch (error) {
        console.error('Error fetching audio:', error);
    }
}

function displayAudio(audioData) {
    const audioContainer = document.querySelector('.audio-div');
    let audioHTML = '';

    audioData.forEach((audioBlob, index) => {
        // Create an object URL for the audio blob
        const audioUrl = URL.createObjectURL(audioBlob);

        // Display audio element
        audioHTML += `
<li>
    <div class="audio" data-index="${index}">
        <span class="index">Audio ${index + 1}</span>
        <audio controls>
            <source src="${audioUrl}" type="audio/mpeg">
            Your browser does not support the audio element.
        </audio>
        <input type="checkbox" class="audioCheckbox" name="audio" value="${index}">
    </div>
</li>
`;
    });

    // Set HTML content to display audio elements
    audioContainer.innerHTML = audioHTML;
}

/////////////////////////////////////////////////////////////

function updateToFlask(){
    if (selectedAudioFilesIds.length === 0){
        alert("No Audio Selected.");
        return;
    }
    else if (selectedImagesFileNames.length === 0){
        alert("No Images selected");
        return ;
    }
    else{
        var formData2 = new FormData();
        for (var i = 0; i < selectedImagesFileNames.length; i++) {
            formData2.append('selectedImagesFileNames[]', selectedImagesFileNames[i]);
        }
    
        // Append each element of selectedImages array
        for (var j = 0; j < selectedAudioFilesIds.length; j++) {
            formData2.append('selectedAudioFilesIds[]', selectedAudioFilesIds[j]);
        }
        $.ajax({
            type: "POST",
            url: "/create_video",
            data: formData2,
            processData: false,  // Prevent jQuery from processing the data
            contentType: false,  // Prevent jQuery from setting the content type
            success: function(response) {
                console.log('Arrays sent successfully.');
                console.log(response);
            },
            error: function(error) {
                console.error('Error sending arrays to the backend:', error);
            }
        });

    }
    return ; 
}