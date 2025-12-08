// This script runs inside the QWebEngineView for each browser instance.

(function() {
    var OFFLINE_OVERLAY_ID = 'autodarts-offline-overlay';
    var isOffline = false;
    var overlayElement = null;
    
    // Decoded content from Python (Base64)
    var offlinePageContent = "";
    try {
        // Decode Base64 to UTF-8 string
        var b64 = "{offline_html_b64}".trim(); // Remove potential whitespace
        // Standard trick to decode UTF-8 from Base64 in browser
        offlinePageContent = decodeURIComponent(Array.prototype.map.call(window.atob(b64), function(c) {
            return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
        }).join(''));
    } catch(e) {
        console.error("[Autodarts Browser] Failed to decode offline HTML: " + e);
    }
    
    function showOfflineOverlay() {
        if (!isOffline) {
            console.warn('[Autodarts Browser] Connection lost. Displaying offline overlay.');
            isOffline = true;
            if (!overlayElement) {
                overlayElement = document.createElement('div');
                overlayElement.id = OFFLINE_OVERLAY_ID;
                
                overlayElement.style.position = 'fixed';
                overlayElement.style.top = '0';
                overlayElement.style.left = '0';
                overlayElement.style.width = '100vw';
                overlayElement.style.height = '100vh';
                overlayElement.style.backgroundColor = 'rgba(0, 0, 0, 0.95)';
                overlayElement.style.zIndex = '99999';
                overlayElement.style.display = 'flex';
                overlayElement.style.justifyContent = 'center';
                overlayElement.style.alignItems = 'center';
                overlayElement.style.color = 'white';
                overlayElement.style.fontFamily = 'sans-serif';
                overlayElement.style.textAlign = 'center';

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
            // window.location.reload(true); 
        }
    }

    function checkConnectivity() {
        try {
            fetch('https://play.autodarts.io/version', { mode: 'no-cors', cache: 'no-store' })
                .then(function() {
                    if (isOffline) {
                        console.log('[Autodarts Browser] Re-connected to Autodarts.io.');
                        hideOfflineOverlay();
                        setTimeout(function() { window.location.reload(true); }, 1000); 
                    }
                })
                .catch(function() {
                    console.warn('[Autodarts Browser] Failed to reach Autodarts.io.');
                    showOfflineOverlay();
                })
                .finally(function() {
                    setTimeout(checkConnectivity, 5000);
                });
        } catch (e) {
            console.error("[Autodarts Browser] Connectivity check error: " + e);
            setTimeout(checkConnectivity, 10000);
        }
    }

    setTimeout(checkConnectivity, 2000);
})();