//hodnocení testu - lišta - známky

function neoznacovat(el) {
    $(el).css({
        "user-select": "none",
        "-moz-user-select": "none",
        "-webkit-user-select": "none",
        "-ms-select": "none"				
    }); 
}

function oznacovat(el) {
    $(el).css({
        "user-select": "auto",
        "-moz-user-select": "auto",
        "-webkit-user-select": "auto",
        "-ms-select": "auto"				
    }); 
}

$(document).on("change", "#hodnoceni", function(e) {
    var obtiznost = ph("#hodnoceni option:selected");
    var typ = ph("#hodnoceniTyp option:selected");   
    nastavZnamky(obtiznost,typ);
});	

$(document).on("change", "#hodnoceniTyp", function(e) {
    var obtiznost = ph("#hodnoceni option:selected");
    var typ = ph("#hodnoceniTyp option:selected");  
    nastavZnamky(obtiznost,typ);
});	

function nastavZnamky(obtiznost,typ,data) {
    var hodnoceni = {
        "rovnomerne": {
            0:  [80,-1,60,-1,40,-1,20,-1,0],
            1:  [89,78,67,56,44,33,22,11,0],
            2:  [75,-1,-1,50,-1,-1,25,-1,0],
            3:  [83,-1,67,-1,50,-1,33,16,0],
            4:  [20,-1,-1,-1,-1,-1,-1,-1,0],
        },
        "mirne": {
            0:  [85,-1,70,-1,50,-1,25,-1,0],
            1:  [92,82,73,64,53,43,33,20,0],
            2:  [79,-1,-1,55,-1,-1,29,-1,0],
            3:  [88,-1,74,-1,57,-1,41,23,0],
            4:  [30,-1,-1,-1,-1,-1,-1,-1,0],
        },
        "stredni": {
            0:  [91,-1,78,-1,60,-1,40,-1,0],
            1:  [94,88,80,72,63,55,45,35,0],
            2:  [85,-1,-1,66,-1,-1,43,-1,0],
            3:  [92,-1,82,-1,69,-1,55,40,0],
            4:  [50,-1,-1,-1,-1,-1,-1,-1,0],
        },
        "prisne": {
            0:  [94,-1,87,-1,76,-1,66,-1,0],
            1:  [97,91,86,81,75,69,62,55,0],
            2:  [92,-1,-1,80,-1,-1,66,-1,0],
            3:  [93,-1,87,-1,81,-1,74,65,0],
            4:  [70,-1,-1,-1,-1,-1,-1,-1,0],
        },
        "nejtezsi": {
            0:  [98,-1,92,-1,84,-1,75,-1,0],
            1:  [98,96,93,89,86,83,79,75,0],
            2:  [96,-1,-1,87,-1,-1,75,-1,0],
            3:  [98,-1,95,-1,90,-1,83,75,0],
            4:  [80,-1,-1,-1,-1,-1,-1,-1,0],
        }
    }

    if (data)
        data = data.split(";")

    for(var i=0;i<9;i++) {      
        var znamka = "#zn" + (i+1);        
        pohyb(znamka);
        if (data)
            nastavPozici(znamka,data[i]);
        else
            nastavPozici(znamka,hodnoceni[obtiznost][typ][i]);
    }
}

function nastavPozici(el,procento) {
    if(procento == -1) {
        pr(el).hide();
        pr(el).text("-1");
        return;
    }
    else pr(el).show()

    var sirkaListy = $("#stranka").find("#znamky").innerWidth();
    pixely = sirkaListy*procento/100;

    pr(el).css("left", pixely + "px"); 
    pr(el).text(parseFloat(procento).toFixed(0));
}

function pohyb(el) {					
    var aktivni = null;

    //nastavit prvek jako aktivni pokud se na neho klikne
    $(document).on("mousedown", el, function(e) {
        aktivni = el;;
    });

    //zacit presouvat po stisknuti mysi
    $(document).mousedown(function(e){
        if (aktivni) {
            pr(".znamka").css("transition","0s");            					
            neoznacovat("html");
            neoznacovat("body");
            $("html").css("cursor","e-resize");
            document.onmousemove = hybat;
        }
    }).mouseup(function(e) {//zrusit presouvani
        if (aktivni) {
            aktivni = null;
            oznacovat("html");
            oznacovat("body");
            pr(".znamka").css("transition","1s");	
            $("html").css("cursor","auto");					
            document.onmousemove = null;
        }
    });	

    function hybat(e) {
        var zacatekListy = pr("#znamky").offset().left;
        var rozdil = e.pageX-zacatekListy;
        var sirkaListy = pr("#znamky").innerWidth();
        var procento = 100*rozdil/sirkaListy;

        if(procento>=0 && procento<=100.0) {				
            pr(el).css("left", rozdil + "px"); 
            pr(el).text(parseFloat(procento).toFixed(0));
        }
    }
}


function zjistitHodnoceni() {
    var vysledek = "";

    $.each(pr("#znamky")[0].children, function(i, znamka) {
        vysledek += znamka.innerText + ";"
    });
    return vysledek.substring(0, vysledek.length - 1);
}