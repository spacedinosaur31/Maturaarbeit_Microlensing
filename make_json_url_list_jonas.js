// dieses Programm wurde mithilfe von Jonas Frey geschrieben

var s_url = "https://irsa.ipac.caltech.edu/data/ZTF/lc/lc_dr11/1/" // var creates a variable

var a_o_url = Array.prototype.slice.call(document.querySelectorAll("a")) //gehe ins Webseitengerüst-Dokument und wähle alles mit "a" ("a"= hyperlink = Webseiten-Adresse)
// obern: erstellt array gefüllt mit Links

var a_s_url_part = a_o_url.map(o=>o.href).filter(s=>s.includes("field")) //o und s sind Laufvariablen, .map ist wie for loop (inspiriert von funcitonal programming)
//o.href = Attribut -> schlussendliche Adresse (Link kann anderen Namen im Vordergrund haben -> .href garantiert, dass es http://...ist)
// falls "field" in o.href ist, tue o.href in a_s_url_part


var a_s_url_parquet = [] // ein leeres Array wird definiert

const parser = new DOMParser(); //DOMParser = Maschine im Hintergrund 
//const = Deklarierung -> parser wird nicht überschrieben (Vermeidung von unberechenbaren Problemen)


for(var s_url_part of a_s_url_part){

    var o_response = await fetch(s_url_part); //await = asynchrones Data-Fetching -> warte, bis das darauffolgende geschafft ist, bevor du mit nächster Zeile weitermachst
    // fetch(x) ruft x auf
    var s_response = await o_response.text() // x.text() holt text aus x -> "xy"

    let o_document = parser.parseFromString(s_response, "text/html");
    // let ähnlich wie var
    //hol mir die Seite in html-Format

    var o_nodelist_a = o_document.querySelectorAll("a");
    // alle mit tag "a"
    
    console.log("length")
    console.log(o_nodelist_a.length)
    //console.log(x) = print(x)

    a_s_url_parquet = a_s_url_parquet.concat(Array.prototype.slice.call(o_nodelist_a).map(o=>s_url_part+o.href.split("/").pop()).filter(s=>s.includes(".parquet")))
    // setzt endgültigen Link zusammen
    //.split("/").pop() -> lösche bis Schrägstrich und hänge absoluten Pfad vorne an mit field (sodass man nicht immer durch alle Ordner muss sodnern direkt)
    console.log(a_s_url_parquet)
    // console.log(o_document.querySelectorAll("a")[5].href)
}
JSON.stringify(a_s_url_parquet) // macht .json-file = -> {"data":"data"}
//
