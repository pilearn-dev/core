var Poller = function (route, freq, std_action, std_data) {
    this.route = route;
    this.freq = freq;
    this.lost_data = [];
    this.std_action = std_action || "keep-alive";
    this.std_data = std_data || null;
    this.events = {};
    this.loop = null;
    this.xhttp = new XMLHttpRequest();
    this.xhttp.onload = this.xhttp.onerror = this._fetch.bind(this)
    if(this.freq > 0) {
      this.fetch = undefined;
    }
}
Poller.prototype.connect = function () {
    if (this.loop == null && this.freq > 0) {
        this.loop = window.setInterval(this._poll.bind(this), 1000 / this.freq);
    }
}
Poller.prototype.disconnect = function () {
    if (this.loop != null) {
        window.clearInterval(this.loop);
        this.loop = null;
    }
}
Poller.prototype.on = function (ev, cb) {
    this.events[ev] = cb;
}
Poller.prototype.send = function (action, data) {
    this.lost_data.push([action, data]);
}
Poller.prototype.fetch = function (action, data) {
  this.lost_data.unshift([action, data]);
  this._poll();
}
Poller.prototype._poll = function () {
    if (this.lost_data.length != 0) {
        act_data = this.lost_data.shift();
        obj = {
            "action": act_data[0],
            "data": act_data[1]
        }
    } else {
        obj = {
            "action": this.std_action,
            "data": this.std_data
        }
    }
    this.xhttp.open("POST", this.route + "?poll=" + String(Math.round(100000 * Math.random())), true);
    this.xhttp.send(JSON.stringify(obj));
}
Poller.prototype._fetch = function() {
    if (this.xhttp.readyState == 4 && this.xhttp.status == 200) {
        result = JSON.parse(this.xhttp.responseText);
        ev = result["event"];
        this.events[ev](result["data"]);
    } else if (this.xhttp.readyState == 4) {
        this.events["@error"](null);
    }
}
