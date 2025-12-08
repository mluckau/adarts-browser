try {
    const observer = new MutationObserver(() => {
        // Versuche verschiedene Selektoren für Benutzername und Passwort
        let user = document.querySelector('#username') || document.querySelector('input[name="username"]') || document.querySelector('input[type="email"]');
        let pass = document.querySelector('#password') || document.querySelector('input[name="password"]') || document.querySelector('input[type="password"]');
        
        // Suche nach dem Login-Button (verschiedene Varianten)
        let btn = document.querySelector('input[id="kc-login"]') || document.querySelector('button[type="submit"]') || document.querySelector('button#kc-login');

        // Optional: "Angemeldet bleiben" Checkbox
        let rmb = document.querySelector('input[id="rememberMe"]') || document.querySelector('input[name="rememberMe"]');

        if (user && pass && btn) {
            console.log('Login-Formular gefunden. Führe Autologin aus...');
            
            // Werte setzen
            user.value = '{username}';
            user.dispatchEvent(new Event('input', { bubbles: true })); // Event feuern für Frameworks (React/Vue etc.)
            
            pass.value = '{password}';
            pass.dispatchEvent(new Event('input', { bubbles: true }));

            if (rmb) {
                rmb.checked = true;
                rmb.dispatchEvent(new Event('change', { bubbles: true }));
            }

            // Kurze Verzögerung vor dem Klick, um sicherzustellen, dass Events verarbeitet wurden
            setTimeout(() => {
                btn.click();
            }, 500);

            observer.disconnect(); // Beobachtung stoppen
        }
    });

    observer.observe(document.body, { childList: true, subtree: true });
} catch (error) {
    console.error('Fehler im Autologin-Skript:', error);
}