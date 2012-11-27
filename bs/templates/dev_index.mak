<!DOCTYPE HTML>
<html lang="en">
<head>
    <%namespace name="d" file="bs.templates.definitions"/>
    ${d.css()}
    ${d.title()}
    ${d.js()}
</head>





<body>

    ${d.banner()}
    <p><div style="height:70px;" id="bs_operations"></div></p>
    <p><div id="bs_form_container"></div></p>
    ${d.footer()}

</body>

    <%!
    def se(text):
        return "'" + text + "'"
    %>




<script>
    window.onload = function(){
        var options = {
            'operation_list': ${oplist|n},
            'validation_url': ${validation_url|se,n},
            'bs_server_url': ${bs_serv_url|se,n},
            'bs_form_container_selector': '#bs_form_container',
            'get_url': ${gurl|se,n},
            'root_name' : 'Operations'
        }
        $('#bs_operations').bioscript(options).bioscript('operation_list');
    };
</script>

</html>


