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

            % for job in jobs:
            <p>
                Job <span class="jpending">${job.request.plugin.info['title']}</span> <a href="${tg.url('/jobs')}?task_id=${job.task_id}" >${job.task_id}</a> is <i>${job.status}</i>
                 at ${job.request.date_done}.
                <br/>

                % for r in job.results:
                    % if r.is_file:
                        ${r.fname}
                    % else:
                        ${r.result}
                    % endif
                % endfor

                % if job.simple_error:
                    ${job.simple_error}
                % endif

            </p>
            % endfor
          
    </div>

</body>
</html>
