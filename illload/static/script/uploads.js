// im so damn lazy, i couldent be bothered to load up typescript typings lol
function delete_all_files(email, key) {
  $.ajax({
    type: "POST",
    url: "/api/upload/delete_all",
    data: `key=${key}&email=${email}`,
    success: function(data, status, jqXHR) {
      location.reload();
    }
  });
}
