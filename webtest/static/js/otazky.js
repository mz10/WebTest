function otazkyZobraz(div, otazky) {
    var text = "";

    var tlacitka =  
        '<span class="otTlacitka">\
            <button class="tlSmazat">Smazat</button>\
            <button class="tlZadani">Zadání</button>\
            <button class="tlKostka">Kostka</button>\
            <button class="tlZobrazOdpovedi">Odpovědi</button>\
        </span>';

    //onsole.log(otazky);

    $.each(otazky, function(i, o) {
        text += 
            '<div class="otazka" cislo="' + o.id + '">\
                ' + tlacitka + '\
                <span class="otId">' + o.id + '. </span>\
                <span class="otNazev">' + o.jmeno + '</span>\
                <input class="otPocet" value="1" type="text">\
                <span class="otZadani">' + o.zadaniHTML.replace("\n","<br>") + '</span>\
                <div class="otOdpovedi"></div>\
            </div>';
    });

    if(div == stranka) {
        text = 
            '<h1>Otázky</h1>\
            <span class="otPridat">Přidat | </span>\
            <span class="otSmazatVsechny">Smazat všechny | </span>\
            ' + text + '\
            <div class="otPridat">Přidat</div>';
        
    }

    $(div).html(text);
    mathjax();
}

function otazkyUprav(idOtazky) {
    $(stranka).load("./vzory/otazky/", nacteno);

    function nacteno() {
        $.getJSON("./json/otazky/" + idOtazky, function(otazka) {     
            $.each(otazka, nactiOtazku);
        }).fail(chybaIframe);
    }

    function nactiOtazku(i, o) {
        Simplemde.value(o.zadani), //soubor lista.js
        pr('#otJmeno').val(o.jmeno);
        pr('#otId').text(o.id);
        pr('#otTyp').val(o.typ);
        pr('#otBodu').val(o.bodu);
        pr('#otTolerance').val(o.tolerance);
        pr('#otZaokrouhlit').val(o.zaokrouhlit);
        pr('#otVyhodnotit').val(o.hodnotit);

        $(o.spravneZadano).each(function(i, o)  {vlozitOdpoved("dobre",o); });
        $(o.spatneZadano).each(function(i, o)   {vlozitOdpoved("spatne",o); });
        $(o.otevrenaZadano).each(function(i, o) {vlozitOdpoved("otevrena",o); });        

        vlozitOdpoved("seda","");
    }
}   

function vlozitOdpoved(trida, text) {   
    var div = '<div class="inputLista">\
                <input class="' + trida + '" type="text" value="' + text + '">\
                <span class="inputTlacitka">\
                    <span class="inputSpatna">o</span>\
                    <span class="inputSpravna">o</span>\
                    <span class="inputSmazat">x</span>\
                </span>\
            </div>';
    
    $("#vlozitOtazky").append(div);        
}

function otazkySmazatVsechny(e) {
    dialog('Smazat všechny otázky?', ano, Function);
    
    var json = {
        akce:'smazatVsechny', 
        co:'otazka',
    };

    function ano() {
        postJSON(json, odpovedJSON);
    }
}

function otazkyKostka(e) {
    var otazka = e.currentTarget.parentElement.parentElement;
    var idOtazky = otazka.attributes.cislo.value;
    var otOdpoved = $(".otazka[cislo=" + idOtazky + "] .otOdpovedi");
    var kod = "";

    $.getJSON("./json/otazky/" + idOtazky, gj).fail(chybaIframe);

    function gj(json) {
        cl(json.otazka);
        var o = json.otazka;
        
        var zadani = o.zadaniHTML;
        $(".otazka[cislo=" + idOtazky + "] .otZadani").html(zadani);

        $(o.spravne).each(function(i, o) {
            kod += '<div class="odDobre">' + o + '</div>';
        });

        $(o.spatne).each(function(i, o) {
            kod += '<div class="odSpatne">' + o + '</div>';
        });
  
        $(o.otevrena).each(function(i, o) {
            kod += '<div class="odOtevrena">' + o + '</div>';
        });

        otOdpoved.html(kod);
        mathjax();
    }
}

function otazkyZobrazOdpovedi(e) {
    var otazka = e.currentTarget.parentElement.parentElement;
    var idOtazky = otazka.attributes.cislo.value;
    var otOdpoved = $(".otazka[cislo=" + idOtazky + "] .otOdpovedi");

    if(otOdpoved.text() == "") {
        otazkyKostka(e);
    }

    otOdpoved.toggle();
}

function otazkyPridat() {
    $(stranka).load("./vzory/otazky/",function() {
        pr('h1#upravitOtazku').text("Přidat otázku"); 
        pr('#otSmazat').css("display","none");
        vlozitOdpoved("otevrena","");
        vlozitOdpoved("seda","");   
    });
}

function otazkySmazat(idOtazky) {
    dialog('Smazat otázku?', ano, Function);

    var json = {
        akce:'smazat', 
        co:'otazka',
        id: idOtazky
    };

    function ano() {
        postJSON(json, odpovedJSON);
    }
}

function otazkyOdeslat() {
    var idOtazky = pr('#otId').text();
    var ukol = "pridat";      

    var seznamSpatne = [];
    var seznamDobre = [];  
    var seznamOtevrena = [];

    pr('input.spatne').each(function(i, o) {
        seznamSpatne[i] = $(o).val();
    });

    pr('input.dobre').each(function(i, o) {
        seznamDobre[i] = $(o).val();
    });  

    pr('input.otevrena').each(function(i, o) {
        var hodnota = $(o).val();
        if(hodnota != "")
            seznamOtevrena[i] = $(o).val();
    }); 
    
    var pocet = seznamSpatne.length + seznamDobre.length + seznamOtevrena.length;

    if(pocet == 0) {
        hlaska("Aspoň 1 odpověď musí být zadána.",3);
        return;
    }

    if (ph('#otJmeno') == "") {
        hlaska("Otázka musí mít jméno!",3);
        return;  
    }

    if(idOtazky)
        ukol = "upravit";

    var json = {
        akce: ukol, 
        co: 'otazka',
        id: idOtazky,
        jmeno: ph('#otJmeno'),
        bodu: ph('#otBodu') || 0,
        hodnotit: ph('#otVyhodnotit')*1 || 1,
        tolerance: ph('#otTolerance')*1,
        zaokrouhlit: ph('#otZaokrouhlit')*1,
        zadani: Simplemde.value(), //soubor lista.js
        spravne: seznamDobre,
        spatne: seznamSpatne,
        otevrena: seznamOtevrena
    };

    cl(json);

    postJSON(json, odpoved);

    function odpoved(o) {
        if(o.status != 500) {
            hlaska(o.odpoved,8); 
            prejit("Otazky");
        }
        else chybaIframe(o);
    }
}

function otazkyVlozit(e) {
    var input = e.currentTarget;
    var hodnota = input.value;    
    var inputy = e.currentTarget.parentElement.parentElement.children;
    var posledni = e.currentTarget.parentElement.parentElement.lastElementChild;
    var prvni = inputy[0].children[0];

    cl(e.currentTarget);

    //pokud neni input prazdny, oznac jako spatnou
    if(input.className == "seda" && hodnota.length >= 1)
        $(input).removeClass().addClass("spatne");

    //pokud neni posledni input prazdny, vloz ho
    if(posledni.children[0].className != "seda")
        vlozitOdpoved("seda","");

    //pokud je input prazdny, bude sedy
    if(hodnota.length == 0)
        $(input).removeClass().addClass("seda");

    //pokud je input prazdny, smaz posledni input
    if(hodnota.length == 0 && posledni.children[0].className == "seda") {
        $(posledni).remove();
    }

    if(inputy.length > 2) {
        prvni.className = "dobre";
        prvni.placeholder = "Správně"
    }

    else if(inputy.length <= 2) {
        prvni.className = "otevrena";
        prvni.placeholder = "Otevřená"
    }    
}