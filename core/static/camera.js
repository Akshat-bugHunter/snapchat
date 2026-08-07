document.addEventListener("DOMContentLoaded", () => {
  const video = document.getElementById("video");
  const canvas = document.getElementById("canvas");
  const capture = document.getElementById("capture");
  const container = document.getElementById("camera-container");
  const captureBar = document.getElementById("capture-bar");
  const previewActions = document.getElementById("preview-actions");
  const retakeBtn = document.getElementById("retake");
  const openSendToBtn = document.getElementById("open-send-to");
  const sendToSheet = document.getElementById("send-to-sheet");
  const sheetContent = document.getElementById("sheet-content");
  const closeSendToBtn = document.getElementById("close-send-to");
  const imageDataInput = document.getElementById("image-data");
  const snapThumb = document.getElementById("snap-thumb");
  const sendSnapForm = document.getElementById("send-snap-form");

  if (!video || !canvas || !capture) return;

  let stream = null;
  let cameraReady = false;

  // --- Camera Controls ---
  async function startCamera() {
    cameraReady = false;
    capture.disabled = true;
    capture.style.opacity = "0.5";

    // Restore original video tag if coming from photo preview state
    if (!container.querySelector("video")) {
      container.innerHTML = `<video id="video" autoplay playsinline muted class="w-full h-full object-cover"></video>`;
    }
    const currentVideo = document.getElementById("video");

    try {
      stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: "user" },
        audio: false,
      });
    } catch (err) {
      try {
        stream = await navigator.mediaDevices.getUserMedia({
          video: true,
          audio: false,
        });
      } catch (err2) {
        alert("Unable to access camera.");
        console.error(err2);
        return;
      }
    }

    currentVideo.srcObject = stream;

    currentVideo.onloadedmetadata = async function () {
      try {
        await currentVideo.play();
      } catch (err) {
        console.error(err);
      }
      cameraReady = true;
      capture.disabled = false;
      capture.style.opacity = "1";
    };
  }

  function stopCamera() {
    if (stream) {
      stream.getTracks().forEach((track) => track.stop());
      const currentVideo = document.getElementById("video");
      if (currentVideo) currentVideo.srcObject = null;
      stream = null;
    }
    cameraReady = false;
  }

  function goBack() {
    stopCamera();
    history.back();
  }
  window.goBack = goBack;

  // --- Capture Action ---
  capture.addEventListener("click", () => {
    const currentVideo = document.getElementById("video");
    if (!cameraReady || !currentVideo?.videoWidth || !currentVideo?.videoHeight) {
      return;
    }

    canvas.width = currentVideo.videoWidth;
    canvas.height = currentVideo.videoHeight;
    canvas.getContext("2d").drawImage(currentVideo, 0, 0);

    const photo = canvas.toDataURL("image/jpeg", 0.85);
    imageDataInput.value = photo;

    stopCamera();

    // Show Captured Photo Preview
    container.innerHTML = `<img src="${photo}" class="w-full h-full object-cover">`;
    if (snapThumb) {
      snapThumb.innerHTML = `<img src="${photo}" class="w-full h-full object-cover">`;
    }

    // Toggle Action Bars using Tailwind classes
    captureBar.classList.add("hidden");
    previewActions.classList.remove("hidden");
  });

  // --- Retake Action ---
  retakeBtn?.addEventListener("click", () => {
    imageDataInput.value = "";
    previewActions.classList.add("hidden");
    captureBar.classList.remove("hidden");
    closeSendToSheet();
    startCamera();
  });

  // --- Bottom Sheet Controls ---
  function openSendToSheet() {
    if (!sendToSheet) return;
    sendToSheet.classList.remove("hidden");
    setTimeout(() => {
      sheetContent?.classList.remove("translate-y-full");
    }, 10);
  }

  function closeSendToSheet() {
    if (!sendToSheet) return;
    sheetContent?.classList.add("translate-y-full");
    setTimeout(() => {
      sendToSheet.classList.add("hidden");
    }, 300);
  }

  openSendToBtn?.addEventListener("click", openSendToSheet);
  closeSendToBtn?.addEventListener("click", closeSendToSheet);

  // --- Form Validation ---
  if (sendSnapForm) {
    sendSnapForm.addEventListener("submit", (e) => {
      if (!imageDataInput.value) {
        e.preventDefault();
        alert("Please take a photo first.");
        return;
      }

      const checked = document.querySelectorAll(".friend-check:checked");
      const hasDirectFriend = sendSnapForm.querySelector('input[name="friend_ids"][type="hidden"]');

      if (!hasDirectFriend && checked.length === 0) {
        e.preventDefault();
        alert("Please select at least one friend.");
      }
    });
  }

  // --- Lifecycle Events ---
  window.addEventListener("beforeunload", stopCamera);
  startCamera();
});