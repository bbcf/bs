<%def name="title(title='BioScript')">
    <title>${title}</title>
</%def>

 <%def name="banner(sub='')">
     <ul id="banner">
       <li><a class="text" href="${tg.url('/')}">Bioscript</a></li>
       <li><a href="${tg.url('/direct/')}">Operations</a></li>
        <li><a href="${tg.url('/documentation')}">Documentation</a></li>
     </ul>
</%def>



<%def name="css()">
    <link rel="stylesheet" type="text/css" media="screen" href="${tg.url('/css/style.css')}" />
    <link rel="stylesheet" type="text/css" media="screen" href="${tg.url('/css/bs.css')}" />
</%def>

<%def name="js()">
    <script type="text/javascript" src="${tg.url('/javascript/jslib/jquery/1.8.0/jquery.js')}"></script>
    <script type="text/javascript" src="${tg.url('/javascript/bs.js')}"></script>
</%def>

<%def name="chart_js()">
    <script type="text/javascript" src="${tg.url('/javascript/jslib/d3/d3.js')}"></script>
    <script type="text/javascript" src="${tg.url('/javascript/jslib/bootstrap/bootstrap.js')}"></script>
    <script type="text/javascript" src="${tg.url('/javascript/chart.js')}"></script>
</%def>

<%def name="chart_css()">
    <link rel="stylesheet" type="text/css" media="screen" href="${tg.url('/css/chart.css')}" />
    <link rel="stylesheet" type="text/css" media="screen" href="${tg.url('/css/bootstrap.css')}" />
</%def>

<%def name="footer()">
    <div id="footer"><div class="foottext">
        BioScript is a <a href="http://bbcf.epfl.ch/">BBCF</a> application hosted on <a href="https:///github.com/bbcf/bs">github</a>. <a href="http://www.turbogears.org/">Powered by TurboGears</a>.
    </div></div>
</%def>


<%def name="enable_a_showhide()">
    <script>
        $('.a_hideshow').click(function(){
            $(this).nextAll('.span_hidden').toggle();
        });
    </script>
</%def>

<%def name="plugin_info(plugin)">
    <b><a href="${tg.url('/direct/get')}?id=${plugin['id']}">${plugin['info']['title']}</a> </b>
    <br/>by ${plugin['info']['meta']['author']} (<a href="mailto:${plugin['info']['meta']['contact']}?subject=[BioScript]">contact</a>)
    <br/> v. ${plugin['info']['meta']['version']}
    <a class="a_hideshow">description</a>
    <span class='plugin_description span_hidden'>${plugin['info']['desc_as_html'] | n}</span><br/>
    %if 'html_doc' in plugin['info']:
        <a href="${plugin['info']['html_doc']}">doc</a>
    %endif
    %if 'html_src_code' in plugin['info']:
        - <a href="${plugin['info']['html_src_code']}">code</a>
    %endif
</%def>


<%def name="display_childs(childs)">
    <ul>
    %for child in childs:
        <li> 
        %if 'id' in child:
             <div class="operation-childs">
                ${plugin_info(child)}
            </div>
        %else:
            <h3>${child['key']}</h3>
        %endif
        %if 'childs' in child:
            ${display_childs(child['childs'])}
        %endif
        </li>
    %endfor
    </ul>
</%def>
