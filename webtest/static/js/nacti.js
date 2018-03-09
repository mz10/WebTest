spustJS("dalsiFunkce"); 
spustJS("hlavni");  
spustJS("zaklad");    
spustJS("hodnoceni"); 
spustJS("kalendar");

window.onload = function() {
    spustJS("udalosti"); 
    zmenHash();

    document.getElementById("obnovJS").onclick = function() {
        $(document).off(); //odstrani udalosti
        obnovJS("dalsiFunkce"); 
        obnovJS("hlavni");  
        obnovJS("zaklad");    
        obnovJS("hodnoceni"); 
        obnovJS("kalendar");
        obnovJS("udalosti"); 
    }
}

var stranka = "#stranka";
var intervalDb;

function spustJS(jsSoubor) {
    var cas = new Date().getTime();
    var js = document.createElement("script");
    js.type = "text/javascript";
    js.src = "/static/js/" + jsSoubor + ".js?" + cas;
    js.setAttribute("defer", "defer");
    document.head.appendChild(js);
}

function obnovJS(jsSoubor) {
    var cas = new Date().getTime();
    var js = document.createElement("script");
    odebratJS(jsSoubor);
    js.type = "text/javascript";
    js.src = "/static/js/" + jsSoubor + ".js?" + cas;
    js.setAttribute("defer", "defer");
    document.head.appendChild(js);
}

function odebratJS(jsSoubor){
    var js = document.getElementsByTagName('script');
    
    for (var i = js.length; i >= 0; i--) { 
        if (js[i] && js[i].getAttribute('src') != null 
        && js[i].getAttribute('src').indexOf(jsSoubor + ".js") != -1)
            js[i].parentNode.removeChild(js[i]); 
    }
}