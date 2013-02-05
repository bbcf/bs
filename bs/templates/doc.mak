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
        The documentation is minimal. So if you need some help, please use <a href="mailto:webmaster-bbcf@epfl.ch?Subject=[BS] A question about Bioscript"> this email </a>. Your question will be used to raise a FAQ.
        </p>

        <p> 
        All plugin are hosted on github at <a href="https://github.com/bbcf/bs.operations">bbcf/bs.operations</a>.
        </p>
        
        <p>
        If you want to develop a plugin yourself, you should look at <a href="https://github.com/bbcf/bs.operations/blob/master/Examples.py">this plugin</a> and <a href="https://github.com/bbcf/bs.operations/blob/master/Examples_with_form.py">that one</a>.
        </p>

        <p> 
        If you want to embed BioScript in your application, all you need is 3 HTTP routes, 1 javascript file & 1 CSS file.
        There is a simulated example of such an application <a href="${tg.url('/devs/')}">this way</a>. You can browse the code of this 
        controller <a href="https://github.com/bbcf/bs/blob/master/bs/controllers/dev.py">on github</a>.
        </p>
      
        <p>
        Embedded, you can prefill some field with the files provided by you application.
        You have example <a href="${tg.url('/direct/index/prefill')}">here</a>.
        </p>

    </div>

    ${d.footer()}
</body>


</html>
