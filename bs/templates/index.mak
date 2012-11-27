<html>

<head>
    <%namespace name="d" file="bs.templates.definitions"/>
    ${d.css()}
    ${d.title()}
</head>

<body>

    ${d.banner()}

    <div id="content">
    
        <p>BioScript is a python library aiming to regroup & run bioinformatics scripts
        through a common and a simple interface. It can be used from command line or as a web service. Bioinformatics scripts
        are displayed and used as a traditional `form` way.</p>

        <p>
        The addition of new scripts does not require a high computational skills and is facilitated
        by the plugin system in the application. It is designed to be simple and fast.
        </p>

        <p>
        BioScript is built to be easily pluggable to any third party application, through a cross-domain Ajax API
        which mean that in practice, BioScript can be used and accessed from any web application.
        </p>

        <p>
        Complexity of the application is hidden for end-users – who are running the scripts -,
        but if necessary, powerful features about job brokers and job processing are accessible.
        One other advantage of this application in terms of computing power management
        is to run scripts from different applications on a dedicated server with adapted features.
        </p>
        More documentation can be found on <a href="http://bbcf.epfl.ch/bs/">BBCF website</a>.
    </div>
    
    ${d.footer()}

</body>
</html>

