const audioContext = new (window.AudioContext || window.webkitAudioContext)();
let currentOctave = 1;


const filterNode = audioContext.createBiquadFilter();
const analyser = audioContext.createAnalyser();
analyser.fftSize = 2048;
const bufferLength = analyser.frequencyBinCount;
const dataArray = new Uint8Array(bufferLength);
const gainNode = audioContext.createGain();

filterNode.connect(gainNode);
gainNode.connect(analyser);
analyser.connect(audioContext.destination);

const gainControl = document.getElementById('gain-control');
const gainValueDisplay = document.getElementById('gain-value');

gainControl.addEventListener('input', () => {
    const gainValue = parseFloat(gainControl.value);
    gainNode.gain.value = gainValue; 
    gainValueDisplay.textContent = gainValue.toFixed(2); 
});

const attackSlider = document.getElementById('attack');
const attackValue = document.getElementById('attack-value');

const decaySlider = document.getElementById('decay');
const decayValue = document.getElementById('decay-value');

const sustainSlider = document.getElementById('sustain');
const sustainValue = document.getElementById('sustain-value');

const releaseSlider = document.getElementById('release');
const releaseValue = document.getElementById('release-value');

attackSlider.addEventListener('input', () => {
    attackValue.textContent = attackSlider.value;
});

decaySlider.addEventListener('input', () => {
    decayValue.textContent = decaySlider.value;
});

sustainSlider.addEventListener('input', () => {
    sustainValue.textContent = sustainSlider.value;
});

releaseSlider.addEventListener('input', () => {
    releaseValue.textContent = releaseSlider.value;
});

function groupNotesByOctave(frequencies) {
    const octaves = {
        1: [],
        2: [],
        3: [],
        4: []
    };

    frequencies.forEach(({ note, frequency }) => {
        if (frequency < 130) octaves[1].push({ note, frequency });
        else if (frequency < 260) octaves[2].push({ note, frequency });
        else if (frequency < 520) octaves[3].push({ note, frequency });
        else octaves[4].push({ note, frequency });
    });

    return octaves;
}

function createKeyboard(frequencies, keyboardId) {
    const keyboard = document.getElementById(keyboardId);
    keyboard.innerHTML = '';

    frequencies.forEach(({ note, frequency }) => {
        const key = document.createElement('button');
        key.textContent = note;
        key.dataset.frequency = frequency;
        key.classList.add('key');
        key.addEventListener('click', () => playTone(frequency));
        keyboard.appendChild(key);
    });
}

function updateKeyboard(octave, acousticOctaves, westernOctaves) {
    createKeyboard(acousticOctaves[octave], "acoustic-keyboard");
    createKeyboard(westernOctaves[octave], "western-keyboard");
}

async function fetchFrequencies() {
    try {
        const response = await fetch('/api/frequencies');
        const data = await response.json();

        const acousticOctaves = groupNotesByOctave(data.acoustic);
        const westernOctaves = groupNotesByOctave(data.western);

        updateKeyboard(currentOctave, acousticOctaves, westernOctaves);

        document.getElementById('octave-select').addEventListener('change', (event) => {
            currentOctave = parseInt(event.target.value);
            updateKeyboard(currentOctave, acousticOctaves, westernOctaves);
        });
    } catch (error) {
        console.error("Error while loading frequencies:", error);
    }
}

function applyFilter() {
    const filterType = document.getElementById('filter-type').value;
    const cutoffFrequency = parseFloat(document.getElementById('cutoff').value);

    filterNode.type = filterType;
    filterNode.frequency.value = cutoffFrequency;
}

function playTone(frequency) {
    const numHarmonics = parseInt(document.getElementById('harmonics').value);

    for (let i = 1; i <= numHarmonics; i++) {
        const oscillator = audioContext.createOscillator();
        const harmonicGainNode = audioContext.createGain();

        const waveform = document.getElementById('waveform_dp').value;
        oscillator.type = waveform; 

        oscillator.frequency.value = frequency * i; 

        oscillator.connect(filterNode);
        filterNode.connect(harmonicGainNode);
        harmonicGainNode.connect(gainNode);

        const now = audioContext.currentTime;
        const attack = parseFloat(document.getElementById('attack').value);
        const decay = parseFloat(document.getElementById('decay').value);
        const sustain = parseFloat(document.getElementById('sustain').value);
        const release = parseFloat(document.getElementById('release').value);

        harmonicGainNode.gain.setValueAtTime(0, now);
        harmonicGainNode.gain.linearRampToValueAtTime(1 / i, now + attack);
        harmonicGainNode.gain.linearRampToValueAtTime(sustain / i, now + attack + decay);
        harmonicGainNode.gain.setValueAtTime(sustain / i, now + attack + decay);
        harmonicGainNode.gain.linearRampToValueAtTime(0, now + attack + decay + release);

        oscillator.start(now);
        oscillator.stop(now + attack + decay + release);
    }
}

document.getElementById('filter-type').addEventListener('change', applyFilter);
document.getElementById('cutoff').addEventListener('input', (event) => {
    document.getElementById('cutoff-value').textContent = event.target.value;
    applyFilter();
});

document.getElementById('harmonics').addEventListener('input', (event) => {
    document.getElementById('harmonics-value').textContent = event.target.value;
});

const canvas = document.getElementById('waveform');
const canvasCtx = canvas.getContext('2d');

function drawWaveform() {
    requestAnimationFrame(drawWaveform);
    analyser.getByteTimeDomainData(dataArray);

    canvasCtx.fillStyle = 'rgb(200, 200, 200)';
    canvasCtx.fillRect(0, 0, canvas.width, canvas.height);

    canvasCtx.lineWidth = 2;
    canvasCtx.strokeStyle = 'rgb(0, 0, 0)';
    canvasCtx.beginPath();

    const sliceWidth = canvas.width * 1.0 / bufferLength;
    let x = 0;

    for (let i = 0; i < bufferLength; i++) {
        const v = dataArray[i] / 128.0;
        const y = v * canvas.height / 2;

        if (i === 0) {
            canvasCtx.moveTo(x, y);
        } else {
            canvasCtx.lineTo(x, y);
        }
        x += sliceWidth;
    }

    canvasCtx.lineTo(canvas.width, canvas.height / 2);
    canvasCtx.stroke();
}

drawWaveform();
fetchFrequencies();