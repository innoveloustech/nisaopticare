document.addEventListener("DOMContentLoaded", () => {
  console.log("✅ DOM loaded");

  const video = document.getElementById("video");
  const canvas = document.getElementById("canvas");
  const ctx = canvas.getContext("2d");
  const overlay = document.getElementById("overlay");

  // Pupillary Distance (PD) in mm
  let pdValue = 61;         // default
  const defaultPD = 61;     // baseline for scaling
  const pdDisplay = document.getElementById("pd-value");

  // PD controls
  document.getElementById("pd-inc").addEventListener("click", () => {
    pdValue += 1;
    pdDisplay.textContent = pdValue;
  });
  document.getElementById("pd-dec").addEventListener("click", () => {
    pdValue -= 1;
    pdDisplay.textContent = pdValue;
  });

  // Draw loading message immediately
  function drawLoadingMessage() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = "rgba(0,0,0,0.5)";
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = "white";
    ctx.font = "20px Arial";
    ctx.textAlign = "center";
    ctx.fillText("👓 Just a sec... loading FaceMesh", canvas.width / 2, canvas.height / 2);
  }

  drawLoadingMessage();

  // Init FaceMesh
  const faceMesh = new FaceMesh({
    locateFile: (file) =>
      `https://cdn.jsdelivr.net/npm/@mediapipe/face_mesh/${file}`,
  });

  faceMesh.setOptions({
    maxNumFaces: 1,
    refineLandmarks: true,
    minDetectionConfidence: 0.5,
    minTrackingConfidence: 0.5,
  });

  faceMesh.onResults(onResults);

  let hasFirstResult = false;

  // Handle results
  function onResults(results) {
    ctx.save();
    
    // Clear canvas before each new frame
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // If video feed is ready, apply horizontal flip transformation
    if (results.image) {
      ctx.translate(canvas.width, 0);
      ctx.scale(-1, 1);
    }

    // Always draw video frame
    ctx.drawImage(results.image, 0, 0, canvas.width, canvas.height);

    // If no faces detected, show loading message
    if (!results.multiFaceLandmarks || !results.multiFaceLandmarks.length) {
      if (!hasFirstResult) {
        // Only show loading message without flip
        ctx.fillStyle = "rgba(0,0,0,0.5)";
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        ctx.fillStyle = "white";
        ctx.font = "20px Arial";
        ctx.textAlign = "center";
        ctx.fillText("👓 Just a sec... loading FaceMesh", canvas.width / 2, canvas.height / 2);
      }
      ctx.restore();
      return;
    }

    hasFirstResult = true;
    const lm = results.multiFaceLandmarks[0];

    // Eye centers calculation (for glasses placement)
    const leftEye = {
      x: (lm[33].x + lm[133].x) / 2,
      y: (lm[33].y + lm[133].y) / 2,
    };
    const rightEye = {
      x: (lm[263].x + lm[362].x) / 2,
      y: (lm[263].y + lm[362].y) / 2,
    };

    // Calculate distance & rotation between the eyes
    const dx = (rightEye.x - leftEye.x) * canvas.width;
    const dy = (rightEye.y - leftEye.y) * canvas.height;
    const eyeDist = Math.hypot(dx, dy);
    const angle = Math.atan2(dy, dx);

    // PD scaling for glasses size
    const pdScale = pdValue / defaultPD;

    // Glasses size and center
    const glassesWidth = eyeDist * 2.3 * pdScale;
    const glassesHeight = glassesWidth * (overlay.height / overlay.width);
    const centerX = ((leftEye.x + rightEye.x) / 2) * canvas.width;
    const centerY = ((leftEye.y + rightEye.y) / 2) * canvas.height;

    // Draw glasses (with transformations applied)
    ctx.translate(centerX, centerY);
    ctx.rotate(angle);
    ctx.drawImage(overlay, -glassesWidth / 2, -glassesHeight / 2, glassesWidth, glassesHeight);
    ctx.restore();
  }


  // Camera setup with getUserMedia
  navigator.mediaDevices.getUserMedia({
    video: {
      width: 640,  // Set a fixed width for the camera feed
      height: 480, // Set a fixed height for the camera feed
      facingMode: 'user', // Front camera
    }
  })
  .then((stream) => {
    // Set the video source to the stream
    video.srcObject = stream;
    video.onloadeddata = () => {
      // Ensure that play is only called once after video is ready
      video.play();
      resizeCanvas();  // Call resize function after the video is loaded
    };
  })
  .catch((err) => {
    console.error('Error accessing the camera: ', err);
  });

  // Camera feed to FaceMesh
  const camera = new Camera(video, {
    onFrame: async () => {
      await faceMesh.send({ image: video });
    },
    width: 640,
    height: 480,
  });

  camera.start();

  // Snapshot
  document.getElementById("download-snap").addEventListener("click", () => {
    const link = document.createElement("a");
    link.download = "snapshot.png";
    link.href = canvas.toDataURL("image/png");
    link.click();
  });

  function resizeCanvas() {
    const container = canvas.parentElement;
    const containerWidth = container.clientWidth;

    // Ensure width is within bounds
    let canvasWidth = containerWidth;
    if (canvasWidth < 320) canvasWidth = 320;
    if (canvasWidth > 640) canvasWidth = 640;

    // Dynamically adjust canvas height based on the camera's aspect ratio
    const aspectRatio = video.videoWidth / video.videoHeight;
    const canvasHeight = canvasWidth / aspectRatio;

    // Set canvas CSS size (display size)
    canvas.style.width = `${canvasWidth}px`;
    canvas.style.height = `${canvasHeight}px`;

    // Set internal canvas resolution
    canvas.width = canvasWidth;
    canvas.height = canvasHeight;
  }

  window.addEventListener('load', resizeCanvas);
  window.addEventListener('resize', resizeCanvas);

});
