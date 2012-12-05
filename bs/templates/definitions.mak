<%def name="title(title='BioScript')">
    <title>${title}</title>
</%def>

 <%def name="banner(sub='')">
     <ul id="banner">
       <li><a class="text" href="${tg.url('/')}">Bioscript</a></li>
       <li><a href="${tg.url('/direct/')}">Operations</a></li>
       <li><a href="http://bbcf.epfl.ch/bs">Documentation</a></li>
        <li><a href="${tg.url('/developers')}">Developers</a></li>
     </ul>
</%def>



<%def name="css()">
    <link rel="stylesheet" type="text/css" media="screen" href="${tg.url('/css/style.css')}" />
    <link rel="stylesheet" type="text/css" media="screen" href="${tg.url('/css/bs.css')}" />
</%def>

<%def name="js()">
    <script type="text/javascript" src="https://ajax.googleapis.com/ajax/libs/jquery/1.8.0/jquery.min.js"></script>
    <script type="text/javascript" src="${tg.url('/javascript/bs.js')}"></script>
</%def>


<%def name="footer()">
    <div id="footer"><div class="foottext">
        <p>BioScript is a <a href="http://bbcf.epfl.ch/">BBCF</a> application hosted on <a href="https:///github.com/bbcf/bs">github</a>.</p>
        <p><a href="http://www.turbogears.org/2.1/">Powered by TurboGears 2</a></p>
    </div></div>
</%def>