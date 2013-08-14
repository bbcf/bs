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
                  <div class="row">
                    <div id="thechart" class="panel panel-primary col-lg-11">
                      <!-- head -->
                      <div id="thechart-heading" class="panel-heading text-center">Jobs per <span id="thechart-title-label">...</span></div>
                      <!-- content -->
                      <div class="row">
                        <div class="col-lg-6">
                          <div id="thechart-content" class="panel-content collapsable"></div>
                        </div>
                          <!-- stat panel -->
                         <div class="col-lg-3 pull-right">
                            <div id="statpanel_content" class="collapsable panel-content"></div>
                         </div>
                      </div>

                      <!-- footer -->
                      <div id="thechart-footer" class="panel-footer collapsable">
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

                    <div class="col-lg-2"></div>

                    
                  </div> <!-- end row -->

                  <div class="row">
                    <div id="mused-chart" class="panel panel-primary col-lg-11">
                      <div class="panel-heading text-center">Most used plugins</div>
                      <div class="row">
                        <div id="mused-chart-content" class="col-lg-8 panel-content collapsable"></div>
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
                  </div>

              </div>


    ${d.footer()}

</body>

<script>
    var bioscript_jobs = ${jobs|n};
</script>
  ${d.start_chart()};
</html>
