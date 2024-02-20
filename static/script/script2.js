let audioElement;
let isPlaying = false;

function openAudioFileInput() {
    const audioInput = document.getElementById('audioInput');
    audioInput.click();
}

function handleAudioFile() {
    const audioInput = document.getElementById('audioInput');
    const selectedAudioName = document.getElementById('selectedAudioName');
    const audioControls = document.getElementById('audioControls');
    
    if (audioInput.files.length > 0) {
        const selectedAudio = audioInput.files[0];
        console.log('Selected audio file:', selectedAudio);

        selectedAudioName.textContent = `Selected Audio: ${selectedAudio.name}`;

        // Create an audio element
        audioElement = new Audio();
        audioElement.src = URL.createObjectURL(selectedAudio);

        // Show play/pause button
        audioControls.style.display = 'flex';
    }
}

function togglePlayPause() {
    const playIcon = document.getElementById('playIcon');
    const pauseIcon = document.getElementById('pauseIcon');

    if (audioElement.paused) {
        audioElement.play();
        isPlaying = true;
        playIcon.style.display = 'none';
        pauseIcon.style.display = 'inline';
    } else {
        audioElement.pause();
        isPlaying = false;
        playIcon.style.display = 'inline';
        pauseIcon.style.display = 'none';
    }
}
