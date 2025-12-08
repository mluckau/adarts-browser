try {
    (function() {
        let img = document.createElement('img');
        img.src = '{logo_url}';
        img.classList.add("logo-bottom-right");
        document.body.appendChild(img);
    })()
}
catch (error) {
    console.log('Mixed Content Error during logo injection:', error);
}
