$(document).ready(function () {

    // TODO: Controllare meglio questa custom toolbar (può essere interessante per elencare le videolezioni)
    $(function() {
        $('.defaultScrollStartup').removeClass("defaultScrollStartup")
        //The passed argument has to be at least a empty object or a object with your desired options
        $('.customScroll').overlayScrollbars({

            className       : "os-theme-dark",
            overflowBehavior: {
                x: "scroll",
                y: "scroll"
            },
            scrollbars : {
                clickScrolling : true,
                touchSupport: true
            }
        });
    });

    $('#sidebarCollapse').on('click', function () {
        $('#sidebar').toggleClass('active');
    });

});