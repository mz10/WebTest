﻿function testyOdeslat() {
    var tridy = [];

    $.each(pr(".ttTridy"), function(i, t) {
        tridy.push($(t).val()*1);
    });     
    
    var idTestu = pt('#ttId');
    var ukol = "pridat";      

    if(idTestu) ukol = "upravit";

    if (ph('#ttNazev') == "") {
        hlaska("Test musí mít jméno!",3); 
        return;
    }

    var seznamOtazek = testyVyberOtazky();

    if(seznamOtazek.length == 0) {
        hlaska("V testu musí být aspoň 1 otázka!",3); 
        return;
    }
    
    var json = {
        akce:       ukol, 
        co:         'test',
        id:         idTestu,
        jmeno:      ph('#ttNazev'),
        od:         ph('#ttOd'),
        do:         ph('#ttDo'),
        typHodnoceni:  ph("#hodnoceniTyp option:selected")*1,
        hodnoceni:  zjistitHodnoceni(),
        pokusu:     ph("#ttPokusu") || 1,       
        limit:      ph("#ttLimit") || "5",
        skryty:     $("#ttSkryt")[0].checked,  
        nahodny:    $("#ttVyber")[0].checked, 
        omezit:     ph("#ttOmezeni") || 0,
        otazky:     seznamOtazek,
        tridy:      tridy
    };

    postJSON(json, odpovedJSON);
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
            '<div class="test ucitel" cislo="' + t.id + '">\
                ' + tlacitka + '\
                <span class="ttId">' + t.id + '. </span>\
                <span class="ttNazev">' + t.jmeno + '</span>\
                <br>\
                <span class="ttAutor">' + t.autor + '</span>\
                <span class="ttOd">' + t.od + '</span>\
                <span class="ttDo">' + t.do + '</span>\
                <span class="ttLimit">Čas: ' + t.limit + ' min</span>\
            </div>';
    });
    
    text = 
    '<h1>Testy</h1>\
    <div class="ttPridat">Přidat</div>\
    ' + text + '\
    <div class="ttPridat">Přidat</div>';

    $(stranka).html(text);
}

function testyStudentZobraz(json) {
    var text = "";

    $.each(json.testy, function(i, t) {
        text +=     
            '<div class="test student" cislo="' + t.id + '">\
                <span class="ttNazev">' + t.jmeno + '</span>\
                <br>\
                <span class="ttAutor">' + t.autor + '</span>\
                <span class="ttOd">' + t.od + '</span>\
                <span class="ttDo">' + t.do + '</span>\
                <span class="ttLimit">Čas: ' + t.limit + ' min</span>\
            </div>';
    });

    $(stranka).html(text);
}

function testyVyzkouset(idTestu,ucitel) {
    var adresa = "./json/student/testy/";

    if(ucitel)
        adresa = "./json/testy/vyzkouset/";

    $.getJSON(adresa + idTestu, zpracujJSON).fail(chybaIframe);
    text = "";
    //vymazat vsechny odpocty
    smazIntervaly();

    function zpracujJSON(json) {
        if(json.info) {
            hlaska(json.info,3);
            return;
        }

        var test = json.test;

        text += "<h1>" + test.jmeno + "</h1>";
        text += "<div id='odpocet'> </div>";
        $.each(test.otazky, zpracujOtazky);
        
        mathjax();
        //5 sekund jako rezerva
        limit = (test.limit*60)-5;

        var interval = null;

        if(!ucitel) {
            text += '<button id="odeslatTest" value="' + test.id + '">Odeslat</button>';
            interval = odpocet("#odpocet",limit, konecTestu);
        }
        else
            text = `<button id='vygenerovat' value='${idTestu}'>Vygenerovat</button>` + text;

        $(stranka).html(text);  
    }

    function konecTestu() {
        pr("#odpocet").text("Čas vypršel!!!");
        testyVyhodnotit();
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
            <ol type='a' class='odpovedi' vyber=" + o.spravnych + " otazka='" + o.id + "'>" + odpovedi + "</ol>";
    }
}

function testyUprava(akce,idTestu) {
    //kód je asynchroní!

    $(stranka).load("./vzory/testy/", nacteno);

    function nacteno() {
        nastavZnamky("rovnomerne",0);  
        $.getJSON("./json/testy/", zpracujJSON).fail(chybaIframe);
        
        $.getJSON("./json/tridy/", function(json) {     
            $.each(json.tridy, nactiTridy);
            $(".ttTridy").append(option);
        }).fail(chybaIframe);
    }

    var seznamOtazek = [];
    var seznamTridy = [];

    function zpracujJSON(json) {
        if(akce == "uprav")
            $.each(json.testy, zpracujTest);
        else if(akce == "pridat")
            pridatTest();
        
        nactiOtazky();
    }

    function pridatTest() {
        var datum = dnes();
        var dalsiRok = zaRok();
        pr('h1#upravitTest').text("Přidat test");
        pr('#ttSmazat').hide();
        pr('#ttOd').val(datum);
        pr('#ttDo').val(dalsiRok); 

    }

    function zpracujTest(i, t) {
        if(t.id==idTestu) {            
            pr('#ttNazev').val(t.jmeno);
            pr('#ttId').text(t.id); 
            pr('#ttOd').val(t.od);
            pr('#ttDo').val(t.do); 
            pr('#ttPokusu').val(t.pokusu); 
            pr('#ttLimit').val(t.limit); 
            pr('#ttOmezeni').val(t.omezit); 
            pr('#hodnoceniTyp').val(t.typHodnoceni);           
            pr('#ttSkryt')[0].checked = t.skryty;
            pr('#ttVyber')[0].checked = t.nahodny;
            nastavZnamky(null,null,t.hodnoceni);
            seznamOtazek = t.otazky;
            $.each(t.tridy, zobrazTridy);
            return;           
        }        
    }

    function nactiOtazky() {
        $.getJSON("./json/otazky/", function(json) {
            otazkyZobraz("#ttDostupne",json.otazky);
            otazkyZobraz("#ttZvolene",json.otazky);	   
            
            var dostupne = $("#ttDostupne")[0].childNodes;
            var zvolene = $("#ttZvolene")[0].childNodes;

            $.each(dostupne, dostupneOtazky); 
            $.each(zvolene, zvoleneOtazky); 
        
        }).fail(chybaIframe);
    }
    
    function dostupneOtazky(i, otazka) {
        var id = otazka.attributes.cislo.value;

        $.each(seznamOtazek, function(i, o) {
            if(id==o[0])
                otazka.style.display = "none";
        });   
    }

    function zvoleneOtazky(i, otazka) {
        var id = otazka.attributes.cislo.value;
        var hledat = true;
        var info = [];

        //hleda otazky ktere jsou v testu
        $.each(seznamOtazek, function(y, o) {
            if(id==o[0]) {
                info = o;
                hledat = false;
                return;
            }
        });

        if(!hledat) //priradi k otazce pocet opakovani
            $(otazka.children[3]).val(info[1]); 
        else
            otazka.style.display = "none";
    }
    
    var option = "";
    
    function nactiTridy(i, t) {
        option += '<option value=' + t.id + '>' + t.poradi + t.nazev + '</option>';
    }

    function zobrazTridy(i,t) {
        var prvek = $(".inputLista:first").clone().insertAfter(".inputLista:first");      
        var zaklad = '<option value="0">Všechny třídy</option>';
        var option = '<option value=' + t.id + '>' + t.jmeno + '</option>';

        var select = $(prvek[0].children[0]);
        select.html(zaklad + option);
        select.val(t.id);
        if(i == 0) $(".inputLista:first").remove();
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
            $.getJSON("./json/testy/", testyZobraz)
        }
        else chybaIframe(o);
    }
}

function testyVyberOtazky() {
    var cislaOtazek = [];
    var vybrane = $("#ttZvolene .otazka:visible");
    
    $.each(vybrane, function(i, otazka) {
        var pocet = otazka.children[3].value*1;
        var id = otazka.attributes.cislo.value*1;
        cislaOtazek.push([id, pocet]);
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

//vyhodnotit test - student
function testyVyhodnotit(e) {
    smazIntervaly(); //smaze odpocet zbyvajiciho testu
    var seznamOdpovedi = [];

    $.each($(".odpoved.oznacena"), foreach);  
    $.each($(".odpovedOt"), foreach);
    var idTestu = ph("#odeslatTest");

    function foreach(i,o) {
        var text = $(o).text() || $(o).val();
        var idOtazky = o.parentElement.attributes.otazka.value;        
        seznamOdpovedi.push([idOtazky,text]); 
    }
    
    var json = {
        akce:'vyhodnotit', 
        co:'test',
        idTestu: idTestu,
        odpovedi: seznamOdpovedi
    };

    postJSON(json, odpoved, "./json/post/student/");

    function odpoved(o) {
        vysledkyZobraz(idTestu);
    }
}