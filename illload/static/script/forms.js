var AlertType;
(function (AlertType) {
    AlertType[AlertType["SUCCESS"] = 0] = "SUCCESS";
    AlertType[AlertType["INFO"] = 1] = "INFO";
    AlertType[AlertType["WARNING"] = 2] = "WARNING";
    AlertType[AlertType["DANGER"] = 3] = "DANGER";
})(AlertType || (AlertType = {}));
function alert_type_to_str(type) {
    switch (type) {
        case AlertType.SUCCESS:
            return "alert-success";
        case AlertType.INFO:
            return "alert-info";
        case AlertType.WARNING:
            return "alert-warning";
        case AlertType.DANGER:
            return "alert-danger";
    }
    return "";
}
class Alert {
    constructor(message, type) {
        this.message = message;
        this.alert_type = type;
    }
    to_list_element() {
        let elem = document.createElement("li");
        let alert_div = document.createElement("div");
        alert_div.classList.add("alert");
        alert_div.classList.add(alert_type_to_str(this.alert_type));
        alert_div.innerText = this.message;
        elem.appendChild(alert_div);
        return elem;
    }
}
function post(path, params) {
    var method = "post";
    var form = document.createElement("form");
    form.setAttribute("method", method);
    form.setAttribute("action", path);
    for (var key in params) {
        if (params.hasOwnProperty(key)) {
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
function delete_file(file, deletion_key) {
    var params = `deletion_key=${deletion_key}&file=${file}`;
    var url = `api/upload/delete`;
    var http = new XMLHttpRequest();
    http.open("POST", url, true);
    http.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    http.setRequestHeader("Content-length", "" + params.length);
    http.setRequestHeader("Connection", "close");
    http.send(params);
    location.reload(true);
}
function add_alert(alert) {
    document.getElementById("alerts").appendChild(alert.to_list_element());
}
function clear_alerts() {
    let node = document.getElementById("alerts");
    for (let child of Array.prototype.slice.call(node.children)) {
        if (child instanceof HTMLLIElement)
            node.removeChild(child);
    }
}
function validate_login_forms() {
    clear_alerts();
    let emailField = document.getElementById("emailField");
    let passField = document.getElementById("passwordField");
    if (emailField.value == "") {
        add_alert(new Alert("the email field is empty", AlertType.WARNING));
    }
    if (passField.value == "") {
        add_alert(new Alert("the password field is empty", AlertType.WARNING));
    }
    if (passField.value != "" && emailField.value != "") {
        document.getElementById("loginForm").submit();
    }
}
function gup(name, url) {
    if (!url)
        url = location.href;
    name = name.replace(/[\[]/, "\\\[").replace(/[\]]/, "\\\]");
    var regexS = "[\\?&]" + name + "=([^&#]*)";
    var regex = new RegExp(regexS);
    var results = regex.exec(url);
    return results == null ? "" : results[1];
}
function load_alerts() {
    let err = gup("e", location.href);
    if (err != "") {
        if (err == "l_e_email") {
            add_alert(new Alert("user not found", AlertType.WARNING));
        }
        else if (err == "l_e_password") {
            add_alert(new Alert("passwords do not match", AlertType.DANGER));
        }
        else if (err == "j_e_invite") {
            add_alert(new Alert("invalid invite token", AlertType.DANGER));
        }
    }
}
function validateEmail(email) {
    var re = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
    return re.test(email);
}
function validate_join_forms() {
    clear_alerts();
    let emailField = document.getElementById("emailField");
    let inviteField = document.getElementById("inviteField");
    let usernameField = document.getElementById("usernameField");
    let passField = document.getElementById("passwordField");
    if (emailField.value == "") {
        add_alert(new Alert("the email field is empty", AlertType.WARNING));
    }
    if (passField.value == "") {
        add_alert(new Alert("the password field is empty", AlertType.WARNING));
    }
    if (usernameField.value == "") {
        add_alert(new Alert("the username field is empty", AlertType.WARNING));
    }
    if (inviteField.value == "") {
        add_alert(new Alert("the invite field is empty", AlertType.WARNING));
    }
    if (!validateEmail(emailField.value)) {
        add_alert(new Alert("the email is in an invalid format", AlertType.DANGER));
        return;
    }
    if (inviteField.value != "" && usernameField.value != "" && passField.value != "" && emailField.value != "") {
        document.getElementById("joinForm").submit();
    }
}
