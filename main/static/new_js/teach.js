let teach_group_data = $("#team-data");
const teach_group_id = teach_group_data.attr("data-id");
const teach_group_token = teach_group_data.attr("data-token");

function Teach_MemberAction($this, member_id, action) {
  $.ajax({
    url: "/teach/" + teach_group_token + "/members/actions",
    method: "POST",
    contentType: "application/json; charset=utf-8",
    data: JSON.stringify({
      action,
      member_id
    }),
    success: function( r ) {
      $this.removeClass("-loading -active");
      if(r.result == "success") {
        if(action == "remove") {
          $this.parent().parent().parent().remove();
        } else if(action == "activate") {
          par = $this.parent()
          par.find(".js--remove-btn").attr("disabled", true);
          par = par.parent().removeClass("-active").parent();
          par.find(".js--active").text("ja")
          par.removeClass("-inactive")
        } else if(action == "deactivate") {
          par = $this.parent()
          par.find(".js--remove-btn").removeAttr("disabled");
          par = par.parent().addClass("-active").parent();
          par.find(".js--active").text("nein")
          par.addClass("-inactive")
        } else if(action == "grantadmin") {
          par = $this.parent().parent().parent();
          par.find(".js--admin").text("ja")
        } else if(action == "revokeadmin") {
          par = $this.parent().parent().parent();
          par.find(".js--admin").text("nein")
        }
      } else {
        PiJS.warnbox.error(r.message, $this.parent());
      }
    }
  });
}


PiJS.route(/^\/teach\/[a-zA-Z0-9]{8}\/members/, function() {
  $(".js--remove-btn").click(function() {
    $this = $(this);
    let member_id = $this.attr("data-member-id");
    $this.addClass("-loading -active");
    Teach_MemberAction($this, member_id, "remove")
  })
  $(".js--role-change-btn").click(function() {
    $this = $(this);
    let member_id = $this.attr("data-member-id");
    role_element = $("<div>").append(
      $("<p>Neue Rolle:</p>")
    );
    if($this.parent().parent().hasClass("-active")) {
      role_element.append(
        $("<button class='_btn _btn--primary _btn-on-dark _btn-lighter'>Aktiv</button>")
          .click(function() {
            $(this).parent().parent().parent().remove();
            $this.addClass("-loading -active");
            Teach_MemberAction($this, member_id, "activate")
          })
      );
    } else {
      role_element.append(
        $("<button class='_btn _btn--primary _btn-on-dark _btn-lighter'>Inaktiv</button>")
          .click(function() {
            $(this).parent().parent().parent().remove();
            $this.addClass("-loading -active");
            Teach_MemberAction($this, member_id, "deactivate");
          })
      )
      if($this.parent().parent().parent().find(".js--admin").text() == "nein") {
        role_element.append(
          $("<button class='_btn _btn--primary _btn-on-dark _btn-lighter'>Admin</button>")
            .click(function() {
              $(this).parent().parent().parent().remove();
              $this.addClass("-loading -active");
              Teach_MemberAction($this, member_id, "grantadmin");
            })
        );
      } else {
        role_element.append(
          $("<button class='_btn _btn--primary _btn-on-dark _btn-lighter'>Deadmin</button>")
            .click(function() {
              $(this).parent().parent().parent().remove();
              $this.addClass("-loading -active");
              Teach_MemberAction($this, member_id, "revokeadmin");
            })
        );
      }
    }
    PiJS.warnbox._generate("-primary", role_element, $this.parent(), true);
  })
});

PiJS.route(/^\/teach\/[a-zA-Z0-9]{8}\/members\/invitations/, function() {
  $(".js--delete-btn").click(function() {
    $this = $(this);
    $this.addClass("-loading -active");
    $.ajax({
      url: "/teach/" + teach_group_token + "/members/invitations",
      method: "POST",
      contentType: "application/json; charset=utf-8",
      data: JSON.stringify({
        action: "remove",
        invitation_id: $this.attr("data-id")
      }),
      success: function( r ) {
        $this.removeClass("-loading -active");
        if(r.result == "success") {
          $this.parent().parent().remove();
        } else {
          PiJS.warnbox.error(r.message, $this.parent());
        }
      }
    });
  });
})
