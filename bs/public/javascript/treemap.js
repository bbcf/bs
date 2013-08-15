function treemapgraph(bsurl, w, h, valuedata){

  var color = d3.scale.category20c();

  var treemap = d3.layout.treemap()
      .size([w, h])
      .sticky(true)
      .children(function(d){
      return d.childs;
    })
  //fetch their value stored in another variable
      .value(function(d) {
        return valuedata[d.info.title];
    });

  var div = d3.select("#treemap-chart-content").append("div")
      .style("position", "relative")
      .style("width", (w + margin.left + margin.right) + "px")
      .style("height", (h + margin.top + margin.bottom) + "px")
      .style("left", margin.left + "px")
      .style("top", margin.top + "px");

  d3.json(bsurl + "plugins?ordered=True", function(error, root) {
    var treenode = div.datum(root.plugins).selectAll(".treenode")
        .data(treemap.nodes).enter().append("div")
        .attr("class", "treenode")
        .call(position)
        .style("background", function(d) { return d.childs ? color(d.key) : null; })
        .text(function(d) { return d.childs ? null : d.key; });

    // d3.selectAll("input").on("change", function change() {
    //   var value = this.value === "count" ? function() { return 1; } : function(d) { return d.size; };
      
    //   treenode
    //       .data(treemap.value(value).nodes)
    //     .transition()
    //       .duration(1500)
    //       .call(position);
    // });

     //red border on mouseover
    //and tooltip

     var tooltip = d3.select("#treemap-chart-tooltip")
    .append("div")
    .style("z-index", "10")
    .style("visibility", "hidden");

    treenode.on('mouseover', function(d){
      d3.select(this)
      .attr('class', 'htreenode');
      var bi = badge_info(d.key, d.childs ? d.childs.length + " children" : d.value + " jobs");
      tooltip.style("visibility", "visible").html(bi);
    })
    .on('mouseout', function(){
      d3.select(this)
      .attr('class', 'treenode');
      tooltip.style("visibility", "hidden");
    });


      treenode.on('click', function(d){
      var redirecto = $('input[name=treemap-chart-chooser]:radio:checked').val();
      var loc = '';
      if(redirecto == 'doc'){
        loc = d.info.html_doc;
      } else if(redirecto == 'code'){
        loc = d.info.html_src_code;
      } else {
        loc = bsurl + '/direct/get?id=' + d.id;
      }
      window.open(loc);
      });

  });

}


function position() {
  this.style("left", function(d) { return d.x + "px"; })
      .style("top", function(d) { return d.y + "px"; })
      .style("width", function(d) { return Math.max(0, d.dx - 1) + "px"; })
      .style("height", function(d) { return Math.max(0, d.dy - 1) + "px"; });
}
treemapgraph(bs_url, 860, 560, bioscript_jobs['plugins']);


