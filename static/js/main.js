$(document).ready(function () {

    //TODO: Controllare meglio questa custom toolbar (può essere interessante per elencare le videolezioni)
    // $('#sidebar').mCustomScrollbar({
    //      theme: "minimal"
    // });

    $('#sidebarCollapse').on('click', function () {
        $('#sidebar').toggleClass('active');
    });

});