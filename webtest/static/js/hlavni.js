
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
            $.each(otazka, foreach);
        }).fail(chybaIframe);
    }

    function foreach(i, o) {
        $(stranka).find('#otJmeno').val(o.jmeno);
        Simplemde.value(o.zadani), //soubor lista.js
        $(stranka).find('#otId').text(o.id);
        $(stranka).find('#otTyp').val(o.typ);
        $(stranka).find('#SPRO').val(o.spravneZadano[0]);
        $(stranka).find('#SPO1').val(o.spatneZadano[0]);
        $(stranka).find('#SPO2').val(o.spatneZadano[1]);
        $(stranka).find('#SPO3').val(o.spatneZadano[2]);
        $(stranka).find('#SPO4').val(o.spatneZadano[3]);
        $(stranka).find('#SPO5').val(o.spatneZadano[4]);
        $(stranka).find('#SPO6').val(o.spatneZadano[5]);
    }
}   

function otazkyUpravVsechny(e) {
    var otazky = $(".otazka");
    $.each(otazky, foreach);

    function foreach(i, o) {
        cl(o);
        var input = $("<input />");
        var zadani = o.children[2];
        $(zadani).replaceWith(input);
        var text = $(zadani).html();
        input.val(text);

        //$(zadani).replaceWith(input);
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

        kod+= o.spravne[0] + "<br>";
        kod+= o.spatne[0] + "<br>";
        kod+= o.spatne[1] + "<br>";
        kod+= o.spatne[2] + "<br>";
        kod+= o.spatne[3] + "<br>";
        kod+= o.spatne[4] + "<br>";
        kod+= o.spatne[5] + "<br>";   
        
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

    //cl(json);

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