# body {
#   font-family: "Helvetica Neue", Helvetica, sans-serif;
#   margin: 30px auto;
#   width: 1280px;
#   position: relative;
# }

css = """
header {
  padding: 6px 0;
}

.group {
  margin-bottom: 1em;
}

.axis {
  font: 10px sans-serif;
  position: fixed;
  pointer-events: none;
  z-index: 2;
}

.axis text {
  -webkit-transition: fill-opacity 250ms linear;
}

.axis path {
  display: none;
}

.axis line {
  stroke: #000;
  shape-rendering: crispEdges;
}

.axis.top {
  background-image: linear-gradient(top, #fff 0%, rgba(255,255,255,0) 100%);
  background-image: -o-linear-gradient(top, #fff 0%, rgba(255,255,255,0) 100%);
  background-image: -moz-linear-gradient(top, #fff 0%, rgba(255,255,255,0) 100%);
  background-image: -webkit-linear-gradient(top, #fff 0%, rgba(255,255,255,0) 100%);
  background-image: -ms-linear-gradient(top, #fff 0%, rgba(255,255,255,0) 100%);
  top: 0px;
  padding: 0 0 24px 0;
}

.axis.bottom {
  background-image: linear-gradient(bottom, #fff 0%, rgba(255,255,255,0) 100%);
  background-image: -o-linear-gradient(bottom, #fff 0%, rgba(255,255,255,0) 100%);
  background-image: -moz-linear-gradient(bottom, #fff 0%, rgba(255,255,255,0) 100%);
  background-image: -webkit-linear-gradient(bottom, #fff 0%, rgba(255,255,255,0) 100%);
  background-image: -ms-linear-gradient(bottom, #fff 0%, rgba(255,255,255,0) 100%);
  bottom: 0px;
  padding: 24px 0 0 0;
}

.horizon {
  border-bottom: solid 1px #000;
  overflow: hidden;
  position: relative;
}

.horizon {
  border-top: solid 1px #000;
  border-bottom: solid 1px #000;
}

.horizon + .horizon {
  border-top: none;
}

.horizon canvas {
  display: block;
}

.horizon .title,
.horizon .value {
  bottom: 0;
  line-height: 30px;
  margin: 0 6px;
  position: absolute;
  text-shadow: 0 1px 0 rgba(255,255,255,.5);
  white-space: nowrap;
}

.horizon .title {
  left: 0;
  color: rgb(200,50,50);
  font-weight: bold;
}

.horizon .value {
  right: 0;
}

.line {
  background: #000;
  z-index: 2;
}
"""

scripts = [
  'http://d3js.org/d3.v2.js',
  'http://square.github.com/cubism/cubism.v1.js'
]

# <body id="demo">

body_script = """
<script>
var context = cubism.context()
    //.serverDelay(new Date(2012, 4, 2) - Date.now())
    //.step(864e5)
    .step(2)
    .size(200)
    .stop();

d3.select("#__id__").selectAll(".axis")
    .data(["top", "bottom"])
  .enter().append("div")
    .attr("class", function(d) { return d + " axis"; })
    .each(function(d) { d3.select(this).call(context.axis().ticks(12).orient(d)); });

d3.select("#__id__").append("div")
    .attr("class", "rule")
    .call(context.rule());

d3.select("#__id__").selectAll(".horizon")
    .data([__devs__].map(osd_data))
    .enter().insert("div", ".bottom")
    .attr("class", "horizon")
    .call(context
          .horizon()
          .height(45)
          // .colors(["#000000", "#000000", "#000000", "#20b020", "#2020b0","#b02020"])
          .format(d3.format("+,.2p")));

context.on("focus", function(i) {
  d3.selectAll(".value").style("right", i == null ? null : context.size() - i + "px");
});

function osd_data(name) {
    function os_data_stor(start, stop, step, callback) {
        data = {
            __data__
        };
        callback(null, data[name])
    }
    var format = d3.time.format("%d-%b-%y");
    return context.metric(os_data_stor, name);
}

</script>
"""
