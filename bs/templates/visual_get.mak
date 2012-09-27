<!DOCTYPE HTML>
<!--
/*
 * jQuery File Upload Plugin Demo 6.9.1
 * https://github.com/blueimp/jQuery-File-Upload
 *
 * Copyright 2010, Sebastian Tschan
 * https://blueimp.net
 *
 * Licensed under the MIT license:
 * http://www.opensource.org/licenses/MIT
 */
-->
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
                window.location = ${bs_server_url|se,n} + 'requests?task_id=' + task_id;
            }
        };

        $('body').bioscript(options).bioscript('hack_submit');
    }


</script>

</html>
