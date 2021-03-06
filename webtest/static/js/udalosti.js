//smazat test - zobrazit dialog
$(document).on("click", "#ttSmazat", function(e) {
    dialog('Smazat test?', ano, ne);

    function ano() {
        hlaska("Smazáno",5); 
    }
});

//smazat otazku
$(document).on("click", "#otSmazat", function(e) {
    var idOtazky = $(stranka).find('#otId').text();       
    otazkySmazat(idOtazky);
});

//mysi najet na logo - nahodne
$(document).on("mouseenter", ".logo2", nahodneLogo);

//odeslat otazku
$(document).on("click", "#otVlozit", otazkyOdeslat);

//odeslat test
$(document).on("click", "#ttOdeslat", testyOdeslat);

//vymenit otazky - dostupne <-> zvolene
$(document).on("click", "#ttVybrat", testyVymenOtazky);

//kliknout na otazku
$(document).on("click", stranka + " > .otazka", function(e) {
    if(e.target.localName == "button") return false;
    if(e.target.localName == "textarea") return false;
    var idOtazky = e.currentTarget.attributes.cislo.value;
    prejit("Otazky/" + idOtazky);
});

//kliknout na dostupne otazky
$(document).on("click", "#ttDostupne > .otazka", function(e) {
    $(this).toggleClass("vybrana");
});

//kliknout na zvolene otazky
$(document).on("click", "#ttZvolene > .otazka", function(e) {
    $(this).toggleClass("vybrana");
});

//kliknout na test
$(document).on("click", ".test.ucitel", function(e) {
    if(e.target.localName == "button") return false;
    if(e.target.localName == "input") return false;
    var idTestu = e.currentTarget.attributes.cislo.value; 
    prejit("Testy/" + idTestu);
}); 

//kliknout na test student
$(document).on("click", ".test.student", function(e) {
    prejit("TestyVyzkouset");
    var idTestu = e.currentTarget.attributes.cislo.value;
    testyVyzkouset(idTestu);
}); 

$(document).on("click", "#ttSkrytZadani", function(e) {
    $(".otZadani").toggle();
}); 

//zobrazit tlacitka po najeti mysi - u otazek
$(document).on("mouseenter", stranka + " > .otazka", function(e) {
    $(this).children('.otTlacitka').css("opacity","1");
}).on("mouseleave", stranka + " > .otazka", function(e) {
    $(this).children('.otTlacitka').css("opacity","0");
});

//zobrazit tlacitka po najeti mysi - u testu
$(document).on("mouseenter", ".test", function(e) {
    $(this).children('.ttTlacitka').css("opacity","1");
}).on("mouseleave", ".test", function(e) {
    $(this).children('.ttTlacitka').css("opacity","0");
});
  
//smazat tabulku (databaze)
$(document).on("click", ".tbSmazat", function(e) {
    tabulka(e.target.value,"smazat");
}); 

//vysypat tabulku (databaze)
$(document).on("click", ".tbVysypat", function(e) {
    tabulka(e.target.value,"vysypat");
}); 
    
//kliknout na kalendar
$(document).on("click", ".kalendar", function(e) {
    var umisteni = e.currentTarget.attributes.input.value;
    zobrazitKalendar(umisteni);
});

//smazat otazku
$(document).on("click", ".otTlacitka .tlSmazat", function(e) {
    var idOtazky =  e.target.parentElement.parentElement.attributes.cislo.value;
    otazkySmazat(idOtazky);
});

//smazat test
$(document).on("click", ".ttTlacitka .tlSmazat", function(e) {
    var idTestu =  e.target.parentElement.parentElement.attributes.cislo.value;
    testySmazat(idTestu);
});

//zobrazit vygenerovany test - ucitel
$(document).on("click", ".ttTlacitka .tlZobrazit", function(e) {
    var idTestu =  e.target.parentElement.parentElement.attributes.cislo.value;
    prejit("TestyVyzkouset/" + idTestu)
});

//zobrazit vygenerovany test - nové zadání
$(document).on("click", "#vygenerovat", function(e) {
    var idTestu = this.attributes.cislo.value;
    testyVyzkouset(idTestu,true);
});

//vygenerovat nove zadani u otazky
$(document).on("click", ".otTlacitka .tlKostka", otazkyKostka);

//kliknout na odpovědi u otázek
$(document).on("click", ".otTlacitka .tlZobrazOdpovedi", otazkyZobrazOdpovedi);

//zobrazit puvodni zadani u otazky
var zadaniJakoHTML = false;
$(document).on("click", ".otTlacitka .tlZadani", function(e) {
    var idOtazky =  e.target.parentElement.parentElement.attributes.cislo.value;

    $.getJSON("./json/otazky/" + idOtazky, function(json) {         
        var zadani = json.otazka.zadani.replace(/\n/g,"<br>")
        if(zadaniJakoHTML)
            zadani = json.otazka.zadaniHTML;    
        else
            zadani = "<p>" + zadani + "</p>";
            
        zadaniJakoHTML = !zadaniJakoHTML;
        $(".otazka[cislo=" + idOtazky + "] .otZadani").html(zadani);
        
        if(!zadaniJakoHTML) mathjax();
    });
});



$(document).on("click", "#ttPokusu", function(e) {
    var skrk = $("#ttSkryt")[0].checked;
});

//přidat nový test
$(document).on("click", ".ttPridat", function(e) {
    prejit("TestyVytvorit"); 
    //testyUprava("pridat");
});

//přidat novou otázku
$(document).on("click", ".otPridat", function(e) {
    prejit("OtazkyPridat"); 
    //otazkyPridat();
});

$(document).on("click", ".otSmazatVsechny", function(e) {
    otazkySmazatVsechny(e);
});

//input - pridat spatnou otazku
$(document).on("click", "#otPrSpatna", function(e) {
    
    var vlozitInput = '<input class="seda" placeholder="" type="text">';
    var lista = '<div class="inputLista">' + vlozitInput + '\
                    <span class="inputSpatna">o</span>\
                    <span class="inputSpravna">o</span>\
                    <span class="inputSmazat">x</span>\
                </div>';
    
    $("#vlozitOtazky").append(lista);
});

//input - tlacitka pro zmenu a smazani
$(document).on("click", ".inputTlacitka", otazkyOdpovedi);

//zobrazit tlacitka po najeti mysi - u inputu
$(document).on("mouseenter", ".inputLista", function(e) {
    $(this).children('.inputTlacitka').css("opacity","1");
}).on("mouseleave", ".inputLista", function(e) {
    $(this).children('.inputTlacitka').css("opacity","0");
});

$(document).on("keyup", "#vlozitOtazky input", otazkyVlozit);

//odeslat slovnik
$(document).on("click", "#slOdeslat", function(e) {
    slovnikOdeslat();
});

//upload - vybrat soubor
$(document).on("click", "#upProchazet", function(e) {
    //klikne na tlacitko pro vyber souboru
    $("#upSoubor").click();
});

//upload - nacti soubor
$(document).on("change", "#upSoubor", uploadNahled);

$(document).on("click", "#upOdeslat", uploadOdeslat);

//kliknout na odpoved v testu
$(document).on("click", ".odpoved", function(e) {
    var vyber = e.currentTarget.parentElement.attributes.vyber.value;
    var odpovedi = e.currentTarget.parentElement.children;

    //vyber pouze 1 otazky
    if(vyber == 1)
        $.each(odpovedi, odznacitOdpoved);

    function odznacitOdpoved(i, odpoved){
        var odznacit = this.children[0];
        $(odznacit).removeClass("oznaceno");
    } 

    //$(this).toggleClass("oznacena");
    var oznacit = this.children[0];
    $(oznacit).toggleClass("oznaceno");
});

/*
$(document).on("mouseover", ".odpoved", function(e) {
    var vyber = e.currentTarget.parentElement.attributes.vyber.value;
    var odpovedi = e.currentTarget.parentElement.children;

    //vyber pouze 1 otazky
    if(vyber == 1)
        $.each(odpovedi, odznacitOdpoved);

    function odznacitOdpoved(i, odpoved){
        var odznacit = this.children[0];
        $(odznacit).removeClass("oznaceno");
    } 

    //$(this).toggleClass("oznacena");
    var oznacit = this.children[0];
    $(oznacit).toggleClass("oznaceno");
});
*/

//vyhodnotit test - student
$(document).on("click", "#odeslatTest", testyVyhodnotit);

//prihlaseni
$(document).on("click", "#prihlasit", prihlasit);

//prihlaseni - enter
$(document).on("keyup", "#heslo", function(e) {
    if (e.keyCode == 13) prihlasit();
});

$(document).on("click", "#odhlasit", odhlasit);

//registrace
$(document).on("click", "#registrace", function(e) {
    prejit("Registrace");
});


$(document).on("click", ".radekAkce", tabulkaZmenitZaznam);

//vkladani textu do tabulky
$(document).on("mouseenter", ".tabDb tr", function(e) {
    //tabulkaUpravit(this);
}).on("mouseleave", ".tabDb tr", function(e) {
    //tabulkaUpravit(this,true);
});

//zmena hodnoty v tabulce
$(document).on("keyup", ".tabInput", tabulkyZmenaHodnoty);

//zmena hodnoty v tabulce - u selectu
$(document).on("change", ".tbTridy", tabulkyZmenaHodnoty);

//zmena hodnoty v tabulce - checkbox
$(document).on("change", ".tabCh", function(e) {
    tabulkyZmenaHodnoty(e);
    this.value = false;

    if (this.checked)
        this.value = true;
});

$(window).on("visibilitychange", function(e) {
    if(document.hidden) {
        ws && ws.emit("info","s");
    }
    else
        ws && ws.emit("info","z");
});

$(window).on('blur', function(){
    //$("html").hide();
    ws && ws.emit("info","b");
 });
 
 $(window).on('focus', function(){
    //$("html").show();
    ws && ws.emit("info","f");
 });

$(window).on("unload", function() {
    ws && ws.emit('odhlasit', false);
});
$(window).on("beforeunload", function() {
    ws && ws.emit('odhlasit', false);
});

//odpojit uzivatele pres websocket
$(document).on("click", ".uzivatelOdpojit", function(e) {
    var sid = this.parentElement.parentElement.children[0].textContent;
    $(this).text(". . .");
    ws && ws.emit('odpojUzivatele', sid);
});

//kliknout na vysledek testu
$(document).on("click", ".vysledek", function(e) {
    var idTestu = this.attributes.cislo.value;
    prejit("VysledkyTabulka/"+ idTestu*1);
}); 


//zobrazit vysledek testu
$(document).on("click", ".vsZobrazit", function(e) {
    var idVysledku = this.parentElement.parentElement.children[0].textContent;
    prejit("VysledkyZobrazit/" + idVysledku*1);
}); 


$(document).on("click", "#ucZmenitHeslo", ucetHeslo); 


$(document).on("keyup", ".tabInput", function(e) {
    var max = $(this.attributes.max).val();
    if(!max) max = 20;
    var delka = this.value.length;    
    if (delka >= max) return;
    this.style.width = this.value.length + 2 + "ch";
});

$(document).on("click", "nav ul li a", function(e) {
    var menu = this.parentElement.parentElement.children;  
    $.each(menu, odznacit);

    function odznacit(i, polozka){
        var odznacit = this.children[0];
        $(polozka.firstChild).removeClass("oznaceno");
    } 

    $(this).toggleClass("oznaceno");
});