function test() {
  var menu = document.getElementsByClassName('menu');
  document.getElementById("demo").innerHTML = menu.length;
}

function click() {
 document.addEventListener("click", test()
}

 window.addEventListener("load", click)