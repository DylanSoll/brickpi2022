function return_results(results){
    return results
}
function jq_ajax(input_url, obj = {}, responsehandler = return_results, method = 'POST'){
    $.ajax({
    type: method,
    url: input_url,
    data: JSON.stringify(obj),
    contentType: "application/json",
    dataType: 'json',
    success: function(result) {
        responsehandler(result);
        console.log(data)
    },
    error: function(error){
        console.log(error);
    }
});
}