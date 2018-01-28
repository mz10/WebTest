function menuNahore() {
    var menu = $('nav');
    var pozice = menu.offset().top;				

    $(window).scroll(function() {
        var fix = ($(this).scrollTop() > pozice) ? true : false;	
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

function zmenHash() {
    var hash = nazevStranky();
    if(intervalDb) clearInterval(intervalDb);
    
    //if(!nacti) return;

    if(hash=="DB") {
        $(stranka).load("/tabulky/");
        intervalDb = setInterval(function() {
            $(stranka).load("/tabulky/");
        }, 3000);
    }
    else if(hash=="Otazky"){
        $.getJSON("/json/otazky/", function(json) {
            otazkyZobraz("#stranka",json.otazky);	
        }).fail(chybaIframe);
    }
    else if(hash=="Testy"){
        $.getJSON("/json/testy/", testyZobraz).fail(chybaIframe);
    } 
    else if(hash=="Nahrat"){
        $(stranka).load("/upload/");
    }        
    else if(hash=="TestyVytvorit"){
        testyVytvorit();
    } 
    else if(hash=="OtazkyPridat"){
        otazkyPridat();
    }
}
