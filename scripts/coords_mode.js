try {
    const observer = new MutationObserver(() => {
        const btn = document.querySelector('button[aria-label="Coords mode"]');
        if (btn) {
            // Check if it's already active (data-active attribute usually has a value or exists if active)
            // The user provided snippet has data-active="" which implies NOT active or active?
            // Usually data-active present means active. But let's check.
            // If the user says they HAVE to click it, it means it's not the default.
            // Let's just click it if found.
            
            // Optional: Check if already active to avoid toggling off
            if (!btn.hasAttribute('data-active')) { 
                 console.log("[CoordsMode] Button gefunden. Klicke...");
                 btn.click();
                 observer.disconnect();
            } else {
                 console.log("[CoordsMode] Button bereits aktiv.");
                 observer.disconnect();
            }
        }
    });

    const target = document.getElementById('root') || document.body;
    if (target) {
        observer.observe(target, { childList: true, subtree: true });
    }

} catch (e) {
    console.error("[CoordsMode] Fehler: " + e);
}