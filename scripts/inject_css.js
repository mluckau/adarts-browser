try {
    (function() {
        let css = document.createElement('style');
        css.type = 'text/css';
        css.id = "{name}";
        document.head.appendChild(css);
        css.innerText = `{css}`;
    })()
}
catch (error) {
    console.log('Error during CSS injection:', error);
}
