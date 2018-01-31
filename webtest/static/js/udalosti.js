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
    window.location.hash = "OtazkyUpravit";
    var idOtazky = e.currentTarget.attributes.cislo.value;
    otazkyUprav(idOtazky);
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
$(document).on("click", ".test", function(e) {
    if(e.target.localName == "button") return false;
    window.location.hash = "TestyUpravit";   
    var idTestu = e.currentTarget.attributes.cislo.value;    
    testyUprava("uprav",idTestu);
}); 

$(document).on("click", "#ttSkrytZadani", function(e) {
    $(".otZadani").toggle();
}); 


//zobrazit tlacitka po najeti mysi - u otazek
$(document).on("mouseenter", stranka + " > .otazka", function(e) {
    $(this).children('.otTlacitka').css("display","block");
}).on("mouseleave", stranka + " > .otazka", function(e) {
    $(this).children('.otTlacitka').css("display","none");
});

//zobrazit tlacitka po najeti mysi - u testu
$(document).on("mouseenter", ".test", function(e) {
    $(this).children('.ttTlacitka').css("display","block");
}).on("mouseleave", ".test", function(e) {
    $(this).children('.ttTlacitka').css("display","none");
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


//vygenerovat nove zadani u otazky
$(document).on("click", ".otTlacitka .tlKostka", otazkyKostka);

//kliknout na odpovědi u otázek
$(document).on("click", ".otTlacitka .tlZobrazOdpovedi", otazkyZobrazOdpovedi);

//zobrazit puvodni zadani u otazky
var zadaniJakoHTML = false;
$(document).on("click", ".otTlacitka .tlZadani", function(e) {
    var idOtazky =  e.target.parentElement.parentElement.attributes.cislo.value;

    $.getJSON("/json/otazky/" + idOtazky, function(json) {         
        var zadani = json.otazka.zadani.replace(/\n/g,"<br>")
        if(zadaniJakoHTML)
            zadani = json.otazka.zadaniHTML;
            
        zadaniJakoHTML = !zadaniJakoHTML;
        $(".otazka[cislo=" + idOtazky + "] .otZadani").html(zadani);
    });
});



$(document).on("click", "#ttPokusu", function(e) {
    var skrk = $("#ttSkryt")[0].checked;
    cl(skrk);
});


$(document).on("click", ".ttPridat", function(e) {
    window.location.hash = "TestyVytvorit"; 
    //testyUprava("pridat");
});

$(document).on("click", ".otPridat", function(e) {
    window.location.hash = "OtazkyPridat"; 
    //otazkyPridat();
});

$(document).on("click", ".otUpravitVsechny", function(e) {
    otazkyUpravVsechny(e);
});