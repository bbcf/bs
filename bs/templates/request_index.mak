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
        % if status == 'FAILURE':
            <p>Operation termined with error : </p>
            <div class='error'>${msg}</div>
        % elif status == 'PENDING' :
            <div class='note'>${msg}</div>
        % elif status == 'NORESULT':
            <div class='note'>${msg}</div>
        % elif status == 'SUCCESS':
            % for r in results:
                <p><a href="${links}&amp;name=${r}">${r}</a></p>
            % endfor

        % endif
    </div>

    ${d.footer()}


</body>
</html>
