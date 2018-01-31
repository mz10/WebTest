spustJS("dalsiFunkce"); 
spustJS("hlavni");  
spustJS("zaklad");    
spustJS("hodnoceni"); 
spustJS("kalendar");

window.onload = function() {
    spustJS("udalosti"); 
    zmenHash();
}

var stranka = "#stranka";
var intervalDb;

function spustJS(jsSoubor) {
    var js = document.createElement("script");
    js.type = "text/javascript";
    js.src = "/static/js/" + jsSoubor + ".js";
    js.setAttribute("defer", "defer");
    document.head.appendChild(js);
}