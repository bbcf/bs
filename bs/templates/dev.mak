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
        <p> Developpers documentation can be found on <a href="http://bbcf.epfl.ch/bs/">BBCF website</a>. If you want to develop a plugin, it's the right place to look at.
        </p>
        
        <p> 
        If you want to embed BioScript in your application, all you need is 3 HTTP routes, 1 javascript file & 1 CSS file. 
        There is a simulated example of such an application <a href="${tg.url('/devs/')}">here</a>. You can browse the code on
        <a href="https://github.com/bbcf/bs/blob/master/bs/controllers/dev.py">github</a>.
        </p>
      
        <p>
        User can access to BioScript directly, but BioScript can also be embedded in an application.
        File upload fields can be pre-filled with the application files.<br/>
        You have example <a href="${tg.url('/direct/index/prefill')}">here</a>.
        (beta-test)
        </p>

    </div>

    ${d.footer()}
</body>


</html>
