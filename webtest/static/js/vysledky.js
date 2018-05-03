function vysledkyZobrazSeznam() {
    $.getJSON("./json/vysledky/seznam/", function(json) {     
        $.each(json.vysledky, zobrazit);
        $(stranka).html(text);
    }).fail(chybaIframe);

    var text = "<h1>Výsledky</h1>";

    function zobrazit(i, v) {
        text +=     
            '<div class="vysledek" cislo="' + i + '">\
                <span class="vsId">' + i + '. </span>\
                <span class="vsTest">' + v.jmeno + '</span>\
                <span class="vsPocet"> - výsledků: ' + v.vysledku + '</span>\
            </div>';
    };
}


function vysledkyTabulka(idTestu) {
    $.getJSON("./json/vysledky/" + idTestu, function(json) {
        if(idTestu)
            $.each(json.vysledky, zobrazitUcitel);
        else
            $.each(json.vysledky, zobrazitStudent);
        
        $(stranka).html(`<h1>Výsledky</h1><table>${tabulka}</table>`);
    }).fail(chybaIframe);

    var tlacitko = "<button class='vsZobrazit'>Zobrazit</button>";

    var tabulka =  
        "<tr>\
            <th>id</th>\
            <th>Jméno</th>\
            <th>Zahájeno</th>\
            <th>Ukončeno</th>\
            <th>Limit</th>\
            <th>Čas</th>\
            <th>Pokus</th>\
            <th>Bodů</th>\
            <th>%</th>\
            <th>Známka</th>\
            <th>Student</th>\
            <th>Třída</th>\
            <th></th>\
        </tr>";

    function zobrazitUcitel(i, v) {
        tabulka += tab(v);
    };

    function zobrazitStudent(i, v) {
        cl(v);
        $.each(v, function(y, s) {
            tabulka += tab(s);
        });
    };

    function tab(v) {
        var obsah =
            `<tr>\
                <td>${v.id}</th>\
                <td>${v.jmeno}</th>\
                <td>${v.casZahajeni}</th>\
                <td>${v.casUkonceni}</th>\
                <td>${v.limit}</th>\
                <td>${v.cas}</th>\
                <td>${v.pokus}</th>\
                <td>${v.boduVysledek}</th>\
                <td>${v.procent.zaokrouhlit(2)}</th>\
                <td>${v.znamka}</th>\
                <td>${v.student.prijmeni}</th>\
                <td>${v.student.trida}</th>\  
                <td>${tlacitko}</th>\      
            </tr>`;
        return obsah;
    }
}

function vysledkyZobraz(id) { 
    $.getJSON("./student/vyhodnotit/" + id, zpracujJSON).fail(chybaIframe);
    text = "";

    function zpracujJSON(json) {
        if(!json.test) {
            hlaska(json.odpoved,4);
            return;
        }


        var test = json.test;
        var otazky = json.test.otazky;
        var hodnoceni = test.hodnoceni;

        text += "<h1>Hodnocení testu</h1>";
        text += "Maximální počet bodů: " + test.boduMax + "<br>";
        text += "Výsledný počet bodů: " + test.boduTest + "<br>";
        text += "Výsledek: " + test.procent.zaokrouhlit(2) + " %<br>";
        text += "Známka: " + test.znamka + "<br>";
        text += "Hodnocení: " + hodnoceni + "<br>";

        $.each(otazky, zpracujOtazky);

        $(stranka).html(text);
        mathjax();
    }
    
    function zpracujOtazky(i, otazky) {
        var typ = "odSpatne";
        if(otazky.hodnoceni == otazky.bodu)
            typ = "odDobre";
        
        text += `<h2 class='${typ}'>Otázka: ${otazky.jmeno}
            (${otazky.hodnoceni} / ${otazky.bodu})</h2>`;
        
        text += otazky.zadani + "<br>";

        var oznaceno = "";

        $.each(otazky.zadaniDobre, function(i, od) {
            text += zobrazOdpoved(od,"odDobre");
        });

        $.each(otazky.zadaniSpatne, function(i, od) {
            text += zobrazOdpoved(od,"odSpatne");
        });

        $.each(otazky.zadaniOtevrena, function(i, od) {
            text += `<span class='odOtevrena'>${otazky.zadaniOtevrena}</span>`;
            text += `<span class='odSipka'>→</span>`;
            if(otazky.oznaceneSpatne)
                text += `<span class="odSpatne">${otazky.oznaceneSpatne}</span>`; 
            if (otazky.oznaceneDobre)
                text += `<span class="odDobre">${otazky.oznaceneDobre}</span>`; 
        });

        function zobrazOdpoved(odpoved,typ) {
            if (oznacit(odpoved,typ)) oznaceno = "oznaceno";
            else oznaceno = "";
            return `<div class='${typ} ${oznaceno}'>${odpoved}</div>`;
        }

        function oznacit(odpoved,typ) {
            if (typ == "odDobre" && isInArray(odpoved,otazky.oznaceneDobre))
                return true;
            if (typ == "odSpatne" && isInArray(odpoved,otazky.oznaceneSpatne)) 
                return true;
            if (typ == "odOtevrena" && isInArray(odpoved,otazky.oznaceneOtevrena)) 
                return true;
            return false;
        }
    }
}