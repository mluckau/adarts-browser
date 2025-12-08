// This script runs inside the QWebEngineView for each browser instance.

(function() {
    const OFFLINE_OVERLAY_ID = 'autodarts-offline-overlay';
    let isOffline = false;
    let overlayElement = null;
    let offlinePageContent = `<!-- OFFLINE_PAGE_PLACEHOLDER -->`; // Will be replaced by Python
    
    function showOfflineOverlay() {
        if (!isOffline) {
            console.warn('[Autodarts Browser] Connection lost. Displaying offline overlay.');
            isOffline = true;
            if (!overlayElement) {
                overlayElement = document.createElement('div');
                overlayElement.id = OFFLINE_OVERLAY_ID;
                Object.assign(overlayElement.style, {
                    position: 'fixed',
                    top: '0',
                    left: '0',
                    width: '100vw',
                    height: '100vh',
                    backgroundColor: 'rgba(0, 0, 0, 0.95)', // Darken background
                    zIndex: '99999', // Ensure it's on top
                    display: 'flex',
                    justifyContent: 'center',
                    alignItems: 'center',
                    color: 'white',
                    fontFamily: 'sans-serif',
                    textAlign: 'center'
                });
                // Inject the content of the offline page
                overlayElement.innerHTML = offlinePageContent;
                document.body.appendChild(overlayElement);
            }
            overlayElement.style.display = 'flex';
        }
    }

    function hideOfflineOverlay() {
        if (isOffline) {
            console.info('[Autodarts Browser] Connection restored. Hiding offline overlay.');
            isOffline = false;
            if (overlayElement) {
                overlayElement.style.display = 'none';
            }
            // Optional: Force a reload of the original page to ensure full recovery
            // window.location.reload(true); // force a hard reload
        }
    }

    function checkConnectivity() {
        // Try to fetch a small, reliable resource or the main Autodarts page itself
        fetch('https://play.autodarts.io/version', { mode: 'no-cors', cache: 'no-store' })
            .then(() => {
                // If fetch succeeds (even with CORS error for no-cors), assume online
                if (isOffline) {
                    console.log('[Autodarts Browser] Re-connected to Autodarts.io.');
                    hideOfflineOverlay();
                    // Give it a moment, then reload the page to ensure fresh content
                    setTimeout(() => window.location.reload(true), 1000); 
                }
            })
            .catch(() => {
                // If fetch fails, assume offline
                console.warn('[Autodarts Browser] Failed to reach Autodarts.io.');
                showOfflineOverlay();
            })
            .finally(() => {
                // Schedule next check
                setTimeout(checkConnectivity, 5000); // Check every 5 seconds
            });
    }

    // Start checking connectivity once the script is injected
    setTimeout(checkConnectivity, 2000); // Initial check after 2 seconds
})();
