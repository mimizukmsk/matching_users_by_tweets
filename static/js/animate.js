jQuery(function($) {
  $(function() {
    // nav-button
    $('#nav-button').on('click', function() {
      $(this).toggleClass('active');
      $('.header__menu').toggleClass('active');
    });

    // loading
    $('#btn-primary').on('click', function() {
      $('#loading').toggleClass('active');
    })
  });
});