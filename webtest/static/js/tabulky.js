function studentZobrazTabulku(nacteno) {
    $.getJSON("./json/studenti/", zpracujJSON).fail(chybaIframe);

    var tabulka = tabulkaHlavicka(["id", "Login", "Jméno", "Příjmení", "Třída", ""]);

    function tlacitko(text) {
        return "<button class='radekAkce'>" + text + "</button>";
    }

    function zpracujJSON(json) {
        $.each(json.studenti, zobrazTabulku);
        var select = `<select class="tbTridy">
                <option selected value="null">null</option>\
            </select>`;
        tabulka += tabulkaRadek(4, ["", "", "", "", select, tlacitko("Přidat")]);
        nacteno("<table class='tabDb' nazev='Student'>" + tabulka + "</table>");
    }

    function zobrazTabulku(i, t) {
        var select =
            `<select class="tbTridy" hodnota="${t.trida.id}">\
                <option selected value="null">null</option>\
                <option selected value="${t.trida.id}">${t.trida.nazev}</option>\
            </select>`;
        tabulka += tabulkaRadek(4, [t.id, t.login, t.jmeno, t.prijmeni, select, tlacitko("Smazat")]);
    }
}

function studentZobraz() {
    studentZobrazTabulku(function (tabulka) {
        var nadpis = "<h1>Studenti</h1>";
        $(stranka).html(nadpis + tabulka);
    });
    var option = "";

    $.getJSON("./json/tridy/", function (json) {
        $.when($.each(json.tridy, nactiTridy)).done(nacteno);
    }).fail(chybaIframe);

    function nactiTridy(i, t) {
        option += '<option value=' + t.id + '>' + t.poradi + t.nazev + '</option>';
    }

    function nacteno() {
        $(stranka).find(".tbTridy").append(option); 
    }
}

function uciteleZobrazTabulku() {
    $.getJSON("./json/ucitele/", zpracujJSON).fail(chybaIframe);

    var tabulka = tabulkaHlavicka(["id", "Login", "Jméno", "Příjmení", "Admin", ""]);

    function tlacitko(text) {
        return `<button class='radekAkce'>${text}</button>`;
    }

    function checkbox(tf) {
        var checked = "";
        var hodnota = false;
        if (tf == true) {
            checked = "checked";
            hodnota = "true";
        }
        return `<input ${checked} class="tabCh" type="checkbox" value="${hodnota}">`;
    }

    function zpracujJSON(json) {
        $.each(json.ucitele, zobrazTabulku);
        tabulka += tabulkaRadek(4, ["", "", "", "", checkbox(false), tlacitko("Přidat")]);
        $(stranka).html("<table class='tabDb' nazev='Ucitel'>" + tabulka + "</table>");
    }

    function zobrazTabulku(i, t) {
        tabulka += tabulkaRadek(4, [t.id, t["login"], t.jmeno, t.prijmeni, checkbox(t.admin), tlacitko("Smazat")]);
    }
}

function slovnikZobrazTabulku(nacteno) {
    $.getJSON("./json/slovnik/", zpracujJSON).fail(chybaIframe);

    var tabulka = tabulkaHlavicka(["id", "Slovo 1", "Slovo 2", "Kategorie", "Jazyk", ""]);

    function tlacitko(text) { return "<button class='radekAkce'>" + text + "</button>"; }

    function zpracujJSON(json) {
        $.each(json.slovnik, zobrazTabulku);
        tabulka += tabulkaRadek(5, ["", "", "", "", "", tlacitko("Přidat")]);
        nacteno("<table class='tabDb' nazev='Slovnik'>" + tabulka + "</table>");
    }

    function zobrazTabulku(i, t) {
        tabulka += tabulkaRadek(5, [t.id, t.slovo1, t.slovo2, t.kategorie, t.jazyk, tlacitko("Smazat")]);
    }
}

function tridyZobrazTabulku(nacteno) {
    $.getJSON("./json/tridy/", zpracujJSON).fail(chybaIframe);

    var tabulka = tabulkaHlavicka(["id", "Pořadí", "Název", "Rok", ""]);

    function tlacitko(text) { return "<button class='radekAkce'>" + text + "</button>"; }

    function zpracujJSON(json) {
        $.each(json.tridy, zobrazTabulku);
        tabulka += tabulkaRadek(4, ["", "", "", "", tlacitko("Přidat")]);
        nacteno("<table class='tabDb' nazev='Tridy'>" + tabulka + "</table>");
    }

    function zobrazTabulku(i, t) {
        tabulka += tabulkaRadek(4, [t.id, t.poradi, t.nazev, t.rokUkonceni, tlacitko("Smazat")]);
    }
}

function tabulkaZmenitZaznam(e) {
    var radek = e.target.parentElement.parentElement;
    var tabNazev = radek.parentElement.parentElement.attributes.nazev.value;

    var tlacitko = this;
    var text = $(tlacitko).text();
    var akce = 'smazat';

    if (text == "Změnit")
        akce = 'zmenit';

    //ziska seznam bunek v tabulce (krome 1. a posledni)
    var seznamBunek = [];
    var prazdnych = 0;

    for (i = 1; i < radek.childElementCount - 1; i++) {
        var bunka = radek.children[i].firstChild.value;
        if (bunka != "")
            seznamBunek.push(bunka);
        else 
            prazdnych++;
    }

    if (prazdnych > 0) {
        hlaska("Všechny sloupce musí být vyplněny!", 3);
        return;
    }

    var json = {
        akce: akce,
        co: 'radek',
        tabulka: tabNazev,
        id: $(radek.firstChild).text(),
        bunky: seznamBunek
    }

    cl(json);
    postJSON(json, odpovedJSON);
    if (tabNazev == "Tridy")
        tridyZobraz();

    switch (tabNazev) {
        case "Tridy": tridyZobraz(); break;
        case "Student": studentZobraz(); break;
        case "Slovnik": slovnikZobraz(); break;
        case "Ucitel":  uciteleZobrazTabulku(); break;
    }
}

function tabulkyZmenaHodnoty(e) {
    var tlacitko = e.currentTarget.parentElement
    .parentElement.lastChild.firstChild;

    $(tlacitko).text("Změnit");
}