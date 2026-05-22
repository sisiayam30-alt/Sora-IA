// Mock database array representing available application files
const applicationData = [
    {
        id: "1",
        title: "File Downloader Pro",
        version: "v2.4.1",
        size: "18.4 MB",
        description: "High-speed multi-threaded download manager optimized for mobile architectures.",
        downloadUrl: "#"
    },
    {
        id: "2",
        title: "Media Streamer",
        version: "v1.0.8",
        size: "42.1 MB",
        description: "Lightweight application designed for seamless local network audio and video rendering.",
        downloadUrl: "#"
    },
    {
        id: "3",
        title: "System Optimizer",
        version: "v5.2.0",
        size: "12.7 MB",
        description: "Advanced utility tool to clear cache directories and optimize runtime memory allocation.",
        downloadUrl: "#"
    }
];

document.addEventListener("DOMContentLoaded", () => {
    const container = document.getElementById("app-container");
    renderApplications(applicationData, container);
});

/**
 * Dynamically injects application cards into the DOM
 * @param {Array} items 
 * @param {HTMLElement} targetElement 
 */
function renderApplications(items, targetElement) {
    if (!targetElement) return;
    
    targetElement.innerHTML = "";

    if (items.length === 0) {
        targetElement.innerHTML = `<div class="loading">No applications available at this time.</div>`;
        return;
    }

    items.forEach(item => {
        const card = document.createElement("div");
        card.className = "card";
        card.innerHTML = `
            <div>
                <h3>${escapeHtml(item.title)}</h3>
                <div class="meta">${escapeHtml(item.version)} &bull; ${escapeHtml(item.size)}</div>
                <p>${escapeHtml(item.description)}</p>
            </div>
            <a href="${item.downloadUrl}" class="btn-download" data-id="${item.id}">Download APK</a>
        `;
        targetElement.appendChild(card);
    });
}

/**
 * Utility function to prevent XSS entry points
 * @param {string} string 
 * @returns {string}
 */
function escapeHtml(string) {
    const div = document.createElement("div");
    div.innerText = string;
    return div.innerHTML;
}
