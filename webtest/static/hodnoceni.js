//hodnocení testu - lišta - známky
var nastavZnamky;

$(function() {
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
        var hodnota = $("#stranka").find("#hodnoceni option:selected").val();
        nastavZnamky(hodnota);
        console.log(e);
    });	

    nastavZnamky = function(h) {
        var hodnoceni = [];				
        var znamky = ["#jednicka", "#dvojka", "#trojka", "#ctverka", "#petka"];

        hodnoceni[0] = [80,60,40,20,0];
        hodnoceni[1] = [85,70,50,25,0];
        hodnoceni[2] = [94,87,76,66,0];
        hodnoceni[3] = [98,92,84,75,0];										

        for(var i=0;i<znamky.length;i++) {
            pohyb(znamky[i]);
            nastavPozici(znamky[i],hodnoceni[h][i]);
        }
    }

    function nastavPozici(el,procento) {
        var sirkaListy = $("#stranka").find("#znamky").innerWidth();
        pixely = sirkaListy*procento/100;

        $("#stranka").find(el).css("left", pixely + "px"); 
        $("#stranka").find(el).text(parseFloat(procento).toFixed(0));
    }

    function pohyb(el) {					
        var aktivni = null;

        //nastavit prvek jako aktivni pokud se na to klikne
        $(document).on("mousedown", el, function(e) {
            aktivni = el;
        });
    
        //zacit presouvat po stisknuti mysi
        $(document).mousedown(function(e){
            if (aktivni) {						
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
                $("html").css("cursor","auto");					
                document.onmousemove = null;
            }
        });	

        function hybat(e) {
            var zacatekListy = $("#stranka").find("#znamky").offset().left;
            var rozdil = e.pageX-zacatekListy;
            var sirkaListy = $("#stranka").find("#znamky").innerWidth();
            var procento = 100*rozdil/sirkaListy;

            if(procento>=0 && procento<=100.0) {				
                $("#stranka").find(el).css("left", rozdil + "px"); 
                $("#stranka").find(el).text(parseFloat(procento).toFixed(0));
            }
        }
    }
});