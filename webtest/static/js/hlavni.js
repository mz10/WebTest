
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
        postJSON(json, odpovedJSON);
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


function slovnikZobraz() {
    slovnikZobrazTabulku(function(tabulka) {
        var nadpis = "<h1>Slovník</h1>";
        $(stranka).html(nadpis + tabulka);
    });
}

function slovnikZobrazTabulku(nacteno) {
    $.getJSON("./json/slovnik/", zpracujJSON).fail(chybaIframe);
    
    var tabulka = tabulkaHlavicka(["id", "Slovo 1", "Slovo 2", "Kategorie","Jazyk",""]);
    
    function tlacitko(text) { return "<button class='radekAkce'>" + text + "</button>"; }
    
    function zpracujJSON(json) {
        $.each(json.slovnik, zobrazTabulku);
        tabulka += tabulkaRadek(5,["", "", "", "", "", tlacitko("Přidat")]);
        nacteno("<table class='tabDb' nazev='Slovnik'>" + tabulka + "</table>");
    }

    function zobrazTabulku(i,t) {
        tabulka += tabulkaRadek(5,[t.id, t.slovo1, t.slovo2, t.kategorie, t.jazyk, tlacitko("Smazat")]);
    }
}


function slovnik() {
    $(stranka).load("./static/slovnik.html");
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

    $.getJSON(json, odpovedJSON);
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
    tridyZobrazTabulku(function(tabulka) {
        var nadpis = "<h1>Třídy</h1>";
        $(stranka).html(nadpis + tabulka);
    });
}


function tridyOdeslat() {
    var json = {
        akce: "pridat", 
        co: 'trida',
        poradi: ph('#trPoradi'),
        nazev: ph('#trNazev'),
        rok: ph('#trRok'),
    }; 

    $.getJSON(json, odpovedJSON);
}


function tridyZobrazTabulku(nacteno) {
    $.getJSON("./json/tridy/", zpracujJSON).fail(chybaIframe);
    
    var tabulka = tabulkaHlavicka(["id", "Pořadí", "Název", "Rok",""]);
    
    function tlacitko(text) { return "<button class='radekAkce'>" + text + "</button>"; }
    
    function zpracujJSON(json) {
        $.each(json.tridy, zobrazTabulku);
        tabulka += tabulkaRadek(4,["", "", "", "", tlacitko("Přidat")]);
        nacteno("<table class='tabDb' nazev='Tridy'>" + tabulka + "</table>");
    }

    function zobrazTabulku(i,t) {
        tabulka += tabulkaRadek(4,[t.id, t.poradi, t.nazev, t.rokUkonceni, tlacitko("Smazat")]);
    }
}

/*******************************************/

//pridat studenta nebo ucitele
function osobaPridat(typ) {
    var nadpis = "Přidat učitele";
    var select = "";

    if(typ == "student") {
        nadpis = "Přidat studenta";
        var option = "";
        
        $.getJSON("./json/tridy/", function(json) {     
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
    postJSON(json, odpovedJSON, "./json/registrace/");
}


function studentZobrazTabulku(nacteno) {
    $.getJSON("./json/studenti/", zpracujJSON).fail(chybaIframe);
    
    var tabulka = tabulkaHlavicka(["id", "Login", "Jméno", "Příjmení","Třída",""]);
    
    function tlacitko(text) { 
        return "<button class='radekAkce'>" + text + "</button>"; 
    }
    
    function zpracujJSON(json) {
        $.each(json.studenti, zobrazTabulku);
        var select = '<select class="tbTridy"></select>';
        tabulka += tabulkaRadek(4,["", "", "", "", select, tlacitko("Přidat")]);
        nacteno("<table class='tabDb' nazev='Student'>" + tabulka + "</table>");
    }

    function zobrazTabulku(i,t) {
        var select = 
            '<select class="tbTridy" hodnota="' + t.trida.id + '">\
                <option selected value="' + t.trida.id + '">' + t.trida.nazev + '</option>\
            </select>';
        tabulka += tabulkaRadek(4,[t.id, t.login, t.jmeno, t.prijmeni, select, tlacitko("Smazat")]);
    }
}

function studentZobraz() {
    studentZobrazTabulku(function(tabulka) {
        var nadpis = "<h1>Studenti</h1>";
        $(stranka).html(nadpis + tabulka);
    });
    var option = "";

    $.getJSON("./json/tridy/", function(json) {     
        $.each(json.tridy, nactiTridy);
        $(stranka).find(".tbTridy").append(option);
    }).fail(chybaIframe);
    
    function nactiTridy(i, t) {
        option += '<option value=' + t.id + '>' + t.poradi + t.nazev + '</option>';
    }
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


/** */

function tabulkaUpravit(radek,zpet) {
    for(var i=1;i<=3;i++) {
        var bunka = radek.children[i];
        var typ = bunka.localName;      

        cl(bunka.firstChild.localName);

        if(zpet && bunka.firstChild.localName == "input") {
            var td = $('<td />', {
                html: $(bunka.firstChild).val()
            });

            $(bunka).replaceWith(td);
        }
        else if (bunka.localName == "td") {
            var input = $('<input />', {
                type: 'text',
                value: $(bunka).text()
            });

            $(bunka).html(input);
        }
           
    }
}

function tabulkaZmenitZaznam(e) {
    var radek = e.target.parentElement.parentElement;  
    var tabNazev = radek.parentElement.parentElement.attributes.nazev.value;

    var tlacitko = this;
    var text = $(tlacitko).text();
    var akce = 'smazat';

    if(text == "Změnit")
        akce = 'zmenit';

    //ziska seznam bunek v tabulce (krome 1. a posledni)
    var seznamBunek = [];
    for(i=1;i<radek.childElementCount-1;i++) {
        seznamBunek.push(radek.children[i].firstChild.value);
    }
    cl(radek);


    var json = {
        akce: akce,
        co:'radek',
        tabulka: tabNazev,
        id: $(radek.firstChild).text(), 
        bunky: seznamBunek
    }

    cl(json);
    postJSON(json, odpovedJSON);
    if(tabNazev == "Tridy")
        tridyZobraz();
    else if (tabNazev == "Student")
        studentZobraz();
    else if (tabNazev == "Slovnik")
        slovnikZobraz();    
}


function prihlasit(e) {
    var json = {
        login: ph("#login"),
        heslo: ph("#heslo"),
    };

    console.log(json);
    postJSON(json, odpoved, "./prihlasit/");

    function odpoved(o) {
        if(o.html)
            prihlaseno(o);
        if (o.info)
            hlaska(o.info,7);
    }

    function prihlaseno(o) {
        wsUdalosti();
        $("nav").html(o.html);
        text = o.prihlasen + ': <a id="odhlasit">' + o.uzivatel + '</a><br>';
        text += 'Přihlášených: <span id="prihlasenych">0</span>';
        $("#prihlaseno").html(text);
        $(stranka).html("");
    }

}

function odhlasit() {
    $.getJSON("./odhlasit/", odpoved).fail(chybaIframe);

    function odpoved(o) {
        if(o.odpoved == "odhlaseno"){
            zobrazitPrihlaseni();
            ws && ws.emit('odhlasit', false);
            ws = null;
        }
        else
            hlaska("Chyba při odhášení!",4);
    }
}


function pridatZaznam(json) {
    //hlaska(json,10);
    json = JSON.parse(json); 

    //kontrola jestli neni uz tabulka vlozena
    if ($('.tbZaznamy').length === 0) {
        var tabulka = 
            '<table class="tbZaznamy"><tr>\
                <th>Jméno</th>\
                <th>Login</th>\
                <th>Přihlášen</th>\
                <th>Třída</th>\
                <th>Akce</th>\
                <th>Čas akce</th>\
            </tr></table>';

        $('#log').append(tabulka);
    }


    var radek = 
        '<tr>\
            <td>' + json.jmeno + '</td>\
            <td>' + json.login + '</td>\
            <td>' + json.casPrihlaseni + '</td>\
            <td>' + json.trida + '</td>\
            <td>' + json.akce + '</td>\
            <td>' + json.casAkce.substr(11) + '</td>\
        </tr>';

    $("#log").find(".tbZaznamy tbody").after(radek);
}


function zobrazPrihlasene(json) {
    json = JSON.parse(json); 

    var radky = "";
    var odpojit = "<button class='uzivatelOdpojit'>Odpojit</button>"


    $.each(json, function(i, p) {
        radky += 
            '<tr>\
                <td>' + p.sid + '</td>\
                <td>' + p.jmeno + '</td>\
                <td>' + p.login + '</td>\
                <td>' + p.typ + '</td>\
                <td>' + p.trida + '</td>\
                <td>' + p.casPrihlaseni + '</td>\
                <td>' + odpojit + '</td>\
            </tr>';
    });

    var tabulka = 
        '<table class="tbPrihlaseni"><tr>\
            <th>SID</th>\
            <th>Jméno</th>\
            <th>Login</th>\
            <th>Typ</th>\
            <th>Třída</th>\
            <th>Přihlášen</th>\
            <th></th>\
        </tr>' + radky + '</table>';

    $("#uzivatele").html(tabulka);
}