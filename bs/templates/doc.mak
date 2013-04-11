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
        All plugins are hosted by github at <a href="https://github.com/bbcf/bsPlugins">bbcf/bsPlugins</a>.
        </p>
        
        <p>
        If you want to develop a plugin yourself, you should look at <a href="https://github.com/bbcf/bs.operations/blob/master/Examples.py">this plugin</a> and <a href="https://github.com/bbcf/bs.operations/blob/master/Examples_with_form.py">that one</a>.
        </p>

        <p> 
        If you want to embed BioScript in your application, all you need to do is 3 HTTP routes, 1 javascript file & 1 CSS file.
        There is a simulated example of such an application <a href="${tg.url('/devs/')}">here</a>. You can browse the code of this 
        controller <a href="https://github.com/bbcf/bs/blob/master/bs/controllers/dev.py">on github</a>.
        </p>
      
        <p>
        Embedded, you can prefill some fields with the files provided by your application.
        You have an example <a href="${tg.url('/direct/index/prefill')}">here</a>.
        </p>

   <p>
        The addition of new scripts does not require advanced computational skills and is facilitated
        by the plugin system in the application. It is designed to be simple and fast.
        You can found more 
        </p>

        <p>
        BioScript is built to be easily plugged into any third party application through a cross-domain programming
        interface. BioScript can be used and accessed from any web application.
        </p>

        <p>
        Simple & straightforward, with the complexity hidden for end-users, it allows quick installation and access
        to multiple tools. End-users may ignore where and how the operations are launched: on a dedicated machine with
        adapted CPU & RAM.
        </p>
        More documentation can be found on <a href="http://bbcf.epfl.ch/bs/">BBCF website</a>.
    </div>

    ${d.footer()}
</body>


</html>
