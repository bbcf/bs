<!DOCTYPE HTML>
<html lang="en">
<head>
    <meta content="text/html; charset=UTF-8" http-equiv="content-type"/>
    <title>BioScript</title>
    <meta name="viewport" content="width=device-width"/>

    <link rel="stylesheet" type="text/css" media="screen" href="${tg.url('/css/bs.css')}" />
    <link rel="stylesheet" type="text/css" media="screen" href="${tg.url('/css/style.css')}" />
    <script type="text/javascript" src="//code.jquery.com/jquery-1.8.1.min.js" ></script>
    <script type="text/javascript" src="${tg.url('/javascript/bs.js')}"></script>
</head>





<body>
    <div id="header">
        <h1>
        BioScript
        <span class="subtitle">Operations list</span>
    </h1>
</div>

    <ul id="mainmenu">
        <li><a href="${tg.url('/visual/')}" >Operations</a></li>
        <li><a href="${tg.url('/vocabulary')}" >Vocabulary</a></li>
        <li><a href="http://bbcf.epfl.ch/bs">Documentation</a></li>
    </ul>


    <div id="bs_operations"/>
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
                window.location = ${serv|se,n} + 'visual/get?id=' + plugin_id;
            }
        }



        $('#bs_operations').bioscript(options).bioscript('operation_list');
    };
</script>

</html>
