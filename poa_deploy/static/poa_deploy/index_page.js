$(function() {
	$interceptForm($( "form#app_add_form" ), $( "div#app_add_output" ));
	$interceptForm($( "form#app_install_form" ), $( "div#app_install_output" ), {name: 'mn_ip', value: '10.39.81.101'});
}); // $(function()