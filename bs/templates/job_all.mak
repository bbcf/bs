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
                Job <a href="${tg.url('/jobs')}?task_id=${job.task_id}" >${job.task_id}</a> is <i>${job.status}</i>
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
    <!-- </table>           
        <table cellspacing="1" cellpadding="0" border="0" class="grid">
        <thead><tr>
        <th>Task_id</th>
        <th>Status</th>
        <th>Date</th>
        <th>Result(s)</th>
        </tr></thead>

            % for job in jobs:
            <tr>
                <td>${job.task_id}</td>
                <td>${job.status}</td>
                <td>${job.request.date_done}</td>
                <td>
                % for r in job.results:
                    % if r.is_file:
                        ${r.fname}
                    % else:
                        ${r.result}
                    % endif
                % endfor
                </td>
            </tr>
            % endfor
    </table>  -->           
    </div>

</body>
</html>
