let jsonError = "<p>Unable to load json file. Is it an http or https link directly to the .json?</p>";
let contributeForm = "<p>JSON file loaded. If you see nothing, then there was probably no location data in the file.</p>";

// ------- Modal js ---------
var modal = document.getElementById("loginModal");
// Get the button that opens the modal
var btn = document.getElementById("loginModal-button");

// Get the <span> element that closes the modal
var span = document.getElementsByClassName("close")[0];

// When the user clicks on the button, open the modal
btn.onclick = function() {
  modal.style.display = "block";
}

// When the user clicks on <span> (x), close the modal
span.onclick = function() {
  modal.style.display = "none";
}