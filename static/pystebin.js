window.onload = function() {
    var c = null,
        a = document.getElementById("paste")
  
    a.addEventListener("keyup", function() {
        clearTimeout(c)
        c = setTimeout(function() {
            document.getElementById("status").innerText = "Saving..."
          
            var d = new FormData();
            d.append("paste", a.value)
          
            fetch("/paste", { method: "POST", body: d })
                .then(function(b) { return b.json() })
                .then(function(b) { return history.pushState({}, null, "/" + b.id) })
          
            document.getElementById("status").innerText = "Saved " + (new Blob([a.value])).size + " bytes"
        }, 100)
    })
}
