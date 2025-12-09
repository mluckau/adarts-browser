// Custom CSS Injector with Live-Update support
(function() {
    var styleId = 'autodarts-browser-custom-style';
    var styleElement = document.getElementById(styleId);

    if (!styleElement) {
        styleElement = document.createElement('style');
        styleElement.id = styleId;
        document.head.appendChild(styleElement);
        console.log('[Autodarts Browser] Custom CSS element created.');
    } else {
        console.log('[Autodarts Browser] Updating existing Custom CSS.');
    }

    // The template variable {css_b64} will be replaced by Python with Base64 string
    try {
        var b64 = "{css_b64}".trim(); // Remove potential whitespace
        // Standard trick to decode UTF-8 from Base64 in browser
        var cssContent = decodeURIComponent(Array.prototype.map.call(window.atob(b64), function(c) {
            return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
        }).join(''));
        styleElement.textContent = cssContent;
    } catch (e) {
        console.error('[Autodarts Browser] Failed to decode CSS: ' + e);
    }
})();