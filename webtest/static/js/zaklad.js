function postJSON(json, odeslano, url) {
    if(json && typeof json === "object")
        json = JSON.stringify(json);

    $.ajax({
        url: url || '/json/post/',
        type: 'POST',
        data: json,
        contentType: 'application/json; charset=utf-8',
        dataType: 'json',
        async: true,
        success: odeslano,
        error: odeslano
    });
}

function odpovedJSON(o) {
    console.log(o); 
    if(o.status == 400)
        hlaska(o.responseText);    
    else if(o.status != 500) {
        hlaska(o.odpoved || o.chyba,8);
    }
    else chybaIframe(o);
} 

function smazIntervaly(){
    var id = window.setTimeout(null,0);
    while (id--){
        window.clearTimeout(id);
    }
}

function smazIntervaly2() {
    for(var i=0; i<intervaly.length; i++){
        clearTimeout(intervaly[i]);
    }
    intervaly = [];
}

//funkce na zjisteni prvku - zjednoduseno

//prvek
function pr(prvek) {
    return $(stranka).find(prvek);
}

//prvek -> hodnota
function ph(prvek) {
    return $(stranka).find(prvek).val();
}

//prvek -> text
function pt(prvek) {
    return $(stranka).find(prvek).text();
}

function isInArray(hodnota, pole) {
    return pole.indexOf(hodnota) > -1;
}


function zmenHash() {
    var hash = nazevStranky();
    if(intervalDb) clearInterval(intervalDb);
    
    //if(!nacti) return;

    if(hash=="DB") {
        $(stranka).load("/tabulky/");
        intervalDb = setInterval(function() {
            $(stranka).load("/tabulky/");
        }, 3000);
    }
    else if(hash=="Otazky"){
        $.getJSON("/json/otazky/", function(json) {
            otazkyZobraz("#stranka",json.otazky);	
        }).fail(chybaIframe);
    }
    else if(hash=="Testy")
        $.getJSON("/json/testy/", testyZobraz).fail(chybaIframe);
    else if(hash=="Testy2")
        $.getJSON("/json/testy/", testyStudentZobraz).fail(chybaIframe);    
    else if(hash=="Nahrat")
        $(stranka).load("/upload/");  
    else if(hash=="TestyVytvorit")
        testyUprava("pridat");
    else if(hash=="OtazkyPridat")
        otazkyPridat();
    else if(hash=="Slovnik")
        slovnik();
    else if(hash=="Tridy")
        tridyZobraz();     
    else if(hash=="Studenti")
        osobaPridat("student");   
    else if(hash=="Vysledky")
        vysledkyZobraz();            
}

function chybaServeru(ch) {
    var najdi = ch.responseText.match(/<title>(.*?)<\/title>/);
    var chyba = "neznámá chyba";
    
    if (najdi)
        chyba = najdi[1].replace("// Werkzeug Debugger","");

    return "Flask: " + chyba;
}

function chybaIframe(ch) {
    hlaskaIframe(ch.responseText);
    //cl(chyba);
}

function dialog(zprava, ano, ne) {    
    var div = document.createElement("div");
    div.className = "dialog";
    div.style.display = "block";
    var content = document.createElement("div");
    content.innerHTML = zprava;
    var potvrdit = document.createElement("button");
    potvrdit.innerHTML = "Ano";
    var zrusit = document.createElement("button");
    zrusit.innerHTML = "Ne";

    div.appendChild(content);
    div.appendChild(potvrdit);
    div.appendChild(zrusit );
    document.body.appendChild(div);

    potvrdit.onclick = function() {
        document.body.removeChild(div);
        ano();
    }

    document.onkeyup = function(e) {
        if (e.keyCode == 13) {//enter
            document.onkeyup = null;            
            document.body.removeChild(div);
            ano();
        }
    }

    zrusit.onclick = function() {
        document.body.removeChild(div);
        ne();
    };
}

function hlaska(text, cas) {
    var casovac;
    var div = document.createElement("div");   
    div.innerHTML = text;
    div.id = "hlaska";
    div.className = "zobrazit";       
    document.body.appendChild(div);   
    
    clearTimeout(casovac);

    div.onclick = function() {
        document.body.removeChild(div);
    }

    if(cas>0) {
        casovac = setTimeout(function() {
            if (document.contains(div))
                document.body.removeChild(div);
        }, cas * 1000);
    }
}

function hlaskaIframe(html) {
    var div = document.createElement("div");   
    div.id = "hlaskaIframe";
    div.className = "zobrazit";          

    var ifrm = document.createElement("iframe");
    
    document.body.appendChild(div);
    div.appendChild(ifrm);

    ifrm.contentWindow.document.open();
    ifrm.contentWindow.document.write(html);
    ifrm.contentWindow.document.close();    

    div.onclick = function() {
        document.body.removeChild(div);
    }
}

function Nahodne(zacatek,konec) {
    return Math.floor((Math.random() * konec) + zacatek);
}

window.onhashchange = zmenHash;
window.addEventListener("error", zobrazitChybu, true);

function zobrazitChybu(e) {
    if (e.message)
        hlaska(e.message + "<br>Řádek: " + e.lineno + ":" + e.colno + "<br>Soubor: " + e.filename);
    else
        hlaska("error: " + e.type + " from element: " + (e.srcElement || e.target));
}

cl = console.log;