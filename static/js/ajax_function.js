function defaulthandle(results){
    var results = results;
}
function jq_ajax(input_url, obj = {}, responsehandler = defaulthandle, method = 'POST'){
    $.ajax({
    type: method,
    url: input_url,
    data: JSON.stringify(obj),
    contentType: "application/json",
    dataType: 'json',
    success: function(result) {
        responsehandler(result);
    },
    error: function(error){
        console.log(error);
    }
});
}