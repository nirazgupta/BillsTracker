
// // alert("Thanks for visiting!");
// // $(function(){
// //     $('[data-toggle="tooltip"]').tooltip();
// //     $(".side-nav .collapse").on("hide.bs.collapse", function() {                   
// //         $(this).prev().find(".fa").eq(1).removeClass("fa-angle-right").addClass("fa-angle-down");
// //     });
// //     $('.side-nav .collapse').on("show.bs.collapse", function() {                        
// //         $(this).prev().find(".fa").eq(1).removeClass("fa-angle-down").addClass("fa-angle-right");        
// //     });
// // });    
    
// setTimeout(function() {
//  $('.alert').fadeOut();
// }, 3000 );


$("document").ready(function(){
	$("#users_li").click(function(){
        $('#content').load('/admin/viewusers #show_users', function() {
        });
        
	}); 

    $("#trans_li").click(function(){
        $('#content').load('/trans_view #trans_tbl', function() {
            });
    });

    $("#usr_view_group_li").click(function(){
        $('#content').load('/view_group #group_view_tbl', function() {
            });
    });
});
alert('asdfasdf')



