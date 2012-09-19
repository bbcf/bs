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
    <meta content="text/html; charset=UTF-8" http-equiv="content-type"/>
    <title>BioScript</title>
    <link rel="stylesheet" type="text/css" media="screen" href="${tg.url('/css/style.css')}" />
    <link rel="stylesheet" type="text/css" media="screen" href="${tg.url('/css/admin.css')}" />
    <meta name="viewport" content="width=device-width">

##    <script type="text/javascript" src="${tg.url('/javascript/jslib/tw2.dynforms/dynforms.js')}"></script>
    <link rel="stylesheet" type="text/css" media="screen" href="${tg.url('/css/bs.css')}" />
    <script type="text/javascript" src="https://ajax.googleapis.com/ajax/libs/jquery/1.8.0/jquery.min.js"></script>
    <script type="text/javascript" src="${tg.url('/javascript/bs.js')}"></script>
    <script type="text/javascript" src="${tg.url('/javascript/jQuery.AjaxFileUpload.js/jquery.ajaxfileupload.js')}"></script>



</head>


<body>

<div>${bs|n}</div>

##<script src="${tg.url('/fupload/vendor/jquery.ui.widget.js')}"></script>
##
##<!-- The Iframe Transport is required for browsers without support for XHR file uploads -->
##<script src="${tg.url('/fupload/jquery.iframe-transport.js')}"></script>
##<!-- The basic File Upload plugin -->
##<script src="${tg.url('/fupload/jquery.fileupload.js')}"></script>
##
##<script type="text/javascript" src="${tg.url('/javascript/bs.js')}"></script>





</body>

    <%!
        def se(text):
            return "'" + text + "'"
    %>

<script>

    window.onload = function(){
        var options = {
            'bs_server_url' : ${bs_server_url|se,n}
        };

        $('body').bioscript(options).bioscript('hack_submit');
    }


</script>

</html>
