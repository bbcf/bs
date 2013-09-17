<html>
<head></head>
<body>
    <div class="bs_container">
        <div class="bs_title">${title}</div>
        <div class="bs_desc">${desc|n}</div>
        <div class="bs_desc"><a href="${html_doc}">doc</a> - <a href="${html_src_code}">code</a></div>
        <div class="bs_desc"><br/>by ${author} (<a href="mailto:${contact}?subject=[BioScript]">contact</a>)
        <div class="bs_form">${widget.display()|n}</div>
        <div class="bs_desc">The author of this operation is '${author}': <a href="mailto:${contact}?subject=[BioScript]">contact</a>.

</body>
</html>
