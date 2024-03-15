document.getElementById("submitBtn").addEventListener("click", function () {
    var selectedAudios = [];
    var checkboxes = document.querySelectorAll('.audioCheckbox:checked');
    checkboxes.forEach(function (checkbox) {
        selectedAudios.push(checkbox.value);
    });
    // Send selectedAudios to backend (e.g., using fetch)
    console.log(selectedAudios); // Just for demonstration
    var submissionMessage = "Number of audio files submitted: " + checkboxes.length;
    alert(submissionMessage);
});

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
            const response = await fetch(`/audio/${Audio_id}`);
            const blob = await response.blob();
            return blob;
        });

        // Wait for all audio files to be loaded
        const audioArray = await Promise.all(audioPromises);

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

fetchAudio();