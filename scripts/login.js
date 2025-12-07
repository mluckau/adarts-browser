try {
    const observer = new MutationObserver(() => {
        let user = document.querySelector('#username');
        let pass = document.querySelector('#password');
        let rmb = document.querySelector('input[id="rememberMe"]');
        let btn = document.querySelector('input[id="kc-login"]');
        if (user && pass && rmb && btn) {
            console.log('Benötigte Felder gefunden, Autologin wird ausgeführt.');
            user.value = '{username}';
            pass.value = '{password}';
            rmb.checked = true;
            btn.click();
            observer.disconnect(); // Beobachtung stoppen
        }
    });

    observer.observe(document.body, { childList: true, subtree: true });
} catch (error) {
    console.error('Fehler im Autologin-Skript:', error);
}
