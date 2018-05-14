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
    $("#menuInfo").hide();

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
        case "Akce":             akceZobrazTabulku();          break;
        case "Nahrat":
            $(stranka).load("./vzory/upload/"); 
            break;           
        case "Testy":
            if(promenna) {
                testyUprava("uprav",promenna);
                break;
            }

            testyZobraz();
            break;
        case "Testy2":
            $.getJSON("./json/student/testy/", testyStudentZobraz).fail(chybaIframe);   
            break;  
        case "TestyVyzkouset":
            if(promenna) testyVyzkouset(promenna,true) 
            break;
        case "Aktivita":
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
            if(promenna) {
                otazkyUprav(promenna);
                break;
            }
            otazkyZobraz(stranka);	
            break;
    }
}

function prihlasitUzivatele() {
    var typ = $("#typUzivatele");
    if(typ.length == 0) return;

    if(typ.text() == "učitel")
        $("#menuUcitel").show();
    if(typ.text() == "admin")
        $("#menuAdmin").show();                    
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
    var menu = $('nav:visible');
    if (menu.length == 0) return;
    var poziceMenu = menu.offset().top;
    var poziceNabidka = 0;
    var nabidka = $('.otNabidka');
    
    if(nabidka.length != 0)
        poziceNabidka = nabidka.offset().top-80;

    $(window).scroll(function(e) {
        //menu
        var fix = ($(this).scrollTop() > poziceMenu) ? true : false;	
        menu.toggleClass("menu", fix);
        
        //nabídka
        if(nabidka.length == 0) return;
        fix = ($(this).scrollTop() > poziceNabidka) ? true : false;	
        nabidka.toggleClass("nahore", fix);   

    });

}

function nahodneLogo() {
    for(i=0;i<7;i++) {
        var nahodneC = nahodne(5,72);
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
    
    //cas v sekundach na ms
    cas = cas*1000;
    
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
        else {
            var vel = sloupec.length < 3 ? 3 : sloupec.length;
            if(!vel) vel = 3;
            vysledek += `<td><input type'text' size="${vel}" class='tabInput' value='${sloupec}'></td>`;
        }
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
    if(!ws) return;

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
