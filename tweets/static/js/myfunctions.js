/*$(function(){
    $('.btn-circle-custom').mouseover(function(){
        $(this).removeClass('.btn-circle-custom')
        $(this).addClass('btn-circle-custom-hover')
    })
    $('.btn-circle-custom-hover').mouseout(function(value){
        $(this).removeClass('btn-circle-custom-hover')
        $(this).addClass('btn-circle-custom')
    })
});*/


$(function () {

    $("#myTags").tagit();
    $('#search').tagit();
    $('.img-home').mouseover(function (value) {
        var ob = $(this)
        ob.find('.dropdown-img').show();
        ob.find('.top-img').show();
        ob.find('img').css('opacity','0.6');
        ob.find('button').css('opacity','1');

    })
    $('.img-home').mouseout(function (value) {
        var ob = $(this)
        ob.find('.dropdown-img').hide();
        ob.find('.top-img').hide();
        ob.find('img').css('opacity','1');
    })

    $('.profile-gift').click(function () {
        var id_gift = $(this).closest('ul').attr('id');
        var id_list = $(this).attr('id')
        var data_send = {
            'id_gift': id_gift,
            'id_list': id_list
        }
        var url = 'guardar_gift'
        send_data_url(data_send, url)
    })

});

$(function () {
    $("#caract").tagit();

    $('#upload').click(function (ev) {
        ev.preventDefault()

        var foto = document.getElementById('photo').files[0]
        var name = $('#name').val()
        var list = $('#lists').val()
        var description = $('#description').val()
        var caracteristicas = $("#caract").tagit("assignedTags")
        var tienda = $("#tienda").val()
        var url = $("#url").val()
        var precio = $('#precio').val()
        var visibility = $('#visibility').val()
        var score = $('#score').val()

        var formData = new FormData()

        formData.append('name', name)
        formData.append('list', list)
        formData.append('description', description)
        formData.append('caracteristicas', caracteristicas)
        formData.append('tienda', tienda)
        formData.append('url', url)
        formData.append('precio', precio)
        formData.append('visibility', visibility)
        formData.append('photo', foto)

        var url = 'create_gift'
        send_image_url(formData, url)
    })

});

$(function () {
    $('#upload_list').click(function () {
        var profile = $('#profiles').val()
        var name = $('#name').val()
        var visibility = $('#visibility').val()
        var caracteristicas = $("#caract").tagit("assignedTags")
        
        var data_send = {
            profile:profile,
            name:name,
            visibility:visibility,
            caracteristicas:caracteristicas
        }
        var url = 'create_list'
        send_data_url(data_send,url)
    })
    $('#topic_profile').tagit()
    $('#upload_profile').click(function(){
        var name = $('#name_profile').val()
        var gender = $('#gender_profile').val()
        var caracteristicas = $("#topic_profile").tagit("assignedTags")
        var age = $("#age_profile").val()

        var data_send = {
            name:name,
            gender:gender,
            like_list:caracteristicas.toString(),
            age:age
        }
        var url = 'create_profile'
        send_data_url(data_send,url)
    })
    
})
$(function() {
    $('.jcarousel').jcarousel();

    $('.jcarousel-control-prev')
        .on('jcarouselcontrol:active', function() {
        $(this).removeClass('inactive');
    })
        .on('jcarouselcontrol:inactive', function() {
        $(this).addClass('inactive');
    })
        .jcarouselControl({
        target: '-=1'
    });

    $('.jcarousel-control-next')
        .on('jcarouselcontrol:active', function() {
        $(this).removeClass('inactive');
    })
        .on('jcarouselcontrol:inactive', function() {
        $(this).addClass('inactive');
    })
        .jcarouselControl({
        target: '+=2'
    });


})
function send_data_url(data_send, url) {
    var csrftoken = getCookie('csrftoken')
    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });

    $.ajax({
        url: url,
        type: "POST",
        data: data_send,
        success: function (response) {
            location.reload()
        },
        error: function (error, response) {
            alert('error ' + error.message)
        }
    })
}

function send_image_url(data_send, url) {
    var csrftoken = getCookie('csrftoken')
    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });

    $.ajax({
        url: url,
        type: "POST",
        data: data_send,
        processData: false,
        contentType: false,
        success: function (response) {
            //alert('status: '+response+')
        },
        error: function (error, response) {
            alert('error ' + error.message)
        }
    })
}

function csrfSafeMethod(method) {
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}