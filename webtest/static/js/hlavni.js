spustJS("dalsiFunkce");
spustJS("zaklad");  
spustJS("udalosti");    
spustJS("hodnoceni"); 
spustJS("kalendar");

$(window).on('load', function() {
    //alert("haha");
    zmenHash();
});

//document.onreadystatechange


var stranka = "#stranka";
var intervalDb;

/*****************OTÁZKY*****************/
function otazkyZobraz(div, otazky) {
    var text = "";

    var tlacitka =  
        '<span class="otTlacitka">\
            <button class="tlSmazat">Smazat</button>\
            <button class="tlKostka">Kostka</button>\
            <button class="tlZadani">Zadání</button>\
        </span>';

    //onsole.log(otazky);

    $.each(otazky, function(i, o) {
        text += 
            '<div class="otazka" cislo="' + o.id + '">\
                ' + tlacitka + '\
                <span class="otId">' + o.id + '. </span>\
                <span class="otNazev">' + o.jmeno + '</span>\
                <span class="otZadani">' + o.zadaniHTML.replace("\n","<br>") + '</span>\
            </div>';
    });

    $(div).html(text);
}

function otazkyUprav(idOtazky) {
    $(stranka).load("/vzory/otazky/", nacteno);

    function nacteno() {
        $.getJSON("/json/otazky/" + idOtazky, function(otazka) {     
            $.each(otazka, foreach);
        }).fail(chybaIframe);
    }

    function foreach(i, o) {
        $(stranka).find('#otJmeno').val(o.jmeno);
        Simplemde.value(o.zadani), //soubor lista.js
        $(stranka).find('#otId').text(o.id);
        $(stranka).find('#SPRO').val(o.spravne[0]);
        $(stranka).find('#SPO1').val(o.spatne[0]);
        $(stranka).find('#SPO2').val(o.spatne[1]);
        $(stranka).find('#SPO3').val(o.spatne[2]);
        $(stranka).find('#SPO4').val(o.spatne[3]);
        $(stranka).find('#SPO5').val(o.spatne[4]);
        $(stranka).find('#SPO6').val(o.spatne[5]);
    }
}   

function otazkyPridat() {
    $(stranka).load("/vzory/otazky/",function() {
        $(stranka).find('h1#upravitOtazku').text("Přidat otázku"); 
        $(stranka).find('#otSmazat').css("display","none");
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
        postJSON(json, odpoved);
    }

    function odpoved(o) {
        if(o.status != 500) {
            hlaska(o.odpoved,8); 
            //window.location.hash = "Otazky"; 
            $.getJSON("/json/otazky/", function(json) {
                otazkyZobraz("#stranka",json.otazky);	
            });
        }
        else chybaIframe(o);
    }
}

function otazkyOdeslat() {
    var idOtazky = $(stranka).find('#otId').text();
    var ukol = "pridat";      

    if(idOtazky)
        ukol = "upravit";

    var json = {
        akce: ukol, 
        co: 'otazka',
        id: idOtazky,
        jmeno: $(stranka).find('#otJmeno').val(),
        typ: $(stranka).find('#otTyp').val(),
        zadani: Simplemde.value(), //soubor lista.js
        spravne: [
            $(stranka).find('#SPRO').val()  
        ],
        spatne: [
            $(stranka).find('#SPO1').val(),
            $(stranka).find('#SPO2').val(),
            $(stranka).find('#SPO3').val(),
            $(stranka).find('#SPO4').val(),
            $(stranka).find('#SPO5').val(),
            $(stranka).find('#SPO6').val(),                
        ]
    };

    postJSON(json, odpoved);

    function odpoved(o) {
        if(o.status != 500) {
            hlaska(o.odpoved,8); 
            window.location.hash = "Otazky";
        }
        else chybaIframe(o);
    }
}

/***************TESTY***************/
function testyOdeslat() {
    var idTestu = $(stranka).find('#ttId').text();
    var ukol = "pridat";      

    if(idTestu)
        ukol = "upravit";

    var json = {
        akce: ukol, 
        co: 'test',
        id: idTestu,
        jmeno: $(stranka).find('#ttNazev').val(),
        od: $(stranka).find('#ttOd').val(),
        do: $(stranka).find('#ttDo').val(),
        hodnoceni: null,
        pokusu: 1,
        skryty: false,           
        otazky: testyVyberOtazky()
    };

    cl(json);

    postJSON(json, odpoved);

    function odpoved(o) {
        console.log(o); 
        if(o.status != 500) {
            hlaska(o.odpoved,8); 
            //window.location.hash = "Otazky";
        }
        else chybaIframe(o);
    }
}

/*****************TESTY*******************/
function testyZobraz(json) {
    var text = "";

    var tlacitka =  
        '<span class="ttTlacitka">\
            <button class="tlZobrazit">Zobrazit</button>\
            <button class="tlSmazat">Smazat</button>\
            <button class="tlVyzkouset">Vyzkoušet</button>\
        </span>';

    $.each(json.testy, function(i, t) {
        text +=     
            '<div class="test" cislo="' + t.id + '">\
                ' + tlacitka + '\
                <span class="ttId">' + t.id + '. </span>\
                <span class="ttNazev">' + t.jmeno + '</span>\
                <br>\
                <span class="ttAutor">' + t.autor + '</span>\
                <span class="ttOd">' + t.od + '</span>\
                <span class="ttDo">' + t.do + '</span>\
            </div>';
    });
    
    $(stranka).html(text);
}

function testyUprav(idTestu) {
    $(stranka).load("/vzory/testy/", nacteno);

    function nacteno() {    
        $.getJSON("/json/testy/", zpracujJSON).fail(chybaIframe);
    }

    function zpracujJSON(json) {
        $.each(json.testy, foreach);
    }

    function foreach(i, t) {
        if(t.id==idTestu) {
            $(stranka).find('#ttNazev').val(t.jmeno);
            $(stranka).find('#ttOd').val(t.od);
            $(stranka).find('#ttDo').val(t.do);                    
        }        
    }
}

function testyVytvorit() {        
    $(stranka).load("/vzory/testy/",function(){
        nastavZnamky(1);
        var datum = dnes();
        var dalsiRok = zaRok();
        $(stranka).find('h1#upravitTest').text("Přidat test");
        $(stranka).find('#ttOd').val(datum);
        $(stranka).find('#ttDo').val(dalsiRok);
        
        $(stranka).find('#ttSmazat').css("display","none");

        $.getJSON("/json/otazky/", function(json) {
            otazkyZobraz("#ttDostupne",json.otazky);	
        }).fail(chybaIframe);
        
    });
}

function testySmazat(idTestu) {
    dialog('Smazat test?', ano, Function);

    var json = {
        akce:'smazat', 
        co:'test',
        id: idTestu
    };

    function ano() {
        postJSON(json, odpoved);
    }

    function odpoved(o) {
        if(o.status != 500) {
            hlaska(o.odpoved,5);
            $.getJSON("/json/testy/", testyZobraz)
        }
        else chybaIframe(o);
    }
}

function testyVyberOtazky() {
    var cislaOtazek = [];
    var vybrane = $(".otazka.vybrana");
    
    $.each(vybrane, function(i, v) {
        cislaOtazek[i] = v.attributes.cislo.value*1;
    });
    
    return cislaOtazek;
}


/************DATABÁZE*************/
function tabulka(tabulka,ukol){       
    var zprava = 'Smazat tabulku ' + tabulka + '?';
    if(ukol=="vysypat")
        zprava = 'Vysypat tabulku ' + tabulka + '?';

    dialog(zprava, ano, Function);

    var json = {
        akce: ukol, 
        co:'tabulka',
        nazev: tabulka
    };

    function ano() {
        postJSON(json, odpoved);
    }

    function odpoved(o) {
        if(o.status != 500)
            hlaska(o.odpoved,20); 
        else 
            chybaIframe(o);
    }
}

/*****************KALENDÁŘ*****************/
function zobrazitKalendar(umisteni) {
    var inputId = "#" + umisteni;
    var inputText = $(inputId).val();
    var hledat = inputText.match(/(\d+).(\d+).(\d+) (\d+):(\d+)/);
    var hodiny = " ";
    var kalMesic = 0;
    var kalRok = 0;

    if(!hledat) {
        var d = new Date();
        hodiny = " " + d.getHours() + ":" + d.getMinutes();
    } 

    else if(hledat.length >= 6) {
        hodiny = " " + hledat[4] + ":" + hledat[5];
        kalMesic = hledat[2];
        kalRok = hledat[3];
    }

    kalendar(umisteni, kalMesic, kalRok, function(datum){
        var text = datum.den + "." + datum.mesic + "." + datum.rok + hodiny;
        $(inputId).val(text);
    });
}


/*****************************/
function spustJS(jsSoubor) {
    var js = document.createElement("script");
    js.type = "text/javascript";
    js.src = "/static/js/" + jsSoubor + ".js";
    document.head.appendChild(js);
}