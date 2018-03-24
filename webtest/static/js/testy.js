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

function testyVyzkouset(idTestu) {
    $.getJSON("/json/student/testy/" + idTestu, zpracujJSON).fail(chybaIframe);
    text = "";
    //vymazat vsechny odpocty
    smazIntervaly();

    function zpracujJSON(json) {
        var test = json.test;

        text += "<h1>" + test.jmeno + "</h1>";
        text += "<div id='odpocet'> </div>";
        $.each(test.otazky, zpracujOtazky);
        text += '<button id="odeslatTest" value="' + test.id + '">Odeslat</button>';
        $(stranka).html(text);
        MathJax.Hub.Queue(["Typeset",MathJax.Hub]);
        var interval = odpocet("#odpocet",test.limit);
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

//vyhodnotit test - student
function testyVyhodnotit(e) {
    var seznamOdpovedi = [];

    $.each($(".odpoved.oznacena"), foreach);  
    $.each($(".odpovedOt"), foreach);

    function foreach(i,o) {
        var text = $(o).text() || $(o).val();
        var idOtazky = o.parentElement.attributes.otazka.value;        
        seznamOdpovedi.push([idOtazky,text]); 
    }
    
    var json = {
        akce:'vyhodnotit', 
        co:'test',
        idTestu: ph("#odeslatTest"),
        odpovedi: seznamOdpovedi
    };

    postJSON(json, odpovedJSON, "/json/post/student/");

    cl(json);
}