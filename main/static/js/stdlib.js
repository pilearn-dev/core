function $post(url, param, cb) {
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            if(cb) {
                cb(this.responseText);
            }
        } else if (this.readyState == 4) {
            if(cb) {
                cb(this.responseText);
            }
        }
    };
    xhttp.open("POST", "/"+url, true);
    xhttp.setRequestHeader("Content-Type", "application/json");
    xhttp.send(JSON.stringify(param));
}
hasMovingDialog = null;
dialogX = dialogY = 0;
window.addEventListener("mousedown", function(e) {
    if(e.target.classList.contains("close-link") && e.target.parentNode.classList.contains("flagging-dialog")) {
      hasMovingDialog = e.target.parentNode;
      dialogX = e.clientX - hasMovingDialog.getBoundingClientRect().left + (hasMovingDialog.getBoundingClientRect().width / 2.0) - window.scrollX;
      dialogY = e.clientY - hasMovingDialog.getBoundingClientRect().top - window.scrollY;
    } else {
      hasMovingDialog = null;
    }
})
window.addEventListener("mouseup", function(e) {
    hasMovingDialog = null;
})
window.addEventListener("mousemove", function(e) {
    if(hasMovingDialog) {
      hasMovingDialog.style.left = (e.clientX - dialogX) + "px";
      hasMovingDialog.style.top = (e.clientY - dialogY) + "px";
    }
})
function _________u() {
  if(this.value) {
    this.setAttribute("value", this.value);
  } else {
    this.removeAttribute("value")
  }
}
_x = document.querySelectorAll(".coursenav input");
for (var i = 0; i < _x.length; i++) {
  _x[i].addEventListener("keyup", _________u)
  _x[i].addEventListener("change", _________u)
  _x[i].addEventListener("input", _________u)
}
