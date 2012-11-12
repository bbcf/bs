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
            <p> Job <b>${task_id}</b> ${status}.</p>
            % for result in results:
                % if result['is_file']:
                    <p>File : <a href=${result['path']}>${result['fname']}</a></p>
                % else:
                    <p>Operation return : ${result['result']}</p>
                % endif
            % endfor
        % endif
    </div>

    ${d.footer()}


</body>
</html>
