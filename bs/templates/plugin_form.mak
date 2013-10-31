<html>
<head></head>
<body>
    <div class="bs_container">
        <div class="bs_title">${title}</div>
        <div class="bs_desc">${desc|n}</div>
        <div class="bs_desc">by ${author} (<a href="mailto:${contact}?subject=[BioScript]">contact</a>, 
          <a href="${html_doc}">doc</a>, <a href="${html_src_code}">code</a>)</div>
        <div class="bs_form">${widget.display()|n}</div>

</body>
</html>
