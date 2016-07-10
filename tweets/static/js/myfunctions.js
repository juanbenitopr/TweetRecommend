$(function () {
    var array_tweets = []

    $('.btn-select-category').click(function () {
        var ob = $(this)
        var category_id = ob.attr('id')
        var tweet_id = ob.closest('.panel-footer').attr('id')
        var obj_aux = {
            tweet_id: tweet_id,
            category_id: category_id
        }
        array_tweets.push(obj_aux)
        ob.removeClass('btn-select-category')
        ob.addClass('btn-selected-category')
    })


    $('.btn-retweet').click(function () {
        $(this).text('Retweeted')
        $(this).removeClass('btn-retweet')
        $(this).addClass('btn-retweeted')
        var tweet_id = $(this).closest('.panel-footer').attr('id')
        var obj_aux = {
            tweet_id: tweet_id,
            retweeted: true
        }
        array_tweets.push(obj_aux)
    })
    $('.btn-retweeted').click(function () {
        $(this).text('Retweet')
        $(this).removeClass('btn-retweeted')
        $(this).addClass('btn-retweet')
        var obj_aux = {
            tweet_id: tweet_id,
            retweeted: false
        }
        array_tweets.push(obj_aux)
    })

    $('.btn-circle-custom').click(function () {
        send_data_url({data_send:JSON.stringify(array_tweets)},'http://localhost:4000')
    })
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