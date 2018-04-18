
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

function tridyZobraz() {
    tridyZobrazTabulku(function(tabulka) {
        var nadpis = "<h1>Třídy</h1>";
        $(stranka).html(nadpis + tabulka);
    });
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

function prihlasit(e) {
    var json = {
        login: $("#login").val(),
        heslo: $("#heslo").val(),
    };

    console.log(json);
    postJSON(json, odpoved, "./prihlasit/");

    function odpoved(o) {
        if(o.prihlasen != "nikdo")
            prihlaseno(o);
        if (o.info)
            hlaska(o.info,3);
    }

    function prihlaseno(o) {
        wsUdalosti();
        $("#prihlaseni").hide();
        text = `<span id="typUzivatele">${o.prihlasen}</span>: <a id="odhlasit">${o.uzivatel}</a><br>`;
        text += 'Přihlášených: <span id="prihlasenych">0</span>';
        $("#prihlaseno").html(text);
        if(o.prihlasen == "učitel")
            $("#menuUcitel").show();
        if(o.prihlasen == "admin")
            $("#menuUcitel").show();
        else if(o.prihlasen == "student")
            $("#menuStudent").show();
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

function zobrazitPrihlaseni() {
    $("#prihlaseni").show();
    //vymazat vsechny odpocty
    smazIntervaly();
    
    //odstrani hash
    window.location.hash = "";

    $("#menuUcitel").hide();
    $("#menuStudent").hide();

    $("#prihlaseno").html("");
    $("#log").html("");
    $("#uzivatele").html("");
    $(stranka).html("");
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