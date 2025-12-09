try {
    const targetMode = '{view_mode}'; // Wird durch Python ersetzt: 'Segments mode', 'Coords mode', 'Live mode'

    console.log("[ViewMode] Ziel-Modus: " + targetMode);

    const observer = new MutationObserver(() => {
        // Suche den Ziel-Button anhand des aria-label
        const selector = `button[aria-label="${targetMode}"]`;
        const btn = document.querySelector(selector);

        if (btn) {
            // Prüfen, ob schon aktiv (data-active Attribut)
            if (!btn.hasAttribute('data-active')) {
                 console.log(`[ViewMode] Button '${targetMode}' gefunden. Klicke...`);
                 btn.click();
                 observer.disconnect();
            } else {
                 console.log(`[ViewMode] Button '${targetMode}' ist bereits aktiv.`);
                 observer.disconnect();
            }
        }
    });

    const target = document.getElementById('root') || document.body;
    if (target) {
        observer.observe(target, { childList: true, subtree: true });
    }

} catch (e) {
    console.error("[ViewMode] Fehler: " + e);
}