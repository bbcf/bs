<!DOCTYPE HTML>
<html lang="en">

<head>
    <%namespace name="d" file="bs.templates.definitions"/>
    ${d.css()}
    ${d.title()}
    ${d.css()}
    ${d.js()}
</head>

<body>

    ${d.banner()}
    <div>${bs|n}</div>
    ${d.footer()}

</body>

    <%!
        def se(text):
            return "'" + text + "'"
    %>

<script>

    window.onload = function(){
        var options = {
            'bs_server_url' : ${bs_server_url|se,n},
            'validation_successful' : function(plugin_id, task_id){
                window.location = ${bs_server_url|se,n} + 'jobs?task_id=' + task_id;
            }
        };

        $('body').bioscript(options).bioscript('hack_submit');
    }


</script>

</html>
