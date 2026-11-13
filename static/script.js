const urlInput = document.getElementById("videoUrl");

const downloadBtn = document.getElementById("downloadBtn");

const pasteBtn = document.getElementById("pasteBtn");

const qualitySection = document.getElementById("qualitySection");

const qualitySelect = document.getElementById("quality");

const statusBox = document.getElementById("status");

let selectedMode = "video";


// Select Download Mode

document.querySelectorAll(".mode-btn").forEach(button => {

    button.addEventListener("click", () => {

        document.querySelectorAll(".mode-btn").forEach(btn => {
            btn.classList.remove("active");
        });

        button.classList.add("active");

        selectedMode = button.dataset.mode;

        qualitySection.style.display =
            selectedMode === "video" ? "block" : "none";

    });

});


// Paste URL

pasteBtn.addEventListener("click", async () => {

    try {

        const text = await navigator.clipboard.readText();

        urlInput.value = text;

        showStatus("URL pasted successfully!");

    } catch {

        showStatus("Please paste your URL manually.");

    }

});


// Status Message

function showStatus(message, error = false) {

    statusBox.textContent = message;

    statusBox.className = error
        ? "status error"
        : "status";

}


// Download Function

downloadBtn.addEventListener("click", async () => {

    const url = urlInput.value.trim();

    if (!url) {

        showStatus("Please enter a YouTube URL.", true);

        return;

    }

    downloadBtn.disabled = true;

    downloadBtn.textContent = "Please wait...";

    showStatus("Connecting to YouTube...");

    try {

        const response = await fetch("/download", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({

                url: url,

                mode: selectedMode,

                quality: qualitySelect.value

            })

        });


        if (!response.ok) {

            const result = await response.json();

            throw new Error(
                result.error || "Download failed."
            );

        }


        showStatus("Preparing your file...");


        const blob = await response.blob();

        const contentDisposition =
            response.headers.get("Content-Disposition") || "";

        const match = contentDisposition.match(
            /filename="?([^";]+)"?/i
        );

        const filename = match
            ? match[1]
            : (selectedMode === "audio"
                ? "audio.mp3"
                : "video.mp4");


        const downloadUrl = window.URL.createObjectURL(blob);

        const link = document.createElement("a");

        link.href = downloadUrl;

        link.download = filename;

        document.body.appendChild(link);

        link.click();

        link.remove();

        window.URL.revokeObjectURL(downloadUrl);

        showStatus("Download started! Check your device Downloads folder.");

    }

    catch (error) {

        showStatus(error.message, true);

    }

    finally {

        downloadBtn.disabled = false;

        downloadBtn.innerHTML = "⬇ Download Now";

    }

});