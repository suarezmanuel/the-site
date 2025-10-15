// --- GLOBAL STATE & CONSTANTS ---
const LOGICAL_WIDTH = 493;
const LOGICAL_HEIGHT = 493;
const MODULE_COUNT = 29;
const MODULE_SIZE = LOGICAL_WIDTH / MODULE_COUNT;

let originalMatrix = null, skeletonMatrix = null, skeletonMaskMatrix = null;
let backgroundImage = null, backgroundImageData = null;
let currentModeId = 0;

const canvas = document.getElementById('qrCanvas1');
const ctx = canvas.getContext('2d');
const dpr = window.devicePixelRatio || 1;

const canvas2 = document.getElementById('qrCanvas2');
const canvas3 = document.getElementById('qrCanvas3');
const canvas4 = document.getElementById('qrCanvas4');
const canvas5 = document.getElementById('qrCanvas5');

function fillWhite(canvas) {
    const tempCtx = canvas.getContext('2d');
    setupCanvas(canvas)
    tempCtx.fillStyle = "#707070"
    tempCtx.fillRect(0, 0, LOGICAL_WIDTH, LOGICAL_HEIGHT);
}

function setupCanvas(canvas) {
    const ctx = canvas.getContext('2d');
    canvas.width = LOGICAL_WIDTH * dpr;
    canvas.height = LOGICAL_HEIGHT * dpr;
    canvas.style.width = `${LOGICAL_WIDTH}px`;
    canvas.style.height = `${LOGICAL_HEIGHT}px`;
    ctx.scale(dpr, dpr);
    // Disable smoothing on the main canvas too, for good measure.
    ctx.imageSmoothingEnabled = false;
}

function imageToMatrix(imageObject, type) {
    const tempCanvas = document.createElement('canvas');
    const tempCtx = tempCanvas.getContext('2d');
    tempCanvas.width = imageObject.width;
    tempCanvas.height = imageObject.height;
    tempCtx.drawImage(imageObject, 0, 0);
    const imageData = tempCtx.getImageData(0, 0, imageObject.width, imageObject.height);
    const pixels = imageData.data;
    const matrix = [];
    for (let i = 0; i < MODULE_COUNT; i++) {
        const arr = [];
        for (let j = 0; j < MODULE_COUNT; j++) {
            const sx = j * (imageObject.width / MODULE_COUNT);
            const sy = i * (imageObject.height / MODULE_COUNT);
            const sampleX = Math.floor(sx + (imageObject.width / (MODULE_COUNT * 2)));
            const sampleY = Math.floor(sy + (imageObject.height / (MODULE_COUNT * 2)));
            const pixelIndex = (sampleY * imageObject.width + sampleX) * 4;
            const r = pixels[pixelIndex];
            const a = pixels[pixelIndex + 3];
            let value = 0;
            if (type === 'qr') { if (r === 0 && a === 255) value = 1; }
            else if (type === 'skeleton_mask') { if (a === 255) value = 1; }
            arr.push(value);
        }
        matrix.push(arr);
    }
    return matrix;
}

function draw() {
    if (!originalMatrix) return;

    ctx.fillStyle = "#707070";
    ctx.fillRect(0, 0, LOGICAL_WIDTH, LOGICAL_HEIGHT);

    if (backgroundImage) {
        ctx.globalAlpha = 0.5; // Correct transparency
        // ctx.drawImage(backgroundImage, 0, 0, LOGICAL_WIDTH, LOGICAL_HEIGHT);
        ctx.globalAlpha = 1.0;
    }
    const currMatrix = generateCurrentMatrix();
    if (!currMatrix) return;
    ctx.fillStyle = "rgb(71,28,28)";

    for (let i = 0; i < MODULE_COUNT; i++) {
        for (let j = 0; j < MODULE_COUNT; j++) {
            const isOriginalMode = (currentModeId === 0 || currentModeId === 9);
            let shouldDraw = false;
            if (isOriginalMode) {
                if (currMatrix[i][j] === 1 || skeletonMatrix[i][j] === 1)
                    shouldDraw = true;
            } else {
                if (currMatrix[i][j] === 1 && skeletonMaskMatrix[i][j] !== 1)
                    shouldDraw = true;
            }
            if (shouldDraw) {
                ctx.fillRect(j * MODULE_SIZE, i * MODULE_SIZE, MODULE_SIZE, MODULE_SIZE);
            }
        }
    }
    if (currentModeId === 0) {
        drawGridLines();
    }

    fillWhite(canvas2)
    fillWhite(canvas3)
    fillWhite(canvas4)
    fillWhite(canvas5)
}

function generateCurrentMatrix() {
    let matrix = Array(MODULE_COUNT).fill(0).map(() => Array(MODULE_COUNT).fill(0));
    switch (currentModeId) {
        case 0:
        case 9:
            return originalMatrix;
        case 1:
            for (let i = 0; i < MODULE_COUNT; i++)
                for (let j = 0; j < MODULE_COUNT; j++)
                    if ((i + j) % 2 === 0) matrix[i][j] = 1;
            break;
        case 2:
            for (let i = 0; i < MODULE_COUNT; i++)
                for (let j = 0; j < MODULE_COUNT; j++)
                    if (i % 2 === 0) matrix[i][j] = 1;
            break;
        case 3:
            for (let i = 0; i < MODULE_COUNT; i++)
                for (let j = 0; j < MODULE_COUNT; j++)
                    if (j % 3 === 0) matrix[i][j] = 1;
            break;
        case 4:
            for (let i = 0; i < MODULE_COUNT; i++)
                for (let j = 0; j < MODULE_COUNT; j++)
                    if ((i + j) % 3 === 0) matrix[i][j] = 1;
            break;
        case 5:
            for (let i = 0; i < MODULE_COUNT; i++)
                for (let j = 0; j < MODULE_COUNT; j++)
                    if ((Math.floor(i / 2) + Math.floor(j / 3)) % 2 === 0) matrix[i][j] = 1;
            break;
        case 6:
            for (let i = 0; i < MODULE_COUNT; i++)
                for (let j = 0; j < MODULE_COUNT; j++)
                    if ((i * j) % 2 + (i * j) % 3 === 0) matrix[i][j] = 1;
            break;
        case 7:
            for (let i = 0; i < MODULE_COUNT; i++)
                for (let j = 0; j < MODULE_COUNT; j++)
                    if (((i * j) % 3 + i * j) % 2 === 0) matrix[i][j] = 1;
            break;
        case 8:
            for (let i = 0; i < MODULE_COUNT; i++)
                for (let j = 0; j < MODULE_COUNT; j++)
                    if (((i * j) % 3 + i + j) % 2 === 0) matrix[i][j] = 1;
            break;
    }
    return matrix;
}

function getCenterColor(i, j) {
    if (!backgroundImageData) return null;
    const sx = j * MODULE_SIZE;
    const sy = i * MODULE_SIZE;
    const sampleX = Math.floor(sx + MODULE_SIZE / 2);
    const sampleY = Math.floor(sy + MODULE_SIZE / 2);
    const pixelIndex = (sampleY * LOGICAL_WIDTH + sampleX) * 4;
    return [backgroundImageData.data[pixelIndex], backgroundImageData.data[pixelIndex + 1], backgroundImageData.data[pixelIndex + 2], backgroundImageData.data[pixelIndex + 3]].join(',');
}

function drawGridLines() {
    if (!backgroundImageData) return;
    ctx.strokeStyle = "rgb(189,168,0)";
    ctx.lineWidth = 2 / dpr;
    for (let i = 0; i < MODULE_COUNT; i++) {
        for (let j = 0; j < MODULE_COUNT; j++) {
            const currColor = getCenterColor(i, j);
            if (i > 0) {
                const upColor = getCenterColor(i - 1, j);
                if (upColor !== currColor) {
                    ctx.beginPath();
                    ctx.moveTo(j * MODULE_SIZE, i * MODULE_SIZE);
                    ctx.lineTo((j + 1) * MODULE_SIZE, i * MODULE_SIZE);
                    ctx.stroke();
                }
            }
            if (j > 0) {
                const leftColor = getCenterColor(i, j - 1);
                if (leftColor !== currColor) {
                    ctx.beginPath();
                    ctx.moveTo(j * MODULE_SIZE, i * MODULE_SIZE);
                    ctx.lineTo(j * MODULE_SIZE, (i + 1) * MODULE_SIZE);
                    ctx.stroke();
                }
            }
        }
    }
}

function loadImage(src) {
    return new Promise((resolve, reject) => {
        const img = new Image();
        img.onload = () => resolve(img);
        img.onerror = reject;
        img.src = src;
    });
}

async function loadAllImagesAndInitialize() {
    try {
        const [imageImg, skeletonImg, backgroundImg] = await Promise.all([loadImage('images/image.png'), loadImage('images/skeleton.png'), loadImage('images/background-2.png')]);

        originalMatrix = imageToMatrix(imageImg, 'qr');
        skeletonMatrix = imageToMatrix(skeletonImg, 'qr');
        skeletonMaskMatrix = imageToMatrix(skeletonImg, 'skeleton_mask');
        backgroundImage = backgroundImg;

        const tempCtx = document.createElement('canvas').getContext('2d');
        tempCtx.canvas.width = LOGICAL_WIDTH;
        tempCtx.canvas.height = LOGICAL_HEIGHT;

        // --- THE FIX IS HERE ---
        tempCtx.imageSmoothingEnabled = false;

        tempCtx.drawImage(backgroundImg, 0, 0, LOGICAL_WIDTH, LOGICAL_HEIGHT);
        backgroundImageData = tempCtx.getImageData(0, 0, LOGICAL_WIDTH, LOGICAL_HEIGHT);

        draw();
    } catch (error) {
        console.error("Image loading failed:", error);
    }
}

// --- STARTUP ---
setupCanvas(canvas);
setupCanvas(canvas2);
setupCanvas(canvas3);
setupCanvas(canvas4);
setupCanvas(canvas5);

document.addEventListener('keydown', (event) => {
    const digit = parseInt(event.key, 10);
    if (!isNaN(digit) && digit >= 0 && digit <= 9) {
        currentModeId = digit;
        draw();
    }
});

window.onload = loadAllImagesAndInitialize;