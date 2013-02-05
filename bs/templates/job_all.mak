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
            <ul>
            % for job in jobs:
                <li>id : ${job.id}
                    % for r in ${job.status}:
                        ${r}
                    %endfor

                </li>
            % endfor
            </ul>
             
    </div>

    ${d.footer()}


</body>
</html>
