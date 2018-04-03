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
    var hash = "index";
    if(window.location.hash)
        hash = window.location.hash.substring(1);

    return hash;    
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
        <strong><a href="/databaze/">Databáze</a></strong><br>\
        <span id="obnovJS">obnovit</span>';
    
    //vymazat vsechny odpocty
    smazIntervaly();
    
    //odstrani hash
    window.location.hash = "";

    $("#prihlaseno").html("");
    $("nav").html("");
    $(stranka).html(text);
}