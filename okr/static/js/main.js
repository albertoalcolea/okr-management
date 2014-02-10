var DURATION_ANIMATION = 250


// CSRF
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

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

function sameOrigin(url) {
    // test that a given url is a same-origin URL
    // url could be relative or scheme relative or absolute
    var host = document.location.host; // host + port
    var protocol = document.location.protocol;
    var sr_origin = '//' + host;
    var origin = protocol + sr_origin;
    // Allow absolute or scheme relative URLs to same origin
    return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
        (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
        // or any other URL that isn't scheme relative or absolute i.e relative.
        !(/^(\/\/|http:|https:).*/.test(url));
}

$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && sameOrigin(settings.url)) {
            // Send the token to same-origin, relative URLs only.
            // Send the token only if the method warrants CSRF protection
            // Using the CSRFToken value acquired earlier
            xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
        }
    }
});




$(document).ready(function() {
	$("[id^=krbtn-]").click(function() {
		id = $(this).attr('id').split('-')[1];

        // Ajax request
        var request = {
            'id'        : id,
            'name'      : $('#edit-' + id).find('#id_name').val(),
            'type_data' : $('#edit-' + id).find('#id_type_data option:selected').val(),
            'expected'  : $('#edit-' + id).find('#id_expected').val(),
            'obtained'  : $('#edit-' + id).find('#id_obtained').val()
        };

		$.ajax({
            type: 'POST',
			url: '/okr/ajax_test/',
			data: request,
            dataType: 'json',
			success: function (res) {
                updateKR(id, res);
			},
			error: function (xhr, errmsg, err) {
                alert('Oops! something went wrong.')
			}
		});
		return false;
	});


    $("[id^=kredit-]").click(function() {
        id = $(this).attr('id').split('-')[1];
        if ( $('#details-' + id).is(':visible') ) {
            editMode();
        } else {
            detailsMode();
        }    
    });


    $("[id^=krbtn-]").click(function() {
        id = $(this).attr('id').split('-')[1];
        detailsMode();
    });
});


// Show and hide while we are editing
function editMode() {
    $('#details-' + id).hide(DURATION_ANIMATION);
    $('#edit-' + id).show(DURATION_ANIMATION);
    $('html, body').animate({
        scrollTop: $('#kr-' + id).offset().top - 25
    }, DURATION_ANIMATION);
}


function detailsMode() {
    $('#details-' + id).show(DURATION_ANIMATION);
    $('#edit-' + id).hide(DURATION_ANIMATION);
    $('html, body').animate({
        scrollTop: $('#kr-' + id).offset().top - 25
    }, DURATION_ANIMATION);
}


// Update key result after editing
function updateKR(id, data) {
    $('#krname-' + id).text(data['name']);
    $('#krprogress-' + id).css({'width': data['percentage'] + '%'});
    $('#krprogress-' + id).find('span').text(data['percentage'] + '%');
    $('#details-' + id).text(data['details']);
}