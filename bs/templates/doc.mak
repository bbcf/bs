<!DOCTYPE HTML>
<html lang="en">
<head>
    <%namespace name="d" file="bs.templates.definitions"/>
    ${d.css()}
    ${d.title()}
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
    
        <p>
        Each plugin should be documented. So if you need more documentation about one, please contact the author directly.
        <br/><br/>
        Plugins developed by the BBCF are documented on <a href="http://bbcf.epfl.ch/bsplugins/content/bsPlugins.html">this page</a>.
       
        </p>


        <p> 
        For developpers, plugins are hosted by <b>github</b> at <a href="https://github.com/bbcf/bsPlugins">bbcf/bsPlugins</a> so that you can see the algorithms and <b>use/fork</b> them.
        <br/>
        If you want to build your own plugin, take a look at the <a href="http://bbcf.epfl.ch/bsplugins/index.html">developpers documentation</a>.
        </p>
         

        <p>
        Bioscript can be embedded in a third-party application, as in <a href="http://htsstation.epfl.ch/"> HTSstation</a> and <a href="http://gdv.epfl.ch">GDV</a>.
        <br/>
        <br/>
        If you have questions :  use <a href="mailto:webmaster-bbcf@epfl.ch?Subject=[BS] A question about Bioscript"> this email</a>.

        </p>
      
    </div>

    ${d.footer()}
</body>


</html>
