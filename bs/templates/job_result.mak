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
        % if error:
           ${error}
        % elif result:
            ${result}
        % endif
        </p>
    </div>

    ${d.footer()}


</body>
</html>