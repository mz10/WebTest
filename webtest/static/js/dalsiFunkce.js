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

    switch (hash) {  
        case "TestyVytvorit":    testyUprava("pridat");        break;
        case "OtazkyPridat":     otazkyPridat();               break;
        case "Slovnik":          slovnikZobraz();              break;
        case "Tridy":            tridyZobraz();                break;     
        case "Studenti":         studentZobraz();              break;
        case "Ucitele":          uciteleZobrazTabulku();       break;
        case "Vysledky":         vysledkyZobrazSeznam();       break;   
        case "Registrace":       osobaPridat("ucitel");        break;       
        case "VysledkyTabulka":  vysledkyTabulka(promenna);    break;
        case "Hodnoceni":        vysledkyTabulka("");          break;
        case "VysledkyZobrazit": vysledkyZobraz(promenna);     break;   
        case "Ucet":             ucetInfo();                   break;
        case "Nahrat":
            $(stranka).load("./vzory/upload/"); 
            break;           
        case "Testy":
            $.getJSON("./json/testy/", testyZobraz).fail(chybaIframe);
            break;
        case "Testy2":
            $.getJSON("./json/student/testy/", testyStudentZobraz).fail(chybaIframe);   
            break;         
        case "Zaznamy":
            $(stranka).html("");
            $("#log").show(); 
            break;
        case "Prihlaseni":
            $(stranka).html("");
            $("#uzivatele").show();
            break;
        case "DB":        
            $(stranka).load("./tabulky/");
            intervalDb = setInterval(function() {
                $(stranka).load("./tabulky/");
            }, 3000);        
            break;
        case "Otazky": 
            $.getJSON("./json/otazky/", function(json) {
                otazkyZobraz("#stranka",json.otazky);	
            }).fail(chybaIframe);
            break;
    }
}

function prihlasitUzivatele() {
    var typ = $("#typUzivatele");
    if(typ.length == 0) return;

    if(typ.text() == "učitel")
        $("#menuUcitel").show();
    if(typ.text() == "admin")
        $("#menuUcitel").show();                    
    else if(typ.text() == "student")
        $("#menuStudent").show();

    $("#prihlaseni").hide()
}


function uzivatel(typ) {
    var div = $("#typUzivatele");
    if(div.length == 0) 
        return false;
    if (typ == $("#typUzivatele").text())
        return true
    
    return false;
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

function odpocet(prvek,cas, konec) {
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
            clearInterval(intOdpocet);
            konec();
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

function wsUdalosti() {
    websocket();

    ws.on('connect', function() {
        ws && ws.emit("prihlasit",false);
        
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
