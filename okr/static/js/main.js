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
			url: '/okr/edit_kr/',
			data: request,
			dataType: 'json',
			success: function (res) {
				if (res['status'] == 'ok') {
					hideErrors(id);
					updateKR(id, res['data']);
					detailsMode(id);
				} else if (res['status'] == 'error') {
					showErrors(id, res['data']);
				}
			},
			error: function (xhr, errmsg, err) {
				alert('Oops! something went wrong.');
				detailsMode(id);
			}
		});
	});


	$("[id^=kredit-]").click(function() {
		id = $(this).attr('id').split('-')[1];
		if ( $('#details-' + id).is(':visible') ) {
			editMode(id);
		} else {
			detailsMode(id);
		}    
	});


	$("[id^=krcancel-]").click(function() {
		id = $(this).attr('id').split('-')[1];
		detailsMode(id);
	});

	// Binary type_data
	$('[id^=id_type_data]').change(function() {
		if ($(this).find('option:selected').val() == '2') {
			edit_panel = $(this).parents('[id^=edit-]');
			edit_panel.find('#id_expected').val(1);
			edit_panel.find('#id_obtained').val(0);
		}
	});

	$('#cancel').click(function() {
		window.location.href = '/okr/';
	});

	// Datepicker calendar
	$('#id_end_date').datepicker()

	// Delete: are you sure?
	$('.delete').click(function(e) {
        e.preventDefault();
        if (window.confirm("Are you sure?")) {
            location.href = this.href;
        }
    });
});


// Show and hide while we are editing
function editMode(id) {
	// Update the form fields
	updateKRFields(id)

	// If a edit panel is open and it is above this, when we'll hide
	// and we'll scroll down, the offset will be incorrect
	added = 0
	our_offset = $('#kr-' + id).offset().top;

	// Check if there is a edit panel open above of this
	$('[id^=edit-]').not('#edit-' + id).each(function() {
		other_id = $(this).attr('id').split('-')[1];
		edit_panel = $('#edit-' + other_id);

		if ( edit_panel.is(':visible') ) {
			if ( edit_panel.offset().top < our_offset ) {
				added = edit_panel.height() + $('#details-' + id).height() + 25;
				return;
			}
		}
	});


	// Hidden the rest edits
	$('[id^=edit-]').not('#edit-' + id).hide(DURATION_ANIMATION);
	$('[id^=details-]').not('#details-' + id).show(DURATION_ANIMATION);

	$('#details-' + id).hide(DURATION_ANIMATION);
	$('#edit-' + id).show(DURATION_ANIMATION);
	
	// scroll
	var offset = $('#kr-' + id).offset().top - 25 - added;
	$('html').animate({	scrollTop: offset }, DURATION_ANIMATION);
}


function detailsMode(id) {
	$('#details-' + id).show(DURATION_ANIMATION);
	$('#edit-' + id).hide(DURATION_ANIMATION);

	// scroll
	var offset = $('#kr-' + id).offset().top - 25;
	$('html').animate({	scrollTop: offset }, DURATION_ANIMATION);
}


function showErrors(id, errs) {
	for(var field in errs) {
		f = $('#krerror-' + id + '-' + 'id_' + field);
		f.text(errs[field]);
		f.show();
	}
}


function hideErrors(id) {
	$("[id^=krerror-" + id + "-]").hide();
}


// Update key result after editing
function updateKR(id, data) {
	$('#krname-' + id).text(data['name']);
	$('#krprogress-' + id).css({'width': data['percentage'] + '%'});
	$('#krprogress-' + id).find('span').text(data['percentage'] + '%');
	$('#details-' + id).text(data['details']);
}


// Update key result fields form before editing
function updateKRFields(id) {
	// Ajax request
	$.ajax({
		type: 'GET',
		url: '/okr/show_kr/' + id,
		dataType: 'json',
		success: function (data) {
			$('#edit-' + id).find('#id_name').val(data['name']);
			$('#edit-' + id).find('#id_type_data').val(data['type_data']);
			$('#edit-' + id).find('#id_expected').val(data['expected']);
			$('#edit-' + id).find('#id_obtained').val(data['obtained']);
			return true;
		},
		error: function (xhr, errmsg, err) {
			return false;
		}
	});	
}