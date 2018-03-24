
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


/***************tridy************** */

function tridyPridat() {
    var pridat = '\
        <div class="PridatTridu">\
            <h1>Přidat třídu</h1>\
            <input type="text" id="trPoradi" placeholder="Pořadí"><br>\
            <input type="text" id="trNazev" placeholder="Název"><br>\
            <input type="text" id="trRok" placeholder="Rok ukončení"><br>\
            <button id="trOdeslat">Odeslat</button>\
        </div>';
    
    $(stranka).html(pridat);
}


function tridyZobraz(json) {
    var text = "";

    var tlacitka =  
        '<span class="trTlacitka">\
            <button class="trZobrazit">Zobrazit</button>\
            <button class="trSmazat">Smazat</button>\
            <button class="trVyzkouset">Vyzkoušet</button>\
        </span>';

        /*
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
    */

    text = 
    '<h1>Třídy</h1>\
    <div class="trPridat">Přidat</div>\
    ' + text + '\
    <div class="trPridat">Přidat</div>';

    $(stranka).html(text);
}


function tridyOdeslat() {
    var json = {
        akce: "pridat", 
        co: 'trida',
        poradi: ph('#trPoradi'),
        nazev: ph('#trNazev'),
        rok: ph('#trRok'),
    }; 

    postJSON(json, odpovedJSON);    
}


//pridat studenta nebo ucitele
function osobaPridat(typ) {
    var nadpis = "Přidat učitele";
    var select = "";

    if(typ == "student") {
        nadpis = "Přidat studenta";
        var option = "";
        
        $.getJSON("/json/tridy/", function(json) {     
            $.when($.each(json.tridy, nactiTridy)).done(jsonNacten);
        }).fail(chybaIframe);

    }
    else pridat("");

    function nactiTridy(i, t) {
        option += '<option value=' + t.id + '>' + t.poradi + t.nazev + '</option>';
        cl(t);
    }

    function jsonNacten() {
        select = '<select id="osTrida"><option selected disabled>Třída</option>' + option + '</select>';                           
        pridat(select);
    }

    function pridat(select) {
        var pridat = '\
            <div class="osPridat">\
                <h1>' + nadpis + '</h1>\
                <input type="text" id="osLogin" placeholder="Login"><br>\
                <input type="password" id="osHeslo" placeholder="Heslo"><br>\
                <input type="text" id="osJmeno" placeholder="Jméno"><br>\
                <input type="text" id="osPrijmeni" placeholder="Přijmení"><br>'
                + select + '\
                <button value="' + typ + '" id="osOdeslat">Odeslat</button>\
            </div>';

        $(stranka).html(pridat);
    }
}

//odeslat osobu - student/ucitel
function osobaOdeslat() {
    var json = {
        akce: "pridat", 
        co: 'osoba',
        typ: ph('#osOdeslat'),
        login: ph('#osLogin'),
        heslo: ph('#osHeslo'),
        jmeno: ph('#osJmeno'),
        prijmeni: ph('#osPrijmeni'),
        trida: ph('#osTrida'),
    }; 

    cl(json);
    postJSON(json, odpovedJSON, "/json/registrace/");
}


function uploadNahled() {
    var soubor = this.files[0];
    var jmeno = soubor.name;
    var pripona = jmeno.substring(jmeno.length - 4);

    $("#upSJmeno").text(jmeno);
    
    if(soubor.size > 524288) {
        $("#upKontrola").text("Soubor je moc velký!");
        return false;
    }

    var reader = new FileReader();       
    var souborTxt = reader.readAsText(soubor);    
    
    //precist obsah souboru
    reader.onload = function(e2) {
        var obsah = e2.target.result;
        $("#upravaJSON").val(e2.target.result);
        $("#upravaJSON").removeClass();
        $("#upOdeslat").removeClass(); 

        if(pripona == ".csv") {
            $("#upKontrola").text("CSV soubor");
            $("#upOdeslat").addClass("csv"); 
            return
        }

        try {
            $.parseJSON(obsah);
            $("#upKontrola").text("JSON je v pořádku.");
        } catch(chyba) {
            $("#upKontrola").text(chyba);
            $("#upOdeslat").addClass("skryty"); 
        }
    }    
}

function uploadOdeslat(e) {
    var soubor = ph("#upravaJSON");
    
    if(e.target.className == "csv") {
        soubor = {
            akce: "nahrat", 
            co: "csvSlovnik",
            data: soubor
        }
    }

    cl(soubor);
    postJSON(soubor, odpovedJSON);
}



/****************VYSLEDKY******************* */

function vysledkyZobraz() {

    $.getJSON("/vyhodnotit/" + "10", zpracujJSON).fail(chybaIframe);
    text = "";

    function zpracujJSON(json) {
        var test = json.test;
        $.each(test, zpracujOtazky);
        $(stranka).html(text);
        MathJax.Hub.Queue(["Typeset",MathJax.Hub]);
    }

    //!!!!!
    function zpracujOtazky(i, seznam) {
        var typ = "odSpatne";
        if(seznam.hodnoceni >= 1)
            typ = "odDobre";
        
        text += "<h2 class='" + typ + "'>Otázka " + seznam.jmeno + " (" + seznam.bodu + ")</h1>";
        text += "<h3>" + seznam.zadani + "</h3>";

        $.each(seznam.dobre, function(i, od) {
            if(seznam.oznaceneDobre && isInArray(od, seznam.oznaceneDobre))
                text += "<div class='odDobre'>" + od + "</div>";
            else
                text += "<div>" + od + "</div>";
        });

        $.each(seznam.spatne, function(i, od) {
            if(seznam.oznaceneSpatne && isInArray(od, seznam.oznaceneSpatne))
                text += "<div class='odSpatne'>" + od + "</div>";
            else
                text += "<div>" + od + "</div>";
        });

        $.each(seznam.otevrena, function(i, od) {
            if(seznam.oznaceneDobre && isInArray(od, seznam.oznaceneDobre))
                text += "<div class='odDobre'>" + od + "</div>";
            else if(seznam.spatne && isInArray(od, seznam.oznaceneSpatne))
                text += "<div class='odSpravne'>" + od + "</div>";
        });

    }
}