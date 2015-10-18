<!DOCTYPE html>
<meta charset="utf-8">
<style>

.node {
  stroke: #fff;
  stroke-width: 1.5px;
}

.link {
  stroke: #bbb;
  fill: none;
  stroke-opacity: .6;
}

text {
  font: 10px sans-serif;
  pointer-events: none;
  text-shadow: 0 1px 0 #fff, 1px 0 0 #fff, 0 -1px 0 #fff, -1px 0 0 #fff;
}
</style>
<body>

<div id="container">
<text x="20" y="20" font-family="sans-serif" font-size="30px" fill="red">Country View </text>
<select name="country" id="country" onchange="show(this.options[this.selectedIndex].value, this.options[this.selectedIndex].text);">
    <option>Please select country</option>
    <option value="af.json">Afghanistan</option>
    <option value="ag.json">Antigua and Barbuda</option>
    <option value="ai.json">Anguilla</option>
    <option value="am.json">Armenia</option>
    <option value="ao.json">Angola</option>
    <option value="as.json">American Samoa</option>
    <option value="aw.json">Aruba</option>
    <option value="ax.json">X3</option>
    <option value="az.json">Azerbaijan</option>
    <option value="ba.json">Bosnia and Herzegovina</option>
    <option value="bb.json">Barbados</option>
    <option value="bf.json">Burkina Faso</option>
    <option value="bi.json">Burundi</option>
    <option value="bm.json">Bermuda</option>
    <option value="bn.json">Brunei</option>
    <option value="bo.json">Bolivia</option>
    <option value="bq.json">X4</option>
    <option value="bs.json">Bahamas</option>
    <option value="bw.json">Botswana</option>
    <option value="cd.json">Democratic Republic of the Congo</option>
    <option value="cf.json">Central African Republic</option>
    <option value="cg.json">Republic of the Congo</option>
    <option value="ck.json">Cook Islands</option>
    <option value="cm.json">Cameroon</option>
    <option value="co.json">Colombia</option>
    <option value="cr.json">Costa Rica</option>
    <option value="cu.json">Cuba</option>
    <option value="dj.json">Djibouti</option>
    <option value="do.json">Dominican Republic</option>
    <option value="dz.json">Algeria</option>
    <option value="et.json">Ethiopia</option>
    <option value="fm.json">Micronesia</option>
    <option value="fo.json">Faroe Islands</option>
    <option value="ga.json">Gabon</option>
    <option value="gd.json">gd</option>
    <option value="ge.json">ge</option>
    <option value="gf.json">gf</option>
    <option value="gg.json">gg</option>
    <option value="gh.json">gh</option>
    <option value="gi.json">gi</option>
    <option value="gl.json">gl</option>
    <option value="gm.json">Gambia</option>
    <option value="gn.json">Guinea</option>
    <option value="gp.json">X5</option>
    <option value="gq.json">Equatorial Guinea</option>
    <option value="gt.json">Guatemala</option>
    <option value="gw.json">Guinea-Bissau</option>
    <option value="hn.json">Honduras</option>
    <option value="hr.json">Croatia</option>
    <option value="ht.json">Haiti</option>
    <option value="im.json">Isle of Man</option>
    <option value="io.json">io</option>
    <option value="iq.json">Iraq</option>
    <option value="jo.json">Jordan</option>
    <option value="kg.json">Kyrgyzstan</option>
    <option value="km.json">km</option>
    <option value="kn.json">Saint Kitts and Nevis</option>
    <option value="kp.json">kp</option>
    <option value="kw.json">Kuwait</option>
    <option value="lr.json">Liberia</option>
    <option value="ls.json">Lesotho</option>
    <option value="ly.json">Libya</option>
    <option value="ma.json">Morocco</option>
    <option value="mc.json">Monaco</option>
    <option value="me.json">me</option>
    <option value="mf.json">Saint Martin</option>
    <option value="mg.json">Madagascar</option>
    <option value="mh.json">mh</option>
    <option value="mk.json">Macedonia</option>
    <option value="ml.json">Mali</option>
    <option value="mm.json">Myanmar</option>
    <option value="mo.json">Macao</option>
    <option value="mr.json">Mauritania</option>
    <option value="mv.json">Maldives</option>
    <option value="mw.json">Malawi</option>
    <option value="mz.json">Mozambique</option>
    <option value="ne.json">Niger</option>
    <option value="nf.json">X1</option>
    <option value="ni.json">Nicaragua</option>
    <option value="nr.json">Nauru</option>
    <option value="pe.json">Peru</option>
    <option value="pf.json">French Polynesia</option>
    <option value="pm.json">Saint Pierre and Miquelon</option>
    <option value="ps.json">Palestine</option>
    <option value="pw.json">Palau</option>
    <option value="py.json">Paraguay</option>
    <option value="re.json">Reunion</option>
    <option value="rw.json">Rwanda</option>
    <option value="sb.json">Solomon Islands</option>
    <option value="sc.json">Seychelles</option>
    <option value="sd.json">Sudan</option>
    <option value="si.json">Slovenia</option>
    <option value="sl.json">Sierra Leone</option>
    <option value="sm.json">San Marino</option>
    <option value="sn.json">Senegal</option>
    <option value="so.json">Somalia</option>
    <option value="sr.json">Suriname</option>
    <option value="ss.json">South Sudan</option>
    <option value="st.json">st</option>
    <option value="sv.json">El Salvador</option>
    <option value="sy.json">Syria</option>
    <option value="sz.json">Swaziland</option>
    <option value="td.json">Chad</option>
    <option value="tg.json">Togo</option>
    <option value="tj.json">Tajikistan</option>
    <option value="tl.json">East Timor</option>
    <option value="tm.json">Turkmenistan</option>
    <option value="tn.json">Tunisia</option>
    <option value="tt.json">Trinidad and Tobago</option>
    <option value="ug.json">Uganda</option>
    <option value="uy.json">Uruguay</option>
    <option value="uz.json">Uzbekistan</option>
    <option value="va.json">va</option>
    <option value="vc.json">Saint Vincent and the Grenadines</option>
    <option value="vg.json">British Virgin Islands</option>
    <option value="wf.json">wf</option>
    <option value="ws.json">Samoa</option>
    <option value="ye.json">Yemen</option>
    <option value="yt.json">Mayotte</option>
    <option value="zm.json">Zambia</option>
</select>​
</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/d3/3.5.5/d3.min.js"></script>

<script>

    function show(json_country, country_name) {
        
        // REFERENCES
        // http://jsdatav.is/chap07.html
        // https://www.dashingd3js.com/svg-text-element (How to insert text)
        // http://bl.ocks.org/ChrisJamesC/4474971 (text in circles + json)
        // http://bl.ocks.org/mbostock/4600693 (curved link)
        
        var width = 960,
            height = 750;

        var color = d3.scale.category20();

        var force = d3.layout.force()
            .charge(-100)
            .linkDistance(10)
            .linkStrength(2)
            .gravity(0.2)
            .size([width, height]);

        var svg = d3.select("#container").append("svg")
            .attr("width", width)
            .attr("height", height);
            
        d3.json(json_country, function(error, graph) {
          if (error) throw error;

          var nodes = graph.nodes.slice(),
          links = [],
          bilinks = [];

          graph.links.forEach(function(link) {
            var s = nodes[link.source],
                t = nodes[link.target],
                i = {}; // intermediate node
            nodes.push(i);
            links.push({source: s, target: i}, {source: i, target: t});
            bilinks.push([s, i, t]);
          });

            force
              .nodes(nodes)
              .links(links)
              .start();

          var link = svg.selectAll(".link")
              .data(bilinks)
            .enter().append("path")
              .attr("class", "link");

          var node = svg.selectAll(".node")
              .data(graph.nodes)
            .enter().append("circle")
              .attr("class", "node")
              .attr("r", 7)
              .style("fill", function(d) { return color(d.country); })
              .call(force.drag);

          node.append("title")
              .text(function(d) { return d.name; });

          force.on("tick", function() {
            link.attr("d", function(d) {
              return "M" + d[0].x + "," + d[0].y
                  + "S" + d[1].x + "," + d[1].y
                  + " " + d[2].x + "," + d[2].y;
            });
            node.attr("transform", function(d) {
              return "translate(" + d.x + "," + d.y + ")";
            });
          });
          
          
        // NOT WORKING NOW!! 
        node.on('click', function(d) {

            node
                .filter(function(node) { return node !== d; })
                .classed('selected', false)
                .attr('r', nodeRadius);

            edge.classed('selected', false);

            if (d3.select(this).classed('selected')) {
                d3.select(this)
                    .classed('selected', false)
                    .attr('r', nodeRadius)

            } else {
                d3.select(this)
                    .classed('selected', true)
                    .attr('r', 1.5*nodeRadius);
               
               edge.each(function(edge) {
                    if ((edge.source === d) || (edge.target === d)) {
                        d3.select(this).classed('selected',true);
                    }
               });
            }
        });
          
          
          
          
        });     
    }
</script>