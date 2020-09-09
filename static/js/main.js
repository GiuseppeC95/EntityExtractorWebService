var tooltipOptions = {
    placement: 'top',
    boundary: 'viewport',
    trigger: 'hover',
    html: true
};

$(document).ready(function () {
    // Custom toolbar per elencare le occorrenze. Tolgo la standard e immetto la custom
    $('.defaultScrollStartup').removeClass("defaultScrollStartup");
    //The passed argument has to be at least a empty object or a object with your desired options
    var instances=$('.customScroll').overlayScrollbars({

        className       : "os-theme-dark",
        overflowBehavior: {
            x: "scroll"
        },
        scrollbars : {
            clickScrolling : true,
            touchSupport: true
        }
    }).overlayScrollbars();

    //Chiudo l'anteprima col bottone X
    $('#navClose').click(sideBarClose2);



    $('.rightScroll').click(function () {
        var scrollbar=$(this).parent().find('.customScroll').overlayScrollbars();
        scrollbar.scroll({ x : "+= 1vw", y  : 0 },150);
    });

    $('.leftScroll').click(function () {
        var scrollbar=$(this).parent().find('.customScroll').overlayScrollbars();
        scrollbar.scroll({ x : "-= 1vw", y  : 0 },150);
    });
    console.log(instances);

    $('[data-toggle="tooltip"]').tooltip(tooltipOptions);


});


/*Per evitare l'animazione di apertura della stessa occorrenza, ho inserito un if
* che controlla se sto aprendo la stessa occorrenza. Al momento discrimino ogni occorrenza
* con id della lezione(da sola non basta) e il timecode dell'occorrenza.
* Il modo migliore sarebbe avere un id univoco per ogni occorrenza*/
lastVideoId=null;
lastTimecode=null;

/*Apre la sessione di anteprima con l'occorrenza richiesta.
Richiamo questa funzione direttamente dal HTML, che invia come argomento il l'oggetto occorrenza */
function sideBarClose(videoOccurrence) {
    $('#sidebar').toggleClass('active', true);
    if (videoOccurrence.Lesson.id != lastVideoId && videoOccurrence.timecode!=lastTimecode) {
        $('#sidebar .container').fadeOut(100, function () {
            lastVideoId = videoOccurrence.Lesson.id;
            lastTimecode = videoOccurrence.timecode;
            $('#occurrenceTitle').text(videoOccurrence.Lesson.name);
            $('#occurrenceDate').text(new Date(videoOccurrence.Lesson.date).toLocaleDateString());
            $('#occurrenceDescr').text(videoOccurrence.Lesson.description);
            $('#occurrenceImg').attr("src", videoOccurrence.imgUrl); // TODO: modificare con url_source

            //Timecode is in smpte format
            var t = Timecode(videoOccurrence.timecode);
            timecode=calcTimecode(t);
            $('#occurrenceTimecode').text(timecode);
            var speechString="";
            videoOccurrence.speechTokenArray.forEach(function (speechToken,index) {
                var entityTokens=videoOccurrence.entityTokens;
                var entity=false;
                if(Array.isArray(entityTokens) && entityTokens.length){
                    if(index==entityTokens[0]){
                        entity=true;
                        speechString+=" <strong>"+speechToken+" </strong>";
                        entityTokens.shift();
                    }else
                        entity=false;
                }
                if(!entity)
                    speechString+=" "+speechToken;
            });
            $('#occurrenceSpeech').html(speechString);

            console.log(videoOccurrence.Lesson.videoUrl)
            var occurrenceUrl="static/video/01   Introduzione.mp4"+"#t="+timecode;
            console.log(occurrenceUrl);
            $('.playOccurrence').attr("href", occurrenceUrl);
        }).fadeIn(200);

    }

}
/*Si attiva premendo la X del pannello di anteprima occorrenze*/
function sideBarClose2() {
    $('#sidebar').toggleClass('active');
    lastVideoId=null;
}

/*Il minutaggio dei video è una stringa in standard smpte ("HH:MM:SS:FF" oppure "HH:MM:SS;FF", con FF il numero del
* frame video corrispondente). Visualizzare i frame nel front-end è superfluo, così come le ore nel caso fossero zero*/
function calcTimecode(smpte) {
    tc="";
    if(!smpte.hours==0)
        tc+=(smpte.hours < 10 ? '0' : '') + smpte.hours +":";
    tc+=(smpte.minutes < 10 ? '0' : '') + smpte.minutes+":";
    tc+=(smpte.seconds < 10 ? '0' : '') + smpte.seconds;
    return tc;
}

