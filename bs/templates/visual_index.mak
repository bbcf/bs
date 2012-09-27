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

    <div id="bs_operations"></div>

    ${d.footer()}

</body>

    <%!
    def se(text):
        return "'" + text + "'"
    %>




<script>
    window.onload = function(){

        var options = {
            operation_list : ${oplist|n},
            show_plugin : function(plugin_id){
                window.location = ${serv|se,n} + 'visual/' + ${method|se,n}+ '?id=' + plugin_id;
            },
            'root_name' : 'Operations'
        }
        $('#bs_operations').bioscript(options).bioscript('operation_list');
    };
</script>

</html>
