try {
    console.log("[Autologin] Starte robustes Polling...");

    function setNativeValue(element, value) {
        const lastValue = element.value;
        element.value = value;
        const event = new Event("input", { target: element, bubbles: true });
        // React 15/16 hack
        const tracker = element._valueTracker;
        if (tracker) {
            tracker.setValue(lastValue);
        }
        element.dispatchEvent(event);
    }

    var attempts = 0;
    var loginInterval = setInterval(function() {
        attempts++;
        
        var userField = document.getElementById('username');
        var passField = document.getElementById('password');
        var submitBtn = document.getElementById('kc-login');

        if (userField && passField && submitBtn) {
            console.log("[Autologin] Elemente gefunden. Setze Werte...");
            clearInterval(loginInterval);

            // React-freundliches Setzen der Werte
            
            // Benutzername
            const nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, "value").set;
            nativeInputValueSetter.call(userField, '{username}');
            userField.dispatchEvent(new Event('input', { bubbles: true }));
            
            // Passwort
            nativeInputValueSetter.call(passField, '{password}');
            passField.dispatchEvent(new Event('input', { bubbles: true }));

            // Checkbox "Angemeldet bleiben"
            var remember = document.getElementById('rememberMe');
            if (remember && !remember.checked) {
                remember.click();
            }

            console.log("[Autologin] Warte kurz und klicke...");
            setTimeout(function() {
                submitBtn.click();
            }, 800); // Etwas mehr Zeit geben
        }

        if (attempts > 120) { // 60 Sekunden
            console.log("[Autologin] Timeout.");
            clearInterval(loginInterval);
        }
    }, 500);

} catch (e) {
    console.error("[Autologin] Exception: " + e);
}