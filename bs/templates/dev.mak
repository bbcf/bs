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
        User can access to BioScript directly, but BioScript can also be embedded in an application.
        File upload fields can be pre-filled with the application files.<br/>
        You have example <a href="${tg.url('/visual/index/prefill')}">here</a>.
        </p>

        <p>
            BioScript use controlled vocabulary to identify the file's type. You have the list of words
            <a href="${tg.url('/vocabulary')}">here</a>.
        </p>

    </div>

    ${d.footer()}
</body>


</html>
