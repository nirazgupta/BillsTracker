// function loopForm(form)
// {
//   if (document.getElementById('checkbox').checked == false) 
//   {
//       //alert('Select at least one member');
//       document.getElementById('checkalert').innerHTML="Select at least one member";
//       return false;
//   }
// }

function validate(){
	var user = document.loginform.username.value;
	var pass = document.loginform.password.value;
	if(user == ""){
		document.getElementById('useralert').innerHTML="Please enter the username";
		document.getElementById('form_css1').style.borderColor = "red";
		return false;
	}
	else if(pass == ""){
		document.getElementById('passalert').innerHTML="Please enter the password";
		document.getElementById('form_css2').style.borderColor = "red";
		return false;
	}

}

setTimeout(function() {
 $('.alert').fadeOut();
}, 3000 );

$("document").ready(function(){

    $("#usr_trans_li").click(function(){
        $('#content').load('/trans_view #trans_tbl', function() {
            });
    });

    $("#usr_dash_li").click(function(){
        $('#content').load('/dashboard #msg', function() {
            });
    });
});



function validateForm() {
	var check = document.forms["transaction_form"]["status"].value;
    if (check == "") {
        alert("Please choose a status");
        return false;
	} 
}




// function loopForm(form) {
//     var cbResults = 'Checkboxes: ';
//     for (var i = 0; i < form.elements.length; i++ ) {
//         if (form.elements[i].type == 'checkbox') {
//             if (form.elements[i].checked == true) {
//                 cbResults += form.elements[i].value + ' ';
//             }
//         }

// 	}
// 	document.getElementById("cbResults").innerHTML = cbResults;
// 	alert(cbResults);
// }