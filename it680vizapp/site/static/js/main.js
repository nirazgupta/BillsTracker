// function loopForm(form)
// {
//   if (document.getElementById('checkbox').checked == false) 
//   {
//       //alert('Select at least one member');
//       document.getElementById('checkalert').innerHTML="Select at least one member";
//       return false;
//   }
// }

// function transaction_detail(){
//     output="<tr><td>" + 'first td' + "</td><td>" + 'secondtd' + "</td></tr>";
//     $("#add_td tbody").append(output);
    
// }

function show_hide_row(row)
{
 $("#"+row).toggle(  );
}


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

    $("#usr_view_group_li").click(function(){
        history.pushState({}, "", "/show_group");
        $('#content').load('/show_group #data-table', function() {
        });
    });

    $("#usr_join_group_li").click(function(){
        history.pushState({}, "", "/joingroup");
        $('#content').load('/joingroup #tbl_groups1');
       
    });

    $("#usr_create_group_li").click(function(){
        history.pushState({}, "", "/create_group");
        $('#content').load('/create_group #create_group');
       
    });
});




$(document).ready(function() {  
    $('#show_btn').click(function() { 
        var displayResources = $('#container');
        $.ajax({
        url: "/_show_group", //{{ url_for ('site.getdata') }}",
        type: 'GET',
        dataType: 'json',
        success: function (result) {
            // $('#container').html(data);
            
            var output="<table><thead><tr><th>Group Name</th><th>Member</th></thead><tbody>";
            for (var i in result)
            {
            output+="<tr><td>" + result[i].group_name + "</td><td>" + result[i].name + "</td></tr>";
            }
            output+="</tbody></table>";

            displayResources.html(output);
            console.log(output)
            $("table").addClass("table");
        }
        });
});
});



// Ajax call for loading the groups in vnavbar
$(document).ready(function() {  
        var displayResources = $('#mypanel');
        $.ajax({
        url: "/show_group", //{{ url_for ('site.getdata') }}",
        type: 'GET',
        dataType: 'json',
        success: function (result) {
            // $('#container').html(data);
            
            var output="<table><thead></thead><tbody>";
            for (var i in result)
            {
            
            output+="<tr><td id='result[i].group_id'>" + '<a href="'+'/transactions/'+result[i].group_id+'">' + result[i].group_name  +'</a>' + "</td></tr>";
            }
            output+="</tbody></table>";
            displayResources.html(output);
            $("table").addClass("table");
            // $("td").addClass("group_id");
            
        }
        });
});

// $(document).ready(function() {  
//     var displayResources = $('#mypanel');
//     $.ajax({
//     url: "/show_group", //{{ url_for ('site.getdata') }}",
//     type: 'GET',
//     dataType: 'json',
//     success: function (result) {
//         // $('#container').html(data);
//         console.log(result)
//         var output="<table><thead></thead><tbody>";
//         for (var i in result)
//         {
        
//         output+="<tr><td id='result[i].group_id'>" + '<a href="'+'/transactions/'+result[i].group_id+'">' + result[i].group_name  +'</a>' + "</td></tr>";
//         }
//         output+="</tbody></table>";
//         displayResources.html(output);
//         $("table").addClass("table");
//         // $("td").addClass("group_id");
        
//     }
//     });
// });




// $(document).ready(function() {  
//     $('#show_btn').click(function() { 
//         $.ajax("/_show_group").done(function (reply) {
//             $('#container').html(reply);
//             console.log(reply);
        
//     });
// });
// });




// $(document).ready(function() {   
//     $('#data-table').DataTable({
//         "ajax":"/show_group",
//         "columns" : [
//             {"data" : "group_id"},
//             {"data" : "group_name"},
//             {"data" : "user_id"}
//         ]
//     });
// });


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


var app = angular.module('MyApp', []);


app.config(function($interpolateProvider, $httpProvider){         
   $interpolateProvider.startSymbol('[[').endSymbol(']]');
   })
   app.filter('capitalize', function() {
         return function(input) {
           return (!!input) ? input.charAt(0).toUpperCase() + input.substr(1).toLowerCase() : '';
         }
     });
     app.controller('MyController', function($scope, $http) {
          //changed to your local api
     $('.transaction_display').click(function() { 
     trans_value =  $(this).data('value');
          var url = "/owings/"+trans_value;
          $http.get(url).success(function(data) {
             $scope.Content = data;
          });
          });

});