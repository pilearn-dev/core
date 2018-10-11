var x = null;
var y = null;

document.addEventListener('mousemove', onMouseUpdate, false);
document.addEventListener('mouseenter', onMouseUpdate, false);
document.addEventListener('mousedown', onMouseUpdate, false);

function onMouseUpdate(e) {
  x = e.pageX;
  y = e.pageY;
}

function getMouseX() {
  return x;
}

function getMouseY() {
  return y;
}

function issueSystemDialog(msg, class_) {
  el = document.createElement("div");
  el.classList.add("system-dialog");
  el.classList.add(class_);
  content = document.createElement("div");
  content.classList.add("content-box");
  content.innerHTML = msg;
  el.appendChild(content);

  closure = document.createElement("a");
  closure.classList.add("quit-box")
  closure.innerHTML = "&times";
  closure.el = el
  closure.onclick = function () {
    this.el.parentNode.removeChild(this.el);
  }
  el.appendChild(closure);

  el.style.top = String(getMouseY())+"px";
  el.style.left = String(getMouseX())+"px";
  document.body.appendChild(el);
}

function issueSystemWarning(msg) {
  issueSystemDialog(msg, "system-warning")
}
function issueSystemError(msg) {
  issueSystemDialog(msg, "system-error")
}
function issueSystemInfo(msg) {
  issueSystemDialog(msg, "system-info")
}
function issueSystemQuestion(quest, answers) {
  html = quest + "<div class='answer-list'>";
  for (var i = 0; i < answers.length; i++) {
    if(answers[i][1] == "dismiss") {
      answers[i][1] = '#!\' onclick=\'document.querySelector(".system-dialog.system-question").outerHTML=""; return false;';
    }
    html += "<a href='" + answers[i][1] + "'>" + answers[i][0] + "</a>";
  }
  html += "</div>";
  issueSystemDialog(html, "system-question")
}
