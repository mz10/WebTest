function postJSON(json, odeslano, url) {
    cl("Odeslaný JSON:");
    cl(json);  
    
    if(json && typeof json === "object")
        json = JSON.stringify(json);
    else
        json = JSON.stringify(JSON.parse(json)); 

    $.ajax({
        url: url || '/json/post/',
        type: 'POST',
        data: json,
        contentType: 'application/json; charset=utf-8',
        dataType: 'json',
        async: true,
        success: odeslano,
        error: odeslano
    }).fail(chybaIframe);
}

//odesle websocket a pocka na odpoved
//zobrazi traceback pokud je chyba na serveru
function wsJSON(json, odpoved, udalost) {
    cl("JSON k odeslání:");
    cl(json);
    
    if(json && typeof json === "object")
        json = JSON.stringify(json);
    
    if (!udalost) udalost = 'odeslatJSON';

    ws.emit(udalost, json, function(o) {
        var prijato = "";
        
        try {
            prijato = JSON.parse(o);  
        }
        catch(e) {
            prijato = "chyba: " + o;
        }

        if(prijato.odpoved)
            odpoved(prijato);

        var text = "<h3>Chyba na serveru:</h3>";

        if(prijato.traceback) {
            $.each(prijato.traceback, zobrazTraceback);  
            hlaska(text,50);
        }

        function zobrazTraceback(i, t) {
            text += t + "<br>";
        }

        cl("Odpověď ze serveru:");
        cl(prijato);
    });

}


function odpovedJSON(o) {
    cl("Přijatá odpověď:");
    cl(o);
    
    if(o.status == 400)
        hlaska(o.responseText);    
    else if(o.status != 500) {
        hlaska(o.odpoved || o.chyba,3);
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

function chybaServeru(ch) {
    var najdi = ch.responseText.match(/<title>(.*?)<\/title>/);
    var chyba = "neznámá chyba";
    
    if (najdi)
        chyba = najdi[1].replace("// Werkzeug Debugger","");

    return "Flask: " + chyba;
}

function chybaIframe(ch) {
    if(ch.responseText == "neprihlasen") {
        zobrazitPrihlaseni();
        hlaska("Nejsi příhlášen, přihlas se.",3);
    }
    else if(ch.responseText)
        hlaskaIframe(ch.responseText);
    else
        hlaska("Chyba serveru.",3);
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

function utf8encode(s) {
    for(var c, i = -1, l = (s = s.split("")).length, o = String.fromCharCode; ++i < l;
        s[i] = (c = s[i].charCodeAt(0)) >= 127 ? o(0xc0 | (c >>> 6)) + o(0x80 | (c & 0x3f)) : s[i]
    );
    return s.join("");
}

function utf8decode(s) {
    for(var a, b, i = -1, l = (s = s.split("")).length, o = String.fromCharCode, c = "charCodeAt"; ++i < l;
        ((a = s[i][c](0)) & 0x80) &&
        (s[i] = (a & 0xfc) == 0xc0 && ((b = s[i + 1][c](0)) & 0xc0) == 0x80 ?
        o(((a & 0x03) << 6) + (b & 0x3f)) : o(128), s[++i] = "")
    );
    return s.join("");
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

function nahodne(zacatek,konec) {
    return Math.floor((Math.random() * konec) + zacatek);
}

Number.prototype.zaokrouhlit = function(mista){
    mista = Math.pow(10, mista); 
    return Math.round(this * mista)/mista;
}

window.addEventListener("error", zobrazitChybu, true);

function zobrazitChybu(e) {
    if (e.message)
        hlaska(e.message + "<br>Řádek: " + e.lineno + ":" + e.colno + "<br>Soubor: " + e.filename);
    else
        hlaska("error: " + e.type + " from element: " + (e.srcElement || e.target));
}

cl = console.log;