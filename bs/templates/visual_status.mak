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

     <p>
        BioScripts is a python library providing bioinformatics scripts through a simple and consistent interface. It can be used on the command line or via a web service. Each script consists of a <b>plugin</b> running the algorithm and an <b>html form</b> managing its inputs.
        <br/>
        <br/>
        Simple & straightforward, with the complexity hidden for end-users, it allows quick installation and access
        to multiple tools. End-users may ignore where and how the operations are launched: on a dedicated machine with
        adapted CPU & RAM.
    </p>


    <p>There is currently <span class="jstatus jrunning">${running} running</span> and <span class="jstatus jpending">${pending} pending </span>jobs on Bioscript out of <span class="jstatus jtotal">${total} total.</span>
    </p>

    <div id="plugin_presentation">
        There is <span class="jstatus jrunning">${nbplugins}</span> plugins available: <br/>
        <ul>
        % for plugin in plugins:
            <li> 
            <a href="${tg.url('/direct/get')}?id=${plugin['id']}">${plugin['info']['title']}</a> 
            <br/>by ${plugin['info']['meta']['author']} (<a href="mailto:${plugin['info']['meta']['contact']}?subject=[BioScript]">contact</a>)
            <br/> version ${plugin['info']['meta']['version']}
            <a class="a_hideshow">description</a>
            <span class='plugin_description span_hidden'>${plugin['info']['description'] | n}</span>

            </li>
        % endfor
        </ul>
    </div>

    </div>
    ${d.footer()}

</body>

    ${d.enable_a_showhide()}

</html>
