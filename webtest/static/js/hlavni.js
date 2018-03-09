
/*****************OTÁZKY*****************/
function otazkyZobraz(div, otazky) {
    var text = "";

    var tlacitka =  
        '<span class="otTlacitka">\
            <button class="tlSmazat">Smazat</button>\
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
                <span class="otZadani">' + o.zadaniHTML.replace("\n","<br>") + '</span>\
                <div class="otOdpovedi"></div>\
            </div>';
    });

    if(div == stranka) {
        text = 
            '<h1>Otázky</h1>\
            <span class="otPridat">Přidat | </span>\
            <span class="otSmazatVsechny">Smazat všechny | </span>\
            <span class="otUpravitVsechny">Upravit všechny | </span>\
            ' + text + '\
            <div class="otPridat">Přidat</div>';
        
    }

    $(div).html(text);
}

function otazkyUprav(idOtazky) {
    $(stranka).load("/vzory/otazky/", nacteno);

    function nacteno() {
        $.getJSON("/json/otazky/" + idOtazky, function(otazka) {     
            $.each(otazka, nactiOtazku);
        }).fail(chybaIframe);
    }

    function nactiOtazku(i, o) {
        $(stranka).find('#otJmeno').val(o.jmeno);
        Simplemde.value(o.zadani), //soubor lista.js
        $(stranka).find('#otId').text(o.id);
        $(stranka).find('#otTyp').val(o.typ);
        $(stranka).find('#otBodu').val(o.bodu);

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

function otazkyUpravVsechny(e) {
    var otazky = $(".otazka");
    $.each(otazky, foreach);

    function foreach(i, o) {
        cl(o);
        var zadani = o.children[3];
        var typ = zadani.localName;      
        
        var textarea = $('<textarea />', {
            type: 'text',
            class: 'txOtazka',
            html: $(zadani).html()
        });
 
        var span = $('<span />', {
            class: 'otZadani',
            html: $(zadani).val()
        });

        if(typ=="span")
            $(zadani).replaceWith(textarea);
        else if(typ=="textarea")
            $(zadani).replaceWith(span); 
    }
}

function otazkyKostka(e) {
    var otazka = e.currentTarget.parentElement.parentElement;
    var idOtazky = otazka.attributes.cislo.value;
    var otOdpoved = $(".otazka[cislo=" + idOtazky + "] .otOdpovedi");
    var kod = "";

    $.getJSON("/json/otazky/" + idOtazky, gj).fail(chybaIframe);

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
    $(stranka).load("/vzory/otazky/",function() {
        $(stranka).find('h1#upravitOtazku').text("Přidat otázku"); 
        $(stranka).find('#otSmazat').css("display","none");
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

    var seznamSpatne = [];
    var seznamDobre = [];  
    var seznamOtevrena = [];

    $(stranka).find('input.spatne').each(function(i, o) {
        seznamSpatne[i] = $(o).val();
    });

    $(stranka).find('input.dobre').each(function(i, o) {
        seznamDobre[i] = $(o).val();
    });  

    $(stranka).find('input.otevrena').each(function(i, o) {
        seznamOtevrena[i] = $(o).val();
    });  

    if(idOtazky)
        ukol = "upravit";

    var json = {
        akce: ukol, 
        co: 'otazka',
        id: idOtazky,
        jmeno: $(stranka).find('#otJmeno').val(),
        typ: $(stranka).find('#otTyp').val(),
        bodu: $(stranka).find('#otBodu').val(),
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
        pokusu: $("#ttPokusu").val(),       
        limit: $("#ttLimit").val(),
        skryty:  $("#ttSkryt")[0].checked,          
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
    
    text = 
    '<h1>Testy</h1>\
    <div class="ttPridat">Přidat</div>\
    ' + text + '\
    <div class="ttPridat">Přidat</div>';

    $(stranka).html(text);
}

function testyVyzkouset(idTestu) {
    $.getJSON("/json/testy/" + idTestu, zpracujJSON).fail(chybaIframe);
    text = "";

    function zpracujJSON(json) {
        var test = json.test;

        text += "<h1>" + test.jmeno + "</h1>";
        $.each(test.otazky, zpracujOtazky);
        text += '<button id="odeslatTest">Odeslat</button>';
        $(stranka).html(text);
    }

    function zpracujOtazky(i, o) {
        odpovedi = "";
        
        $.each(o.odpovedi, function(y, odpoved){

            if(odpoved == "_OTEVRENA_")
                odpoved = '<input type="text" class="odpovedOt">';
            else
                odpoved = "<li class='odpoved' >" + odpoved + "</li>";

            odpovedi += odpoved;      
        });  
        
        text +=
            "<h2 cislo='" + o.id + "'>" + o.jmeno + "</h1>\
            <div class='zadani'>" + o.zadani + "</div>\
            <ol type='a' class='odpovedi' vyber='1' otazka='" + o.id + "'>" + odpovedi + "</ol>";
    }
}

function testyVyzkouset2(idTestu) {
    $.getJSON("/json/testy/" + idTestu, zpracujJSON).fail(chybaIframe);
    text = "";

    function zpracujJSON(json) {
        var test = json.test;

        text += "<h1>" + test.jmeno + "</h1>";
        $.each(test.otazky, zpracujOtazky);
        $(stranka).html(text);
    }

    function zpracujOtazky(i, o) {
        odpovedi = "";
        
        $.each(o.odpovedi, function(y, odpoved){
            odpovedi += "<li class='odpoved'>" + odpoved + "</li>";        
        });  
        
        text +=
            "<h2 cislo='" + o.id + "'>" + o.jmeno + "</h1>\
            <div class='zadani'>" + o.zadani + "</div>\
            <ol type='a' class='odpovedi'>" + odpovedi + "</ol>";
    }
}

function testyUprava(akce,idTestu) {
    //kód je asynchroní!

    $(stranka).load("/vzory/testy/", nacteno);

    function nacteno() { 
        nastavZnamky(1);  
        $.getJSON("/json/testy/", zpracujJSON).fail(chybaIframe);
    }

    var seznamOtazek = [];

    function zpracujJSON(json) {
        if(akce == "uprav")
            $.each(json.testy, foreach);
        else if(akce == "pridat")
            pridatTest();
        
        nactiOtazky();
    }

    function pridatTest() {
        var datum = dnes();
        var dalsiRok = zaRok();
        $(stranka).find('h1#upravitTest').text("Přidat test");
        $(stranka).find('#ttSmazat').hide();
        $(stranka).find('#ttOd').val(datum);
        $(stranka).find('#ttDo').val(dalsiRok);        
    }

    function foreach(i, t) {
        if(t.id==idTestu) {
            $(stranka).find('#ttNazev').val(t.jmeno);
            $(stranka).find('#ttId').text(t.id); 
            $(stranka).find('#ttOd').val(t.od);
            $(stranka).find('#ttDo').val(t.do); 
            $(stranka).find('#ttPokusu').val(t.pokusu); 
            $(stranka).find('#ttLimit').val(t.limit); 
            $(stranka).find('#ttLimit').checked = t.skryty;
            seznamOtazek = t.otazky;
            return;           
        }        
    }

    function nactiOtazky() {
        $.getJSON("/json/otazky/", function(json) {
            otazkyZobraz("#ttDostupne",json.otazky);
            otazkyZobraz("#ttZvolene",json.otazky);	   
            
            var dostupne = $("#ttDostupne")[0].childNodes;
            var zvolene = $("#ttZvolene")[0].childNodes;

            $.each(dostupne, zobrazOtazky); 
            $.each(zvolene, skryjOtazky); 
        
        }).fail(chybaIframe);
    }

    function zobrazOtazky(i, otazka) {
        if (jeVSeznamu(otazka.attributes.cislo.value))
            otazka.style.display = "none";
    }

    function skryjOtazky(i, otazka) {
        if (!jeVSeznamu(otazka.attributes.cislo.value))      
            otazka.style.display = "none";
    }

    function jeVSeznamu(id) {
        var vysledek = false;
        $.each(seznamOtazek, function(i, idO) {
            if(id==idO) {
                vysledek = true;
                return false;
            }
        });
        return vysledek;
    }
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
    var vybrane = $("#ttZvolene .otazka:visible");
    
    $.each(vybrane, function(i, v) {
        cislaOtazek[i] = v.attributes.cislo.value*1;
    });
    
    return cislaOtazek;
}

function testyVymenOtazky() {
    var dostupne = $("#ttDostupne .otazka.vybrana");
    var zvolene = $("#ttZvolene .otazka.vybrana");

    $.each(dostupne, function(i, otazka) { skryt(otazka,"#ttZvolene") });
    $.each(zvolene,  function(i, otazka) { skryt(otazka,"#ttDostupne") });

    function skryt(otazka, div) {
        $(otazka).removeClass("vybrana");
        otazka.style.display = "none";
        idOtazky = otazka.attributes.cislo.value;
        $(div + " .otazka[cislo=" + idOtazky + "]").show();        
    }

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





/*************slovnik **********/

function slovnik() {
    $(stranka).load("/static/slovnik.html");
} 


function slovnikOdeslat() {
    var json = {
        akce: "pridat", 
        co: 'slovnik',
        slovo1: $(stranka).find('#slJazyk1').val(),
        slovo2: $(stranka).find('#slJazyk2').val(),
        kategorie: $(stranka).find('#slKategorie').val(),
        jazyk: $(stranka).find('#slTyp').val()
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