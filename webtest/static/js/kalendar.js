function kalendar(umisteni, mesic, rok, potvrdit) {
	var datum = new Date();
	var denDnes = datum.getDate();
	var mesicDnes = datum.getMonth() + 1;
	var rokDnes = datum.getFullYear();

	if(rok!=0) {
		mesicDnes = mesic;
		rokDnes = rok;

		//test jestli datum zacina 0
		if (mesicDnes.substring(0,1) == "0") {
			mesicDnes = mesicDnes.substring(1);
		}
		
		if (rokDnes.substring(0,1) == "0")
			rokDnes = rokDnes.substring(1);				
	}

	zobrazSkryjKalendar(umisteni, mesicDnes, rokDnes);

	//funkce spuštěna při kliknutí na ikonu kalendáře ve formuláři
	function zobrazSkryjKalendar(umisteni,mesic,rok) {
		var kal = document.getElementById("kalendar1");
		
		if(kal) {
				zavritKalendar(kal);
				return;
		}

		div = document.createElement('div');
		div.id = "kalendar1";
		div.innerHTML = vytvorKalendar(mesic,rok);
		div.style.display = "none";
		$('.kalendar[input="' + umisteni + '"').after(div);
		$(div).fadeIn(300);
	}

	function vytvorKalendar(mesic, rok) {
		if(mesic==0) mesic = mesicDnes;
		if(rok==0) rok = rokDnes;

		var dnes = new Date();      //aktuální datum
		var nazevMesice = new Array("", "leden", "únor", "březen", "duben", "květen", 
				"červen", "červenec", "srpen", "září", "říjen", "listopad", "prosinec");
		
		//1. den v zadaném měsíci - v JS se měsíce číslují od 0, proto musíme odečíst 1
		var datum = new Date(rok, mesic - 1, 1); 
		
		//číslo dne v týdnu 0 = NE, 6 = SO
		var denTyd = datum.getDay();
		if (denTyd == 0)
			denTyd = 7;
		
		//počet dní v měsíci
		var pocetDniMesice = new Array(0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31);

		if (((rok % 4 == 0) && (rok % 100 != 0)) || (rok % 400 == 0))
			pocetDniMesice[2] = 29;   //přestupný rok - únor 29 dní

		var tab = "<table>\
				<tr>\
					<th class='kalPredchozi'>&lsaquo;&lsaquo;</th>\
					<th class='kalMesic' colspan='5'>" + nazevMesice[mesic] + " " + rok + "</th>\
					<th class='kalDalsi'>&rsaquo;&rsaquo;</th>\
				</tr>\
				<tr>\
					<th>Po</th>\
					<th>Út</th>\
					<th>St</th>\
					<th>Čt</th>\
					<th>Pá</th>\
					<th>So</th>\
					<th>Ne</th>\
				</tr>\
				<tr>";

		for (i = 1; i < denTyd; i++)
			tab += "<td></td>"; //prázdné buňky před 1. dnem měsíce

		for (den = 1; den <= pocetDniMesice[mesic]; den++) {
			if (rok == dnes.getFullYear() && mesic == dnes.getMonth() + 1 && den == dnes.getDate())
				styl = "dnes";
			//else if(rok==r && mesic==m && den==d) {styl="akt";}
			else
				styl = "";
			tab += "<td class='kalDen" + styl + "'>" + den + "</td>";
			if (i % 7 == 0 && den != pocetDniMesice[mesic])
				tab += "</tr><tr>";
			i++;
		}
		for (i = i - 1; i % 7 != 0; i++) {
			//prázdné buňky za posledním dnem měsíce pro dokončení tabulky
			tab += "<td></td>";
		}
		tab += "</tr></table>";
		return tab;
	}

	function zavritKalendar(kal) {
		$(kal).fadeOut(300, function() {$(this).remove();});
	}
	
	//kliknout na mesic v kalendari
	$(document).on("click", ".kalMesic", function (e) {
		var kal = document.getElementById("kalendar1");
		zavritKalendar(kal);
	});

	//kliknut na << v kalendáři
	var intervalPred;
	$(document).on("mousedown", ".kalPredchozi", function (e) {
		intervalPred = setInterval(function() {
			if (mesicDnes == 1) {
				rokDnes--;
				mesicDnes = 12;
			}
			else
				mesicDnes--;
	
			$("#kalendar1").html(vytvorKalendar(mesicDnes, rokDnes));
		}, 100);
	}).mouseup(function() {
		clearInterval(intervalPred);
	});

	//kliknut na >> v kalendáři
	var intervalDalsi;
	$(document).on("mousedown", ".kalDalsi", function (e) {
		intervalDalsi = setInterval(function() {
			if (mesicDnes == 12) {
				rokDnes++;
				mesicDnes = 1;
			}
			else
				mesicDnes++;

			$("#kalendar1").html(vytvorKalendar(mesicDnes, rokDnes));
		},100);
	}).mouseup(function() {
		clearInterval(intervalDalsi);
	});

	//ziskat datum z kalendare
	$(document).on("click", ".kalDen", function (e) {
		var dat = new Object();

		dat.den = e.target.innerText;	
		dat.mesic = mesicDnes;
		dat.rok = rokDnes;
		var kal = document.getElementById("kalendar1");
		zavritKalendar(kal);
		potvrdit(dat);
		//zabranit aby se callback vykonal nekolikrat
		potvrdit = new Function();
	});
}