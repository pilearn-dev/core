/*
 *  DELAYDIO 1.0
 * ==============
 * Delay video embed and show informational banner
 * for data privacy reasons (e.g. due to GDPR)
 *
 *  How to use
 * ------------
 * Use this code:
 *
 *    <div data-delaydio
 *      data-delaydio-platform="{PLATFORM}"
 *      data-delaydio-embedcode="{EMBEDCODE}"
 *      data-delaydio-lang="{BANNERLANG}" (optional)
 *    ></div>
 *
 * - {PLATFORM} is the video platform (e.g. youtube)
 * - {EMBEDCODE} is the Embedcode for the video
 *   (for https://youtu.be/2halApdn_UA -> 2halApdn_UA)
 * - {BANNERLANG} is the info banner language
 *
 *  Supported languages
 * ---------------------
 * - "de" German
 * - "en" English
 *
 *  Supported Platforms
 * ---------------------
 * - "youtube" Youtube
 * - "vimeo" Vimeo
 * */

/* Init: banner messages */
var BANNER_MESSAGES = {
  "de": "Dieses Video wird von der externen Plattform <strong>{:platform.name}</strong> geladen. Beim Laden des Videos von {:platform.name} werden (möglicherweise) Daten weitergegeben. Bitte konsultieren Sie die <a href='{:platform.privacy_link}'>Datenschutzerklärung von {:platform.name}</a> vor dem Fortfahren.",
  "en": "This video is loaded from the external platform <strong>{:platform.name}</strong>. During this process, some data may be transmitted to {:platform.name}. Please read their <a href='{:platform.privacy_link}'>privacy policy</a> before continuing."
}
var BANNER_BUTTONS = {
  "de": "Video laden",
  "en": "Load video"
}
var PLATFORM_DATA = {
  "youtube": {
    "name": "Youtube",
    "privacy_link": "https://policies.google.com/privacy"
  },
  "vimeo": {
    "name": "Vimeo",
    "privacy_link": "https://vimeo.com/privacy"
  }
}

/* Init: variables */
var DelaydioVideoContainers = [];
var DelayVideoLoadLinks = [];

/* Step 1: fetch all video containers */
let tmpVCList = document.querySelectorAll("[data-delaydio]");
for (var i = 0; i < tmpVCList.length; i++) {
  if(!tmpVCList[i].hasAttribute("data-delaydio-platform")) {
    console.error("Delaydio element misses required attribute data-delaydio-platform");
  } else if(!tmpVCList[i].hasAttribute("data-delaydio-embedcode")) {
    console.error("Delaydio element misses required attribute data-delaydio-embedcode");
  } else {
    DelaydioVideoContainers.push(tmpVCList[i]);
  }
}

/* Step 2: apply banner to them */
for (var i = 0; i < DelaydioVideoContainers.length; i++) {
  let element = DelaydioVideoContainers[i];

  let platform = PLATFORM_DATA[element.getAttribute("data-delaydio-platform")];
  let embed_code = element.getAttribute("data-delaydio-embedcode");
  let lang = element.getAttribute("data-delaydio-lang") || "en";

  element.innerHTML = "";

  element.style.backgroundColor = "#ffa";
  element.style.color = "#222";
  element.style.padding = "10px";
  element.style.font = "16px Courier";
  element.style.display = "block";
  element.style.boxSizing = "border-box";
  element.style.margin = "1px";

  let message = BANNER_MESSAGES[lang];
  message = message.replace(/\{\:platform.name\}/g, platform.name);
  message = message.replace(/\{\:platform.privacy_link\}/g, platform.privacy_link);

  let banner = document.createElement("p");
  banner.innerHTML = message;
  banner.style.boxSizing = "border-box";
  banner.style.margin = "2px";
  banner.style.display = "block";
  links = banner.getElementsByTagName("a");
  for (var j = 0; j < links.length; j++) {
    links[j].style.color="#888";
    links[j].style.font="inherit";
    links[j].style.textDecoration="none";
    links[j].style.borderBottom="1px dotted";
    links[j].setAttribute("target", "_blank")
  }
  element.appendChild(banner);

  let button = document.createElement("a");
  button.style.color="#444";
  button.style.backgroundColor="#dd8";
  button.style.font="inherit";
  button.style.textDecoration="none";
  button.style.display = "inline-block";
  button.style.margin = "2px";
  button.style.padding = "5px 10px";
  button.style.cursor = "pointer";
  button.innerText = BANNER_BUTTONS[lang];
  DelayVideoLoadLinks.push(button);
  element.appendChild(button);
}


/* Step 3: add event handlers */
for (var i = 0; i < DelayVideoLoadLinks.length; i++) {
  let btn = DelayVideoLoadLinks[i];
  btn.addEventListener("click", function () {
    element = this.parentNode;
    element.innerHTML = "";
    element.style.backgroundColor = "transparent";
    element.style.color = "#000";
    element.style.padding = "2px";
    element.style.font = "inherit";
    element.style.display = "block";
    element.style.boxSizing = "border-box";

    let platform = element.getAttribute("data-delaydio-platform");
    let embed_code = element.getAttribute("data-delaydio-embedcode");

    if (platform == "youtube") {
      element.innerHTML = '<iframe type="text/html" src="https://www.youtube-nocookie.com/embed/'+embed_code+'?rel=0&showinfo=0&autoplay=1" frameborder="0" allowfullscreen allow="autoplay; encrypted-media" style="width: 720px; height: 480px; max-width: 100%; max-height: 66vw;">';
    } else if (platform == "vimeo") {
      element.innerHTML = '<iframe src="https://player.vimeo.com/video/'+embed_code+'?autoplay=1" frameborder="0" webkitallowfullscreen mozallowfullscreen allowfullscreen></iframe>'
    }
  })
}
