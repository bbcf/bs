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
        % if not job_id:
           <p> No job identifier specified.</p>
        % elif error:
            <p> ${error} </p>
        % else:
            <p> Job ${job_id}.</p>
            <p><ul>
            % for result in results:
                <li>${result}</li>
            % endfor
            </ul></p>
        % endif
    </div>

    ${d.footer()}


</body>
</html>
