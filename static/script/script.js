var selectedImagesBlobs = [];

function selectImages() {
    selectedImagesBlobs = [];
    var selectedImages = document.querySelectorAll('.image-checkbox:checked');
    var selectedImagesDiv = document.getElementById('selected-images');
    selectedImagesDiv.innerHTML = '';

    selectedImages.forEach(function (image) {
        var imgElement = document.createElement('img');
        imgElement.src = image.value;
        // selectedImagesUrls.push(imgElement.src);
        selectedImagesBlobs.push(displayedImagesdata[imgElement.src]);
        imgElement.classList.add('selected-image');
        selectedImagesDiv.appendChild(imgElement);
    });
    console.log(selectedImagesBlobs);
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
displayedImagesdata = {};
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
                        displayedImagesdata[imgElement.src] = imageData.data;
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
        selectedAudioFilesIds = [];
        var selectedAudios = [];
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
        console.log('retrieved audio');
        const audioPromises = audioIds.map(async (Audio_id) => {
            // Fetch audio file
            audioID.push(Audio_id);
            console.log(Audio_id);
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
    else if (selectedImagesBlobs.length === 0){
        alert("No Images selected");
        return ;
    }
    else{
        var formData2 = new FormData();
        
        for (var i = 0; i < selectedImagesBlobs.length; i++) {
            formData2.append('selectedImagesBlobs[]', selectedImagesBlobs[i]);
        }
        
        for (var j = 0; j < selectedAudioFilesIds.length; j++) {
            formData2.append('selectedAudioFilesIds[]', selectedAudioFilesIds[j]);
        }
        var resolution = document.getElementById('resolution').value;
        formData2.append('resolution', resolution);

        var transition = document.getElementById('transition').value;
        formData2.append('transition', transition);
        
        alert("Don't refresh the page. Please wait for few moments...");
        $.ajax({
            type: "POST",
            url: "/create_video",
            data: formData2,
            processData: false,  
            contentType: false,  
            success: function(response) {
                console.log('blob received successfully.');

                var previewContainer = document.getElementById('preview-container');
                var existingVideo = previewContainer.querySelector('video');
                var downloadLink = document.getElementById('download-link');
                var previewHeading = document.getElementById('preview-heading');

                if (existingVideo) {
                    previewContainer.removeChild(existingVideo);
                }

                if (downloadLink) {
                    downloadLink.parentNode.removeChild(downloadLink);
                }

                if (previewHeading) {
                    previewHeading.parentNode.removeChild(previewHeading);
                }

                var videoElement = document.createElement('video');
                var blob = new Blob([base64ToArrayBuffer(response.video_base64)], { type: response.mime_type });
                var videoUrl = URL.createObjectURL(blob);
                videoElement.src = videoUrl;
                videoElement.width = 640;
                videoElement.height = 480;
                videoElement.controls = true;
                previewContainer.appendChild(videoElement);

                // var previewheading = document.createElement('H2');
                // previewheading.innerText='PREVIEW VIDEO'
                // var heading = document.getElementById('preview')
                // heading.appendChild(previewheading)

                var newPreviewHeading = document.createElement('h2');
                newPreviewHeading.id = 'preview-heading';
                newPreviewHeading.innerText = 'PREVIEW VIDEO';
                previewContainer.prepend(newPreviewHeading);
                
                var newDownloadLink = document.createElement('a');
                newDownloadLink.id = 'download-link';
                newDownloadLink.href = videoUrl;
                newDownloadLink.innerText = "Download Video";
                newDownloadLink.download = "video.mp4"
                var downloadLinkContainer = document.querySelector('.download-link');
                downloadLinkContainer.appendChild(newDownloadLink); 
                
            },
            error: function(xhr, status, error) {
                console.error("Error:", error);
                alert("error loading video ,please try again")
            }
        });

    }
    return ; 
}