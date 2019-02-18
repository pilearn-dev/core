function draw_reorder(reorder, data) {
  reorder.innerHTML = "";

  for(var i=0; i<data.length; i++) {
    container = document.createElement("div");
    container.classList.add("reorder-item");

    arrays = document.createElement("div");
    arrays.classList.add("arrays");

    up = document.createElement("a");
    up.innerText = "▲";
    up.setAttribute("href", "#!");
    up.elid = i;
    up.addEventListener("click", function() {

    });
    arrays.appendChild(up);

    down = document.createElement("a");
    down.innerText = "▼";
    down.setAttribute("href", "#!");
    down.elid = i;
    down.addEventListener("click", function() {

    });
    arrays.appendChild(down);

    container.appendChild(arrays);

    arrays = document.createElement("div");
    arrays.classList.add("arrays");

    indent = document.createElement("a");
    indent.innerText = "▶";
    indent.setAttribute("href", "#!");
    indent.elid = i;
    indent.addEventListener("click", function() {

    });
    arrays.appendChild(indent);

    container.appendChild(arrays);

    title = document.createElement("span");
    title.innerText = data[i].title;
    container.appendChild(title);

    reorder.appendChild(container);
  }
}

window.addEventListener("load", function() {
  reorder = document.getElementById("reorder");
  data = REORDER_DATA;
  draw_reorder(reorder, data);
});
