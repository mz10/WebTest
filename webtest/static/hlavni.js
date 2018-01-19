$("document").ready(function($){      
    zmenHash();
    var stranka = $("#stranka");
    var intervalDb;

    function menuNahore() {
        var menu = $('nav');
        var pozice = menu.offset().top;				

        $(window).scroll(function() {
            var fix = ($(this).scrollTop() > pozice) ? true : false;	
            menu.toggleClass("menu", fix);
            $('body').toggleClass("body-menu", fix);			
        });
    }


    function dnes() {
        var tik = new Date();      
        var den = tik.getDate();
        var mesic = tik.getMonth()+1;
        var rok = tik.getFullYear();
        var hodina = tik.getHours();
        var minuta = tik.getMinutes();
        var sekunda = tik.getSeconds();

        var vysledek = den + "." + mesic + "." + rok + " " + hodina + ":" + minuta;

        return vysledek;
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
        
        if(hash=="DB") {
            $("#stranka").load("/tabulky/");
            intervalDb = setInterval(function() {
                $("#stranka").load("/tabulky/");
            }, 3000);
        }
        else if(hash=="Otazky"){
            $.getJSON("/json/otazky/", function(json) {
                otazkyZobraz(json.otazky);	
            });
        }
        else if(hash=="Testy"){
            $.getJSON("/json/testy/", function(json) {
                testyZobraz(json.testy);	
            });
        } 
        else if(hash=="Nahrat"){
            $("#stranka").load("/upload/");
        }        
        else if(hash=="TestyVytvorit"){
            testyVytvorit();
        } 
        else if(hash=="OtazkyPridat"){
            otazkyPridat();
        }        
        

    }

    /************OTAZKY***************/
    function otazkyZobraz(otazky) {
        var text = "";

        var tlacitka =  
            '<span class="otTlacitka">\
                <button class="tlUpravit">Upravit</button>\
                <button class="tlSmazat">Smazat</button>\
            </span>';

        $.each(otazky, function(i, o) {
            text +=     
                '<div class="otazka" cislo="' + o.id + '">\
                    <span class="otId">' + o.id + '. </span>\
                    <span class="otNazev">' + o.jmeno + '</span>\
                    <span class="otZadani">' + o.zadaniHTML.replace("\n","<br>") + '</span>\
                </div>';
        });

        $("#stranka").html(text);
    }

    function otazkyUprav(idOtazky) {
        $("#stranka").load("/vzory/otazky/", nacteno);

        function nacteno() {
            $.getJSON("/json/otazky/" + idOtazky, function(otazka) {         
                $.each(otazka, function(i, o) {
                    stranka.find('#otJmeno').val(o.jmeno);
                    Simplemde.value(o.zadani), //soubor lista.js
                    stranka.find('#otId').text(o.id);
                    stranka.find('#SPRO').val(o.spravne[0]);
                    stranka.find('#SPO1').val(o.spatne[0]);
                    stranka.find('#SPO2').val(o.spatne[1]);
                    stranka.find('#SPO3').val(o.spatne[2]);
                    stranka.find('#SPO4').val(o.spatne[3]);
                    stranka.find('#SPO5').val(o.spatne[4]);
                    stranka.find('#SPO6').val(o.spatne[5]);
                });
            });
        }
    }   
 
    function otazkyPridat() {
        $("#stranka").load("/vzory/otazky/",function() {
            $("#stranka").find('h1#upravitOtazku').text("Přidat otázku"); 
        });
    }

    function otazkyOdeslat() {
        var idOtazky = stranka.find('#otId').text();
        var ukol = "pridat";      

        if(idOtazky)
            ukol = "upravit";

        var json = {
            akce: ukol, 
            co: 'otazka',
            id: idOtazky,
            jmeno: stranka.find('#otJmeno').val(),
            typ: stranka.find('#otTyp').val(),
            zadani: Simplemde.value(), //soubor lista.js
            spravne: [
                stranka.find('#SPRO').val()  
            ],
            spatne: [
                stranka.find('#SPO1').val(),
                stranka.find('#SPO2').val(),
                stranka.find('#SPO3').val(),
                stranka.find('#SPO4').val(),
                stranka.find('#SPO5').val(),
                stranka.find('#SPO6').val(),                
            ]
        };

        postJSON(json, 
            function(o) {
                console.log(o); 
                if(o.status != 500) {
                    hlaska(o.odpoved,8); 
                    window.location.hash = "Otazky";
                }
                else
                    hlaska(chybaServeru(o),0);
            }
        );
    }

    function otazkySmazat(idOtazky) {       
        dialog('Smazat otázku?',
            function() {//ano              
                var json = {
                    akce:'smazat', 
                    co:'otazka',
                    id: idOtazky
                };

                postJSON(json, 
                    function(o) {
                        console.log(o); 
                        if(o.status != 500) {
                            hlaska(o.odpoved,8); 
                            window.location.hash = "Otazky"; 
                        }
                        else
                            hlaska(chybaServeru(o),0);
                    }
                )
            },
            function() {}
        );
    }


    function tabulka(tabulka,ukol){       
        var zprava = 'Smazat tabulku ' + tabulka + '?';
        if(ukol=="vysypat")
            zprava = 'Vysypat tabulku ' + tabulka + '?';

        dialog(zprava,
            function() {//ano              
                var json = {
                    akce: ukol, 
                    co:'tabulka',
                    nazev: tabulka
                };

                postJSON(json, 
                    function(o) {
                        console.log(o); 
                        if(o.status != 500) {
                            hlaska(o.odpoved,20); 
                        }
                        else
                            hlaska(chybaServeru(o),0);
                    }
                )
            },
            function() {} //ne
        );
    }

    /*****************TESTY*******************/
    function testyZobraz(testy) {
        var text = "";

        var tlacitka =  
            '<span class="otTlacitka">\
                <button class="tlUpravit">Upravit</button>\
                <button class="tlSmazat">Smazat</button>\
            </span>';

        $.each(testy, function(i, o) {
            text +=     
                '<div class="test" cislo="' + o.id + '">\
                    <span class="ttNazev">' + o.jmeno + '</span>\
                    <span class="ttZadani">' + o.autor + '</span>\
                    <span class="ttOd">' + o.od + '</span>\
                    <span class="ttDo">' + o.do + '</span>\
                </div>';
        });

        $("#stranka").html(text);
    }

    function testyUprav(idTestu) {
        $("#stranka").load("/vzory/testy/");
        $.getJSON("/json/testy/", function(json) {
            $.each(json.testy, function(i, t) {
                if(t.id==idTestu) {
                    stranka.find('#ttNazev').val(t.jmeno);
                    stranka.find('#ttOd').val(t.od);
                    stranka.find('#ttDo').val(t.do);                    
                }
            });             	
        });   
    }

    function testyVytvorit() {        
        $("#stranka").load("/vzory/testy/",function(){
            nastavZnamky(1);
            var datum = dnes();
            stranka.find('h1#upravitTest').text("Přidat test");
            stranka.find('#ttOd').val(datum);
            stranka.find('#ttDo').val(datum);
        });
    }

    /****************UDALOSTI*********************/

    $(document).on("click", "#ttSmazat", function(e) {
        dialog('Smazat test?',
            function() {//ano
                hlaska("Smazáno",5);               
            },
            function() {//ne

            }
        );
    });

    $(document).on("click", "#otSmazat", function(e) {
        var idOtazky = stranka.find('#otId').text();       
        otazkySmazat(idOtazky);
    });

    $(document).on("click", "#otVlozit", function(e) {
        otazkyOdeslat();
    });

    $(document).on("click", ".otazka", function(e) {
        window.location.hash = "OtazkyUpravit";
        var idOtazky = e.currentTarget.attributes.cislo.value;
        otazkyUprav(idOtazky);
    });

    $(document).on("click", ".test", function(e) {
        window.location.hash = "TestyUpravit";   
        var idTestu = e.currentTarget.attributes.cislo.value;    
        testyUprav(idTestu);
    });   

    $(document).on("click", ".tbSmazat", function(e) {
        tabulka(e.target.value,"smazat");
    }); 

    $(document).on("click", ".tbVysypat", function(e) {
        console.log(e);
        tabulka(e.target.value,"vysypat");
    }); 
            
    /***********ZAKLADNI FUNKCE***************/

    function postJSON(json, odeslano) {
        $.ajax({
            url: '/json/post/',
            type: 'POST',
            data: JSON.stringify(json),
            contentType: 'application/json; charset=utf-8',
            dataType: 'json',
            async: true,
            success: odeslano,
            error: odeslano
        });
    }

    function chybaServeru(ch) {
        var najdi = ch.responseText.match(/<title>(.*?)<\/title>/);
        var chyba = "neznámá chyba";
        
        if (najdi)
            chyba = najdi[1].replace("// Werkzeug Debugger","");

        return "Flask: " + chyba;
    }

    function dialog(zprava, ano, ne) {    
        var div = document.createElement("div");
        div.className = "dialog";
        div.style.display = "block";
        var content = document.createElement("div");
        content.innerHTML = zprava;
        var potvrdit = document.createElement("button");
        potvrdit.innerHTML = "Ano";
        var zrusit = document.createElement("button");
        zrusit.innerHTML = "Ne";
  
        div.appendChild(content);
        div.appendChild(potvrdit);
        div.appendChild(zrusit );
        document.body.appendChild(div);

        potvrdit.onclick = function() {
          document.body.removeChild(div);
          ano();
        }
  
        zrusit.onclick = function() {
          document.body.removeChild(div);
          ne();
        };
    }
  
    function hlaska(text, cas) {
        var casovac;
        var div = document.createElement("div");   
        div.innerHTML = text;
        div.id = "hlaska";
        div.className = "zobrazit";       
        document.body.appendChild(div);   
        
        clearTimeout(casovac);

        div.onclick = function() {
            document.body.removeChild(div);
        }

        if(cas>0) {
            casovac = setTimeout(function() {
                if (document.contains(div))
                    document.body.removeChild(div);
            }, cas * 1000);
        }
    }

    window.onhashchange = zmenHash;
    window.addEventListener("error", zobrazitChybu, true);
    
    function zobrazitChybu(e) {
        if (e.message)
            hlaska(e.message + "<br>Řádek: " + e.lineno + ":" + e.colno + "<br>Soubor: " + e.filename);
        else
            hlaska("error: " + e.type + " from element: " + (e.srcElement || e.target));
    }




    









});