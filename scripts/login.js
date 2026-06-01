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
        
        // Heuristische Erkennung der Login-Elemente (zukunftssicher)
        var passField = document.querySelector('input[type="password"]');
        var userField = null;
        var submitBtn = null;

        if (passField) {
            var container = passField.closest('form') || document;
            
            userField = container.querySelector('input[autocomplete="username"]') ||
                        container.querySelector('input[name="username"]') ||
                        container.querySelector('input[name="email"]') ||
                        container.querySelector('input[type="email"]') ||
                        container.querySelector('input[type="text"]') ||
                        document.getElementById('username');
            
            submitBtn = container.querySelector('button[type="submit"]') ||
                        container.querySelector('input[type="submit"]') ||
                        document.getElementById('kc-login');

            if (!submitBtn) {
                var buttons = container.querySelectorAll('button');
                for (var i = 0; i < buttons.length; i++) {
                    var txt = buttons[i].innerText.toLowerCase();
                    if (txt.includes('login') || txt.includes('signin') || txt.includes('anmelden') || txt.includes('inloggen') || txt.includes('sign-in')) {
                        submitBtn = buttons[i];
                        break;
                    }
                }
            }
        }

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