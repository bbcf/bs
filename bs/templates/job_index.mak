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

            <!-- DISPLAY RESULTS -->
            % for result in results:
                % if result['is_file']:
                    <p>File : <a href=${result['path']}>${result['fname']}</a></p>
                % else:
                    <p>Operation return : ${result['result']}</p>
                % endif
            % endfor

            <!-- DISPLAY TRACEBACK -->
            % if traceback != '':
                <p>${traceback}     <a class='full_traceback'>full traceback</a><br/> 
                <span class='full_traceback'>${full_traceback}</span></p>
            % endif
            <!-- DISPLAY JOB INFORMATION -->
            <div class="belement">
                <h2>Job Information</h2>
                <ul>
                    <li>Date : ${date}</li>
                    <li>Plugin identifier: ${plugin_id}</li>
                    <li>
                        Plugin information: 
                        <div class='belement'>
                       <ul> 
                            % for k, v in plugin_info.iteritems():
                                <li>${k} : ${v}</li>
                            %endfor
                        </ul></div>
                    </li>

                    <li>
                        Plugin parameters: 
                        <div class='belement'>
                       <ul> 
                            % for k, v in parameters.iteritems():
                                <li>${k} : ${v}</li>
                            %endfor
                        </ul></div>
                    </li>
                </ul>
            </div>
        % endif
    </div>

    ${d.footer()}


</body>
${d.full_traceback_js()}
</html>
