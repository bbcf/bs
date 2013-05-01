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
                <p>${traceback | n}     <a class='a_hideshow'>full traceback</a><br/> 
                <span class='span_hidden'>${full_traceback | n}</span></p>
            % endif


            <!-- DISPLAY JOB PARAMETERS -->
            <div class='belement'>
            <h2>Plugin parameters</h2> <br/><br/>
                <table class="job_params">
                % for k, v in parameters.iteritems():
                    % if isinstance(v, dict):
                        <tr> <td><b>${k}</b></td><td><ul>
                        % for key, val in v.iteritems():
                            <li><i>${key}</i> :
                            % if isinstance(val, list):
                                % for item in val:
                                    ${item}, 
                                % endfor

                            % else:
                                ${val}
                            %endif
                            </li>
                        % endfor
                        </ul></td></tr>
                    % else:
                        <tr> <td><b>${k}</b></td> <td>${v}</td></tr>
                    % endif
                %endfor
                </table>
            </div>


            <!-- DISPLAY JOB INFORMATION -->
            <div class="belement">
                % if 'title' in plugin_info:
                    <h2>${plugin_info['title']}</h2>
                        <br/><br/>
                % endif

                % if 'description' in plugin_info:
                    ${plugin_info['description']}
                    <br/><br/>
                % endif
                % if 'meta' in plugin_info:
                    % if 'author' in plugin_info['meta']:
                        <b>Author</b> : ${plugin_info['meta']['author']}.
                    <br/><br/>
                    % endif
                    % if 'contact' in plugin_info['meta']:
                        <b>Contact</b> : ${plugin_info['meta']['contact']}.
                    <br/><br/>
                    % endif
                    % if 'version' in plugin_info['meta']:
                        <b>Version</b> : ${plugin_info['meta']['version']}.
                    <br/><br/>
                    % endif

                % endif

            </div>
        % endif
    </div>

    ${d.footer()}


</body>
${d.enable_a_showhide()}
</html>
