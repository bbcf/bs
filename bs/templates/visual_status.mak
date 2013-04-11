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
    <div id="content">


    <p>There is currently <span class="jstatus jrunning">${running} running</span> and <span class="jstatus jpending">${pending} pending </span>jobs on Bioscript out of <span class="jstatus jtotal">${total} total.</span>
    </p>

    <div id="plugin_presentation">
        <span class="jstatus jrunning">${nbplugins}</span> plugins are available: <br/>
  <!--
        <ul>
        % for plugin in plugins:
            <li> 
            <b><a href="${tg.url('/direct/get')}?id=${plugin['id']}">${plugin['info']['title']}</a> </b>
            <br/>by ${plugin['info']['meta']['author']} (<a href="mailto:${plugin['info']['meta']['contact']}?subject=[BioScript]">contact</a>)
            <br/> version ${plugin['info']['meta']['version']}
            <a class="a_hideshow">description</a>
            <span class='plugin_description span_hidden'>${plugin['info']['description'] | n}</span>

            </li>
        % endfor
        </ul>
    -->
    
    </div>

    <br/>
     <div id="plugin_presentation2">
        ${d.display_childs(ordered['childs'])}
      <div>


    </div>
    ${d.footer()}

</body>

    ${d.enable_a_showhide()}

</html>
