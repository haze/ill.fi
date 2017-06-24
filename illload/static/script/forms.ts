function post(path, params) {
    var method = "post";
    var form = document.createElement("form");
    form.setAttribute("method", method);
    form.setAttribute("action", path);
    for(var key in params) {
        if(params.hasOwnProperty(key)) {
            var hiddenField = document.createElement("input");
            hiddenField.setAttribute("type", "hidden");
            hiddenField.setAttribute("name", key);
            hiddenField.setAttribute("value", params[key]);
            form.appendChild(hiddenField);
         }
    }
    document.body.appendChild(form);
    form.submit();
}

function delete_file(file: string, deletion_key: string) {
  var params = `deletion_key=${deletion_key}&file=${file}`;
  var url = `api/upload/delete`
  var http = new XMLHttpRequest();
  http.open("POST", url, true);

  //Send the proper header information along with the request
  http.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
  http.setRequestHeader("Content-length", ""+params.length);
  http.setRequestHeader("Connection", "close");
  http.send(params);
  location.reload(true);
}
