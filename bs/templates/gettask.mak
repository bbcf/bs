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
            <p>
                task <span class="jpending">${task.id} : ${task.task_id}</span> is <i>${task.status}</i>
                 at ${task.date_done}.
                <br/>
            </p>
          
    </div>

</body>
</html>
