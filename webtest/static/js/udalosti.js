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
    if(e.target.localName == "input") return false;
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

//přidat nový test
$(document).on("click", ".ttPridat", function(e) {
    window.location.hash = "TestyVytvorit"; 
    //testyUprava("pridat");
});

//přidat novou otázku
$(document).on("click", ".otPridat", function(e) {
    window.location.hash = "OtazkyPridat"; 
    //otazkyPridat();
});

$(document).on("click", ".otUpravitVsechny", function(e) {
    otazkyUpravVsechny(e);
});

//vyzkouset test
$(document).on("click", ".ttTlacitka .tlVyzkouset", function(e) {
    window.location.hash = "TestyVyzkouset";   
    var idTestu = e.target.parentElement.parentElement.attributes.cislo.value;
    testyVyzkouset(idTestu);
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
$(document).on("click", ".inputTlacitka", function(e) {
    var trida = e.target.className;
    var input = e.currentTarget.previousElementSibling;

    if(trida == "inputSpravna")
        $(input).attr('class','dobre');
    else if (trida == "inputSpatna")
        $(input).attr('class','spatne');
    else if (trida == "inputSmazat")
        $(input.parentElement).remove();
});

//zobrazit tlacitka po najeti mysi - u inputu
$(document).on("mouseenter", ".inputLista", function(e) {
    $(this).children('.inputTlacitka').css("display","inline");
}).on("mouseleave", ".inputLista", function(e) {
    $(this).children('.inputTlacitka').css("display","none");
});

$(document).on("keyup", "#vlozitOtazky input", function(e) {
    var input = e.currentTarget;
    var hodnota = input.value;    
    var inputy = e.currentTarget.parentElement.parentElement.children;
    var posledni = e.currentTarget.parentElement.parentElement.lastElementChild;
    var prvni = inputy[0].children[0];

    cl(e.currentTarget);

    //pokud neni input prazdny, oznac jako spatnou
    if(input.className == "seda" && hodnota.length >= 1)
        $(input).removeClass().addClass("spatne");

    //pokud neni posledni input prazdny, vloz ho
    if(posledni.children[0].className != "seda")
        vlozitOdpoved("seda","");

    //pokud je input prazdny, bude sedy
    if(hodnota.length == 0)
        $(input).removeClass().addClass("seda");

    //pokud je input prazdny, smaz posledni input
    if(hodnota.length == 0 && posledni.children[0].className == "seda") {
        $(posledni).remove();
    }

    if(inputy.length > 2) {
        prvni.className = "dobre";
        prvni.placeholder = "Správně"
    }

    else if(inputy.length <= 2) {
        prvni.className = "otevrena";
        prvni.placeholder = "Otevřená"
    }   
});

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
$(document).on("change", "#upSoubor", function(e) {
    var soubor = this.files[0];
    $("#upSJmeno").text(soubor.name);
    
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

        try {
            $.parseJSON(obsah);
            $("#upKontrola").text("JSON je v pořádku.");
            $("#upravaJSON").removeClass("skryty");
            $("#upOdeslat").removeClass("skryty"); 
        } catch(chyba) {
            $("#upKontrola").text(chyba);
            $("#upOdeslat").addClass("skryty"); 
        }
    }
    
    cl(soubor);
});

/*
with ((console && console._commandLineAPI) || {}) {
    hlaska("!!!");
}
*/


//kliknout na odpoved v testu
$(document).on("click", ".odpoved", function(e) {
    var vyber = e.currentTarget.parentElement.attributes.vyber.value;
    var odpovedi = e.currentTarget.parentElement.children;

    //vyber pouze 1 otazky
    if(vyber == 1)
        $.each(odpovedi, odznacitOdpoved);

    function odznacitOdpoved(i, odpoved){
        $(this).removeClass("oznacena");      
    } 

    $(this).toggleClass("oznacena");
});


//odeslat test
$(document).on("click", "#odeslatTest", function(e) {
    var seznamOdpovedi = [];

    $.each($(".odpoved.oznacena"), foreach);  
    $.each($(".odpovedOt"), foreach);

    function foreach(i,o) {
        var text = $(o).text() || $(o).val();
        var idOtazky = o.parentElement.attributes.otazka.value;        
        seznamOdpovedi.push([idOtazky,text]); 
    }
    
    cl(seznamOdpovedi);
});