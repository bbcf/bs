<!DOCTYPE HTML>
<html lang="en">
<head>
    <%namespace name="d" file="bs.templates.definitions"/>
    ${d.js()}
    ${d.css()}
    ${d.chart_css()}
    ${d.chart_js()}
    ${d.title()}


</head>


<body>

    ${d.banner()}
     <div class="container">

            <div class="panel-group" id="accordion">
                <!-- job per ... --->
                    <div id="thechart" class="panel panel-primary col-lg-11">
                      <!-- head -->
                      <div id="thechart-heading" data-toggle="collapse" data-parent="#accordion" href="#panel-one" class="panel-heading text-center accordion-toggle">Jobs per <span id="thechart-title-label">...</span></div>
                      <!-- content -->
                      <div id="panel-one" class="row panel-collapse collapse in">
                        <div class="col-lg-6">
                          <div id="thechart-content" class="panel-content"></div>
                        </div>
                          <!-- stat panel -->
                        <div class="col-lg-4 pull-right">
                          <div id="statpanel_content" class="row panel-content"></div>
                          <div id="piechart" class="row panel-content"></div>
                        </div>
                      </div>

                      <!-- footer -->
                      <div id="thechart-footer" class="panel-footer">
                          <!-- start radios -->
                          <div id="chart_chooser" class="form-inline">
                            <div class="radio">
                              <label>
                                <input type="radio" name="chart_chooser" value="hours" checked>
                                Hours
                              </label>
                            </div>
                            <div class="radio">
                              <label>
                                <input type="radio" name="chart_chooser" value="days">
                                Days
                              </label>
                            </div>
                            <div class="radio">
                              <label>
                                <input type="radio" name="chart_chooser" value="months">
                                Months
                              </label>
                            </div>
                          </div><!-- end radios -->
                      </div><!-- end footer -->
                    </div><!-- end thechart -->

                    

                  <!-- circles chart -->
                    <div id="mused-chart" class="panel panel-primary col-lg-11">
                      <div data-toggle="collapse" data-parent="#accordion" href="#panel-two" class="panel-heading text-center accordion-toggle">Most used plugins / circles</div>
                      <div id="panel-two" class="row panel-collapse collapse">
                        <div class="col-lg-8">
                          <div id="mused-chart-content" class="panel-content"></div>
                        </div>
                        <div class="col-lg-3 pull-right">
                            <div id="mused-chart-tooltip"></div>
                        </div>  
                      </div>

                      <!-- footer -->
                      <div id="mused-chart-footer" class="panel-footer collapsable">
                          <!-- start radios -->
                          <div id="mused-chart-chooser" class="form-inline">
                            <label>
                              If you click on a circle, you will be redirected to the
                            </label>
                            <div class="radio">
                              <label>
                                <input type="radio" name="mused-chart-chooser" value="form" checked>
                                form
                              </label>
                            </div>
                            <div class="radio">
                              <label>
                                <input type="radio" name="mused-chart-chooser" value="doc">
                                documentation
                              </label>
                            </div>
                            <div class="radio">
                              <label>
                                <input type="radio" name="mused-chart-chooser" value="code">
                                source code
                              </label>
                            </div>
                          </div><!-- end radios -->
                      </div><!-- end footer -->
                    </div>

                  <!-- treemap chart -->
                    <div id="treemap-chart" class="panel panel-primary col-lg-11">
                      <div data-toggle="collapse" data-parent="#accordion" href="#panel-three" class="panel-heading text-center accordion-toggle">Most used plugins / treemap</div>
                      <div id="panel-three" class="row panel-collapse collapse">
                        <div id="treemap-chart-content" class="col-lg-8 panel-content"></div>
                        <div class="col-lg-3 pull-right">
                            <div id="treemap-chart-tooltip"></div>
                        </div>
                        
                    </div>
                      <!-- footer -->
                      <div id="treemap-chart-footer" class="panel-footer collapsable">
                          <!-- start radios -->
                          <div id="treemap-chart-chooser" class="form-inline">
                            <label>
                              If you click on a square, you will be redirected to the
                            </label>
                            <div class="radio">
                              <label>
                                <input type="radio" name="treemap-chart-chooser" value="form" checked>
                                form
                              </label>
                            </div>
                            <div class="radio">
                              <label>
                                <input type="radio" name="treemap-chart-chooser" value="doc">
                                documentation
                              </label>
                            </div>
                            <div class="radio">
                              <label>
                                <input type="radio" name="treemap-chart-chooser" value="code">
                                source code
                              </label>
                            </div>
                          </div><!-- end radios -->
                      </div><!-- end footer -->
                    </div>

            </div>
</body>

<script>
    var bioscript_jobs = ${jobs|n};
    var bs_url = ${tg.url('/')};
</script>
  ${d.start_chart()}
</html>
