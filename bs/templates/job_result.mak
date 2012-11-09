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
        % if error:
           <p>${error}</p>
        % elif result:
            <p>${result}</p>
        % endif
    </div>

    ${d.footer()}


</body>
</html>