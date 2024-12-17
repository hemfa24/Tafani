var body = $('body');
    var contentWrapper = $('.content-wrapper');
    var scroller = $('.container-scroller');
    var footer = $('.footer');
    var sidebar = $('.sidebar');
function applyStyles() {
      //Applying perfect scrollbar
      if (!body.hasClass("rtl")) {
        if ($('.settings-panel .tab-content .tab-pane.scroll-wrapper').length) {
          const settingsPanelScroll = new PerfectScrollbar('.settings-panel .tab-content .tab-pane.scroll-wrapper');
        }
        if ($('.chats').length) {
          const chatsScroll = new PerfectScrollbar('.chats');
        }
        if (body.hasClass("sidebar-fixed")) {
          if($('#sidebar').length) {
            var fixedSidebarScroll = new PerfectScrollbar('#sidebar .nav');
          }
        }
      }
    }

$('[data-toggle="minimize"]').on("click", function() {
//body.toggleClass('sidebar-hidden');
body.toggleClass("");
//      if ((body.hasClass('sidebar-toggle-display')) || (body.hasClass('sidebar-absolute'))) {
//
//      } else {
//        body.toggleClass('sidebar-icon-only');
//      }
    });

     $(".profileDropdown").on("click", function () {
      var $dropdownMenu = $(".profile_dropdown");
      var $navProfile = $(".nav-item.nav-profile.dropdown");
      $dropdownMenu.addClass("show");
      $navProfile.toggleClass("show");
    });