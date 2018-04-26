spustJS("dalsiFunkce"); 
spustJS("hlavni");
spustJS("tabulky");  
spustJS("otazky"); 
spustJS("testy"); 
spustJS("vysledky");
spustJS("zaklad");    
spustJS("hodnoceni");
spustJS("kalendar");

//web sockety - spojeni se navaze az po prihlaseni
ws = null;

window.onload = function() {
    //hlaska("stranka nactena");
    spustJS("udalosti");
    prihlasitUzivatele();
    zmenHash();
    menuNahore();
       
    //navaze WS spojeni pokud je uz uzivatel prihlasen pres http
    if ($("#odhlasit").length > 0)
        wsUdalosti();

    mathjax1();

    document.getElementsByClassName("logo2")[0].onclick = function() {
        console.log("Obnovit JS");
        $(document).off(); //odstrani puvodni udalosti
        obnovJS("dalsiFunkce"); 
        obnovJS("hlavni"); 
        obnovJS("otazky"); 
        obnovJS("testy");  
        obnovJS("vysledky"); 
        obnovJS("tabulky");       
        obnovJS("zaklad");    
        obnovJS("hodnoceni"); 
        obnovJS("kalendar");
        obnovJS("udalosti"); 
    }
}

var stranka = "#stranka";
var intervaly = [];
var intervalDb;

function spustJS(jsSoubor) {
    var cas = new Date().getTime();
    var js = document.createElement("script");
    js.type = "text/javascript";
    js.src = "./static/js/" + jsSoubor + ".js?" + cas;
    js.setAttribute("defer", "defer");
    document.head.appendChild(js);
}

function obnovJS(jsSoubor) {
    var cas = new Date().getTime();
    var js = document.createElement("script");
    odebratJS(jsSoubor);
    js.type = "text/javascript";
    js.src = "./static/js/" + jsSoubor + ".js?" + cas;
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

function websocket() {
    /*
    ws = io.connect(location.protocol + '//' + document.domain + ':' + location.port + "/ws", {
        upgrade: false,
        transports: ['websocket']        
    });   
*/

    ws = io.connect(location.protocol + '//' + document.domain + ':' + location.port + "/ws"); 
}


function mathjax1() {
    try {
        MathJax.Hub.Config({
            tex2jax: {inlineMath: [["$","$"],["\\(","\\)"]]},
            displayAlign: "left"
        });
    }
    catch(e) { 
        hlaska("MathJax není načten. Zkontrolujte připojení k internetu.",2); 
    }
}

function mathjax() {
    try {
        MathJax.Hub.Queue(["Typeset",MathJax.Hub])
    }
    catch(e) { 
        hlaska("MathJax není načten. Zkontrolujte připojení k internetu.",1); 
    }
}