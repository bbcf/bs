// get data
var data = bioscript_jobs['hours'];
var ndata = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24];



// positionning
var margin = {top: 40, right: 20, bottom: 40, left: 50};
var w = 600;
var width = w - margin.left - margin.right;
var h = 300;
var height = h - margin.top - margin.bottom;
//var barwidth = width / hours.length;



function badge_info(label, value){
  return "<div class='nav nav-pills'><span class='badge pull-right'><label>" + value + "</label></span>" + label + "</div>";
}

function piechart_users(selector, users, width, height, rad){

  var radius = rad;

  var color = d3.scale.ordinal()
      .range(["#e61447", "#8a89a6", "#3fc7e4", "#0e6bf9", "#dde410", "#d0743c", "#2ac610"]);

  var arc = d3.svg.arc()
      .outerRadius(radius - 10)
      .innerRadius(0);

  var pie = d3.layout.pie()
      .sort(null)
      .value(function(d) { return d.value; });

  var svg = d3.select(selector).append("svg")
      .attr("width", width)
      .attr("height", height)
    .append("g")
      .attr("transform", "translate(150," + height / 2 + ")");

    // users.forEach(function(d) {
    //   d.value = +d.value;
    // });

    var g = svg.selectAll(".arc")
        .data(pie(users))
      .enter().append("g")
        .attr("class", "arc");

    g.append("path")
        .attr("d", arc)
        .style("fill", function(d) { return color(d.data.name); });

    g.append("text")
        .attr("transform", function(d) { return "translate(" + arc.centroid(d) + ")"; })
        .attr("dy", ".35em")
        .style("text-anchor", "middle")
        .text(function(d) {
          if(d.data.name == 'anonymous'){
            return 'Direct access';
          } else if(d.data.name == 'HTS-DEV'){
            return 'HTSStation';
          }
          return d.data.name; });


}

piechart_users('#piechart', bioscript_jobs['users'], 500, 300, 150);

function update_stats(thedata){
  var cdata = thedata.slice(0);
  $('#statpanel_content').append(badge_info('Total', d3.sum(cdata)))
                         .append(badge_info('Mean', d3.mean(cdata).toFixed(2)))
                         // .append(badge_info('Median', d3.median(cdata).toFixed(2)))
                         // .append(badge_info('1st quantile', d3.quantile(cdata.sort(d3.ascending), 0.25).toFixed(2)))
                         // .append(badge_info('3rd quantile', d3.quantile(cdata.sort(d3.ascending), 0.75).toFixed(2)))
                         // .append(badge_info('Min', d3.min(cdata)))
                         // .append(badge_info('Max', d3.max(cdata)))
                         ;

}


function remove_elements(chart){
  $(".axis").remove();
  $(".axislabel").remove();
  $("#thechart-title-label").html("");
  chart.selectAll("rect").remove();
  $("#statpanel_content").html("");
}


function update_bar_chart(chart, thedata, x, y, title, xlabel, ylabel){
    remove_elements(chart);

    //title 
    $('#thechart-title-label').html(title);

    //scales
    var xAxis = d3.svg.axis().scale(x).orient("bottom").ticks(5);
    var yAxis = d3.svg.axis().scale(y).orient("left").ticks(5);
    
    
    //axis labels
    chart.append("text").attr("class", "axislabel").attr("transform", "translate(" + (width / 2) + " ," + (height + margin.bottom - 4) + ")")
        .style("text-anchor", "middle").text(xlabel);
    chart.append("text").attr("class", "axislabel").attr("transform", "rotate(-90)").attr("y", 0 - margin.left).attr("x",0 - (height / 2))
        .attr("dy", "1em").style("text-anchor", "middle").text(ylabel);
    
    //axis
    chart.append("g").attr("class", "axis").attr("transform", "translate(0," + height + ")").call(xAxis);
    chart.append("g").attr("class", "axis").call(yAxis);

    //bars
    var bars = chart.selectAll("rect").data(thedata);

    //set up initial positions pf the bars
    bars.enter().append("rect").attr('x', function(d, i){
      return x(i);
    }).attr("width", x.rangeBand())
    .attr("y", function(d){
         return height;
    }).attr('height', 0);

    //update position of bars based on value
    bars.transition().ease('elastic').delay(100).duration(1000)
    .attr("height", function(d){
      return height - y(d);
    }).attr("y", function(d){return y(d);});

    bars.exit().transition().duration(1000).remove();
}



var xsacles = {
    'hours' :["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "22", "23", "24"],
  'days' :["Mon", "Tue", "Wen", "Thu", "Fri", "Sat", "Sun" ],
  'months' :["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
};

//chart
var chart = d3.select("#thechart-content").append("svg").attr("class", "chart").attr("width", w).attr("height", h)
  .append("g").attr("transform", "translate("+ margin.left + "," + margin.top + ")");

function change_chart_target(name){

  var ndata = bioscript_jobs[name];
  var xdata = xsacles[name];
  var x = d3.scale.ordinal().domain(xdata).rangeBands([0, width]);
  var y = d3.scale.linear().domain([d3.max(ndata), 0]).rangeRound([0, height]);
  update_bar_chart(chart, ndata, x, y, name, name, 'n jobs');
  update_stats(ndata);
}



$('input[name=chart_chooser]:radio').on('change', function(e, i) {
  change_chart_target($(this).val());
});

change_chart_target($('input[name=chart_chooser]:radio:checked').val());



function bubblegraph(bsurl, diameter, valuedata){

  // plugins graph
  var format = d3.format(",d");

  // select childs
  var pack = d3.layout.pack()
      .size([diameter - 4, diameter - 4])
      .children(function(d){
      return d.childs;
    })
  //fetch their value stored in another variable
      .value(function(d) {
        return valuedata[d.info.title];
    });

  // set the graph 
  var pluginchart = d3.select("#mused-chart-content").append("svg")
      .attr("width", diameter)
      .attr("height", diameter)
    .append("g")
      .attr("transform", "translate(2,2)");

  // loop over all node (the loop is 'automatic', with the 'pack' method defined above)
  d3.json(bsurl + "plugins?ordered=True", function(error, root) {

    // the node
    var node = pluginchart.datum(root.plugins).selectAll(".node")
      .data(pack.nodes)
      .enter().append("g")
      .attr("class", function(d) {
        return d.childs ? "node" : "leaf node";
        })
      .attr("transform", function(d) { return "translate(" + d.x + "," + d.y + ")"; });

    // node title
    node.append("title")
        .text(function(d) {
          return d.key + (d.childs ? "" : ": " + format(valuedata[d.info.title]));
        });

    // node circle
    node.append("circle")
        .attr("r", function(d) { return d.r; });

    // write the title in the node if it's a leaf    
    node.filter(function(d) {
      return !d.childs;
      })
        .append("text")
        .attr("dy", ".3em")
        .style("text-anchor", "middle")
        .text(function(d) {
          return d.info.title.substring(0, d.r / 3);
        });

    //redirection on click
    node.filter(function(d) {
          return !d.childs;
      })
        .on('click', function(d){
      var redirecto = $('input[name=mused-chart-chooser]:radio:checked').val();
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

    //tooltip
    var tooltip = d3.select("#mused-chart-tooltip")
    .append("div")
    .style("z-index", "10")
    .style("visibility", "hidden");

    //red border on mouseover
    //and tooltip
    node.on('mouseover', function(d){
      d3.select(this)
      .append('circle')
      .attr('class', 'select')
      .attr('r', d.r + 1)
      .style('fill', 'none')
      .style('stroke', 'blue')
      .style('stroke-width', '3');
      var bi = badge_info(d.key, d.childs ? d.childs.length + " children" : d.value + " jobs");
      tooltip.style("visibility", "visible").html(bi);
    })
    .on('mouseout', function(){
      node.selectAll('.select').remove();
      tooltip.style("visibility", "hidden");
    });

  });

  

  d3.select(self.frameElement).style("height", diameter + "px");

  //tooltip
   pluginchart.append("text").attr("y", diameter - 25).attr("x",diameter - 150 )
        .attr("dy", "1em").style("text-anchor", "middle").text("Hover on circles to see more information");
}




bubblegraph(bs_url, 860, bioscript_jobs['plugins']);

