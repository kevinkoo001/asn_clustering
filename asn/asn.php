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
    <option value="ae.json">United Arab Emirates</option>
    <option value="af.json">Afghanistan</option>
    <option value="al.json">Albania</option>
    <option value="am.json">Armenia</option>
    <option value="ao.json">Angola</option>
    <option value="ar.json">Argentina</option>
    <option value="as.json">American Samoa</option>
    <option value="at.json">Austria</option>
    <option value="au.json">Australia</option>
    <option value="aw.json">Aruba</option>
    <option value="az.json">Azerbaijan</option>
    <option value="ba.json">Bosnia and Herzegovina</option>
    <option value="bb.json">Barbados</option>
    <option value="bd.json">Bangladesh</option>
    <option value="be.json">Belgium</option>
    <option value="bf.json">Burkina Faso</option>
    <option value="bg.json">Bulgaria</option>
    <option value="bh.json">Bahrain</option>
    <option value="bi.json">Burundi</option>
    <option value="bj.json">Benin</option>
    <option value="bm.json">Bermuda</option>
    <option value="bn.json">Brunei Darussalam</option>
    <option value="bo.json">Bolivia (Plurinational State of)</option>
    <option value="bq.json">Bonaire</option>
    <option value="br.json">Brazil</option>
    <option value="bt.json">Bhutan</option>
    <option value="bw.json">Botswana</option>
    <option value="by.json">Belarus</option>
    <option value="bz.json">Belize</option>
    <option value="ca.json">Canada</option>
    <option value="cd.json">Congo (Democratic Republic of the)</option>
    <option value="cg.json">Congo</option>
    <option value="ch.json">Switzerland</option>
    <option value="ci.json">Cote d'Ivoire</option>
    <option value="cl.json">Chile</option>
    <option value="cm.json">Cameroon</option>
    <option value="cn.json">China</option>
    <option value="co.json">Colombia</option>
    <option value="cr.json">Costa Rica</option>
    <option value="cu.json">Cuba</option>
    <option value="cw.json">Curacao</option>
    <option value="cy.json">Cyprus</option>
    <option value="cz.json">Czech Republic</option>
    <option value="de.json">Germany</option>
    <option value="dj.json">Djibouti</option>
    <option value="dk.json">Denmark</option>
    <option value="dm.json">Dominica</option>
    <option value="do.json">Dominican Republic</option>
    <option value="dz.json">Algeria</option>
    <option value="ec.json">Ecuador</option>
    <option value="ee.json">Estonia</option>
    <option value="eg.json">Egypt</option>
    <option value="es.json">Spain</option>
    <option value="eu.json">Europe</option>
    <option value="fi.json">Finland</option>
    <option value="fj.json">Fiji</option>
    <option value="fr.json">France</option>
    <option value="ga.json">Gabon</option>
    <option value="gb.json">United Kingdom of Great Britain and Northern Ireland</option>
    <option value="gd.json">Grenada</option>
    <option value="ge.json">Georgia</option>
    <option value="gg.json">Guernsey</option>
    <option value="gh.json">Ghana</option>
    <option value="gi.json">Gibraltar</option>
    <option value="gm.json">Gambia</option>
    <option value="gn.json">Guinea</option>
    <option value="gp.json">Guadeloupe</option>
    <option value="gq.json">Equatorial Guinea</option>
    <option value="gr.json">Greece</option>
    <option value="gt.json">Guatemala</option>
    <option value="gu.json">Guam</option>
    <option value="gy.json">Guyana</option>
    <option value="hk.json">Hong Kong</option>
    <option value="hn.json">Honduras</option>
    <option value="hr.json">Croatia</option>
    <option value="ht.json">Haiti</option>
    <option value="hu.json">Hungary</option>
    <option value="id.json">Indonesia</option>
    <option value="ie.json">Ireland</option>
    <option value="il.json">Israel</option>
    <option value="in.json">India</option>
    <option value="iq.json">Iraq</option>
    <option value="ir.json">Iran (Islamic Republic of)</option>
    <option value="is.json">Iceland</option>
    <option value="it.json">Italy</option>
    <option value="je.json">Jersey</option>
    <option value="jm.json">Jamaica</option>
    <option value="jo.json">Jordan</option>
    <option value="jp.json">Japan</option>
    <option value="ke.json">Kenya</option>
    <option value="kg.json">Kyrgyzstan</option>
    <option value="kh.json">Cambodia</option>
    <option value="kn.json">Saint Kitts and Nevis</option>
    <option value="kr.json">Korea (Republic of)</option>
    <option value="kw.json">Kuwait</option>
    <option value="kz.json">Kazakhstan</option>
    <option value="la.json">Lao People's Democratic Republic</option>
    <option value="lb.json">Lebanon</option>
    <option value="li.json">Liechtenstein</option>
    <option value="lk.json">Sri Lanka</option>
    <option value="ls.json">Lesotho</option>
    <option value="lt.json">Lithuania</option>
    <option value="lu.json">Luxembourg</option>
    <option value="lv.json">Latvia</option>
    <option value="ly.json">Libya</option>
    <option value="ma.json">Morocco</option>
    <option value="mc.json">Monaco</option>
    <option value="md.json">Moldova (Republic of)</option>
    <option value="me.json">Montenegro</option>
    <option value="mf.json">Saint Martin (French part)</option>
    <option value="mg.json">Madagascar</option>
    <option value="mh.json">Marshall Islands</option>
    <option value="mk.json">Macedonia (the former Yugoslav Republic of)</option>
    <option value="ml.json">Mali</option>
    <option value="mm.json">Myanmar</option>
    <option value="mn.json">Mongolia</option>
    <option value="mo.json">Macao</option>
    <option value="mr.json">Mauritania</option>
    <option value="mt.json">Malta</option>
    <option value="mu.json">Mauritius</option>
    <option value="mv.json">Maldives</option>
    <option value="mw.json">Malawi</option>
    <option value="mx.json">Mexico</option>
    <option value="my.json">Malaysia</option>
    <option value="mz.json">Mozambique</option>
    <option value="na.json">Namibia</option>
    <option value="nc.json">New Caledonia</option>
    <option value="ne.json">Niger</option>
    <option value="ng.json">Nigeria</option>
    <option value="ni.json">Nicaragua</option>
    <option value="nl.json">Netherlands</option>
    <option value="no.json">Norway</option>
    <option value="np.json">Nepal</option>
    <option value="nz.json">New Zealand</option>
    <option value="om.json">Oman</option>
    <option value="pa.json">Panama</option>
    <option value="pe.json">Peru</option>
    <option value="pf.json">French Polynesia</option>
    <option value="pg.json">Papua New Guinea</option>
    <option value="ph.json">Philippines</option>
    <option value="pk.json">Pakistan</option>
    <option value="pl.json">Poland</option>
    <option value="pr.json">Puerto Rico</option>
    <option value="ps.json">Palestine</option>
    <option value="pt.json">Portugal</option>
    <option value="py.json">Paraguay</option>
    <option value="qa.json">Qatar</option>
    <option value="ro.json">Romania</option>
    <option value="rs.json">Serbia</option>
    <option value="ru.json">Russian Federation</option>
    <option value="rw.json">Rwanda</option>
    <option value="sa.json">Saudi Arabia</option>
    <option value="sc.json">Seychelles</option>
    <option value="sd.json">Sudan</option>
    <option value="se.json">Sweden</option>
    <option value="sg.json">Singapore</option>
    <option value="si.json">Slovenia</option>
    <option value="sk.json">Slovakia</option>
    <option value="sl.json">Sierra Leone</option>
    <option value="sm.json">San Marino</option>
    <option value="sn.json">Senegal</option>
    <option value="so.json">Somalia</option>
    <option value="ss.json">South Sudan</option>
    <option value="sv.json">El Salvador</option>
    <option value="sx.json">Sint Maarten (Dutch part)</option>
    <option value="sy.json">Syrian Arab Republic</option>
    <option value="sz.json">Swaziland</option>
    <option value="tg.json">Togo</option>
    <option value="th.json">Thailand</option>
    <option value="tj.json">Tajikistan</option>
    <option value="tm.json">Turkmenistan</option>
    <option value="tn.json">Tunisia</option>
    <option value="to.json">Tonga</option>
    <option value="tr.json">Turkey</option>
    <option value="tt.json">Trinidad and Tobago</option>
    <option value="tw.json">Taiwan</option>
    <option value="tz.json">Tanzania</option>
    <option value="ua.json">Ukraine</option>
    <option value="ug.json">Uganda</option>
    <option value="us.json">United States of America</option>
    <option value="uy.json">Uruguay</option>
    <option value="uz.json">Uzbekistan</option>
    <option value="vc.json">Saint Vincent and the Grenadines</option>
    <option value="ve.json">Venezuela (Bolivarian Republic of)</option>
    <option value="vi.json">Virgin Islands (U.S.)</option>
    <option value="vn.json">Viet Nam</option>
    <option value="vu.json">Vanuatu</option>
    <option value="ws.json">Samoa</option>
    <option value="ye.json">Yemen</option>
    <option value="za.json">South Africa</option>
    <option value="zm.json">Zambia</option>
    <option value="zw.json">Zimbabwe</option>
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