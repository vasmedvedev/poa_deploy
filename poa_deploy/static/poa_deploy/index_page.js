$( document ).ready(function() {
	$( "form#app_add_form" ).submit(function( event ) {
		var appURL = $( this ).attr( "action" );
		var postData = $( this ).serializeArray();
		var csrftoken = getCookie('csrftoken');
		postData.push({name: 'csrfmiddlewaretoken', value: csrftoken});
		if ($( "p#app_error" ).length == 0) {
			$( "form#app_add_form" ).append( "<p id='app_error' style='color:green'>Adding application...</p>" );
		} else {
			$( "p#app_error" ).replaceWith( "<p id='app_error' style='color:green'>Adding application...</p>" );
		}
		$.ajax({
			url: appURL,
			type: "POST",
			data: postData,
			success: function(data) {
				if (data['status'] == 0) {
					$( "#app_error" ).replaceWith( "<p id='app_error' style='color:green'>Application added</p>" );
				} else if (data['status'] == 1) {
					$( "#app_error" ).replaceWith( "<p id='app_error' style='color:red'>Cannot import application</p>" );
				}
			} // success function
		}) // $.ajax
		event.preventDefault();
	}); // $app_add_form
	$( "form#app_install_form" ).submit(function( event ) {
		var appURL = $( this ).attr( "action" );
		var postData = $( this ).serializeArray();
		var csrftoken = getCookie('csrftoken');
		postData.push({name: 'csrfmiddlewaretoken', value: csrftoken});
		postData.push({name: 'mn_ip', value: '10.39.81.101'});
		$.ajax({
			url: appURL,
			type: "POST",
			data: postData,
			success: function(data) {
				if (data['status'] == 0) {
					console.log(data);
				}
			} // success function
		}) // $.ajax
		event.preventDefault();
	}); // $app_install_form
}); // document