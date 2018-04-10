window.onhashchange = zmenHash;

function zmenHash() {
    var adresa = nazevStranky();
    var hash = adresa.hash;
    var promenna = adresa.promenna;
    document.title = "WT: " + hash;

    if(intervalDb) clearInterval(intervalDb);    
    //if(!nacti) return;

    $("#log").hide();
    $("#uzivatele").hide();

    if(hash=="DB") {
        $(stranka).load("./tabulky/");
        intervalDb = setInterval(function() {
            $(stranka).load("./tabulky/");
        }, 3000);
    }
    else if(hash=="Otazky"){
        $.getJSON("./json/otazky/", function(json) {
            otazkyZobraz("#stranka",json.otazky);	
        }).fail(chybaIframe);
    }
    else if(hash=="Testy")
        $.getJSON("./json/testy/", testyZobraz).fail(chybaIframe);
    else if(hash=="Testy2")
        $.getJSON("./json/testy/", testyStudentZobraz).fail(chybaIframe);    
    else if(hash=="Nahrat")
        $(stranka).load("./upload/");  
    else if(hash=="TestyVytvorit")
        testyUprava("pridat");
    else if(hash=="OtazkyPridat")
        otazkyPridat();
    else if(hash=="Slovnik")
        slovnikZobraz();
    else if(hash=="Tridy")
        tridyZobraz();     
    else if(hash=="Studenti")
        //osobaPridat("student");
        studentZobraz()  
    else if(hash=="Vysledky")
        vysledkyZobrazSeznam();   
    else if(hash=="Registrace")
        osobaPridat("ucitel");         
    else if(hash=="Zaznamy") {
        $(stranka).html("");
        $("#log").show();  
    }
    else if(hash=="VysledkyTabulka")
        vysledkyTabulka(promenna);
    else if(hash=="Hodnoceni")
        vysledkyTabulka("");
    else if(hash=="VysledkyZobrazit")
        vysledkyZobraz(promenna);       
    else if(hash=="Prihlaseni") {
        $(stranka).html("");
        $("#uzivatele").show();
    }
}

function prejit(adresa) {
    window.location.hash = "!" + adresa;
}

function menuNahore() {
    var menu = $('nav');
    var pozice = menu.offset().top;				

    $(window).scroll(function() {
        var fix = $(this).scrollTop() > pozice ? true : false;	
        menu.toggleClass("menu", fix);
        $('body').toggleClass("body-menu", fix);			
    });

}

function nahodneLogo() {
    for(i=0;i<7;i++) {
        var nahodneC = Nahodne(5,60);
        $(".bar" + i).css("height",nahodneC);
    }
}

function dnes() {
    var tik = new Date();      
    var den = tik.getDate();
    var mesic = tik.getMonth()+1;
    var rok = tik.getFullYear();
    var hodina = tik.getHours();
    var minuta = tik.getMinutes();
    var sekunda = tik.getSeconds();

    if(minuta<10)
        minuta = "0" + minuta;

    var vysledek = den + "." + mesic + "." + rok + " " + hodina + ":" + minuta;

    return vysledek;
}

function zaRok() {
    var tik = new Date(new Date().setFullYear(new Date().getFullYear() + 1));   
    var den = tik.getDate();
    var mesic = tik.getMonth()+1;
    var rok = tik.getFullYear();
    return den + "." + mesic + "." + rok + " 00:00";
}

function nazevStranky() {
    var nazev = {};
    nazev.hash = "index";
    nazev.promenna = null;

    if(window.location.hash) {
        var adresa = window.location.hash.substring(1).replace("!","").split("/");
        nazev.hash = adresa[0];
        nazev.promenna = adresa[1];
    }

    return nazev;    
}

function odpocet(prvek,cas) {
    var sekunda = 1000;
    var minuta = sekunda * 60;
    var hodina = minuta * 60;
    cas = cas*60000;
    
    if(intOdpocet) clearInterval(intOdpocet);

    var intOdpocet = setInterval(tik, sekunda);

    function tik() {
        //var ted = new Date() + limit;
        
        cas-=sekunda;
        
        if (cas < sekunda) {
            $(prvek).text("Konec testu!!!");
            return;
        }
        
        var zbyva = {
            hodin: Math.floor((cas / hodina) ),
            minut: Math.floor((cas % hodina) / minuta),
            sekund: Math.floor((cas % minuta) / sekunda)
        }
        
        if(zbyva.hodin < 10) zbyva.hodin = "0" + zbyva.hodin;
        if(zbyva.minut < 10) zbyva.minut = "0" + zbyva.minut;
        if(zbyva.sekund < 10) zbyva.sekund = "0" + zbyva.sekund;
        
        if(zbyva.hodin < 1)
            $(prvek).text(zbyva.minut + ":" + zbyva.sekund);
        else
            $(prvek).text(zbyva.hodin + ":" + zbyva.minut + ":" + zbyva.sekund);
        
    }
}


function tabulkaRadek(pocet,sloupce) {
    var vysledek = "";
    $.each(sloupce, function(i, sloupec) {
        //1. a posledni bunka se neda upravovat
        if(i == 0 || i >= pocet)
            vysledek += "<td>" + sloupec + "</td>";
        else
            vysledek += "<td><input type'text' class='tabInput' value='" + sloupec + "'></td>";
    });
    return "<tr>" + vysledek + "</tr>";
}

function tabulkaHlavicka(sloupce) {
    var vysledek = "";
    $.each(sloupce, function(i, sloupec) {
        vysledek += "<th>" + sloupec + "</th>";
    });
    return "<tr>" + vysledek + "</tr>";
}


function zobrazitPrihlaseni() {
    var text = '\
        <h1>Přihlaste se</h1>\
        <span class="login">\
        <input placeholder="Jméno" id="login" value="ucitel" type="text"><br>\
        <input placeholder="Heslo" id="heslo" type="password"><br> \
        <button id="prihlasit">Přihlásit se</button>\
        <button id="registrace">Registrace</button>\
        </span><br>\
        <strong><a href="./databaze/">Databáze</a></strong><br>\
        <span id="obnovJS">obnovit</span>';
    
    //vymazat vsechny odpocty
    smazIntervaly();
    
    //odstrani hash
    window.location.hash = "";

    $("#prihlaseno").html("");
    $("nav").html("");
    $("#log").html("");
    $("#uzivatele").html("");
    $(stranka).html(text);
}


function wsUdalosti() {
    websocket();

    ws.on('connect', function() {
        ws.emit("prihlasit",false);
        
        ws.on('odpoved', function(o) {
            hlaska(o);
        });
    
        ws.on('disconnect', function() {

        }); 
        
        ws.on('pocet', function(o) {
            $("#prihlasenych").text(o);
        });
        
        ws.on('log', function(json) {
            pridatZaznam(json);
        }); 
        
        ws.on('uzivatele', function(json) {
            zobrazPrihlasene(json);
        }); 

        ws.on('uzivatelOdpojen', function(jmeno) {
            odhlasit();
            hlaska("Uživatel '" + jmeno + "' tě odpojil!",7);
        }); 

    });
}
