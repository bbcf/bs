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

    <div id="bs_operations"></div>
    
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
    ${d.footer()}

</body>

    <%!
    def se(text):
        return "'" + text + "'"
    %>




<script>
    window.onload = function(){
        var options = {
            operation_list : ${oplist|n},
            show_plugin : function(plugin_id){

                window.location = ${serv|se,n} + 'direct/' + ${method|se,n}+ '?id=' + plugin_id;
            },
            'root_name' : 'Operations'
        }
        $('#bs_operations').bioscript(options).bioscript('operation_list');
    };
</script>

</html>
