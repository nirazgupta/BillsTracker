//********************** BAR CHART ***********************************

function dsBarChart1(){
  
    $.ajax({
        url: "/getdata",//"{{ url_for ('site.getdata') }}",
        type: 'GET',
        dataType: 'json',
        async: true,
        success: function (jsonData) {
   
        
        var svgWidth = 600;
        var svgHeight = 300;

        var heightPad = 50;
        var widthPad = 50;

        var tooltip = d3.select("body").append("div").attr("class", "toolTip");

        var svg = d3.select("#barChart")
            .append("svg")
            .attr("width", svgWidth + (widthPad * 2))
            .attr("height", svgHeight + (heightPad * 2))
            .append("g")
            .attr("transform", "translate(" + widthPad + "," + heightPad + ")");



    //Set up scales
    var xScale = d3.scale.ordinal()
        .domain(jsonData.map(function(d) { return d.item; }))
        .rangeRoundBands([0, svgWidth], .4);

   var yScale = d3.scale.linear()
        .domain([0, d3.max(jsonData, function (d) { return d.amount; }) ])
        .range([svgHeight,0]);

   // Create bars
    svg.selectAll("rect")
        .data(jsonData)
        .enter().append("rect")
        .attr("x", function (d) { return xScale(d.item) + widthPad; })
        .attr("y", function (d) { return yScale(d.amount); })
        .attr("height", function (d) { return svgHeight - yScale(d.amount); })
        .attr("width", xScale.rangeBand())
        .attr("fill", "teal")
        .on('mouseover', function(d){ d3.select(this) .style('opacity', 0.4),
                    tooltip
                    .style("left", d3.event.pageX - 50 + "px")
                    .style("top", d3.event.pageY - 70 + "px")
                    .style("display", "inline-block")
                    .style('opacity', 0.9)
                    .html((d.item) + "<br>" + "$" + (d.amount));
        }
            )
        .on('mouseleave', function(d){  d3.select(this) .style('opacity', 1) , tooltip.style("display", "none")})
        .on('click', function(d) { console.log(d3.select(this)) })
    // Y axis
    var yAxis = d3.svg.axis()
        .scale(yScale)
        .orient("left");

    svg.append("g")
        .attr("class", "axis")
        .attr("transform", "translate(" + widthPad + ",0)")
        .call(yAxis)
     .append("text")
        .attr("transform", "rotate(-90)")
        .attr("y", -50)
        .style("text-anchor", "middle")
        .text("Amount");

    // X axis
    var xAxis = d3.svg.axis()
    .scale(xScale)
    .orient("bottom");

    svg.append("g")
        .attr("class", "axis")
        .attr("transform", "translate(" + widthPad + "," + svgHeight + ")")
        .call(xAxis)
        .append("text")
        .attr("x", svgWidth / 2 - widthPad)
        .attr("y", 50)
        .text("Bills");
                
    } });
}



//********************** PIE CHART ***********************************
var formatAsPercentage = d3.format("%"),
    formatAsPercentage1Dec = d3.format(".1%"),
    formatAsInteger = d3.format(","),
    fsec = d3.time.format("%S s"),
    fmin = d3.time.format("%M m"),
    fhou = d3.time.format("%H h"),
    fwee = d3.time.format("%a"),
    fdat = d3.time.format("%d d"),
    fmon = d3.time.format("%b");

    function dsPieChart(){
        $.ajax({
            url: "/get_user_chart_data",//"{{ url_for ('site.getdata') }}",
            type: 'GET',
            dataType: 'json',
            async: true,
            success: function (jsonData) {
    
        var    width = 370,
               height = 370,
               outerRadius = Math.min(width, height) / 2,
               innerRadius = outerRadius * .999,   
               // for animation
               innerRadiusFinal = outerRadius * .6,
               innerRadiusFinal3 = outerRadius* .55,
               color = d3.scale.category20()    //builtin range of colors
               ;
            
        var vis = d3.select("#pieChart")
             .append("svg:svg")              //create the SVG element inside the <body>
             .data([jsonData])                   //associate our data with the document
                 .attr("width", width)           //set the width and height of our visualization (these will be attributes of the <svg> tag
                 .attr("height", height)
                     .append("svg:g")                //make a group to hold our pie chart
                 .attr("transform", "translate(" + outerRadius + "," + outerRadius + ")")    //move the center of the pie chart from 0, 0 to radius, radius
                    ;
                    
       var arc = d3.svg.arc()              //this will create <path> elements for us using arc data
                .outerRadius(outerRadius).innerRadius(innerRadius);
       
       // for animation
       var arcFinal = d3.svg.arc().innerRadius(innerRadiusFinal).outerRadius(outerRadius);
        var arcFinal3 = d3.svg.arc().innerRadius(innerRadiusFinal3).outerRadius(outerRadius);
    
       var pie = d3.layout.pie()           //this will create arc data for us given a list of values
            .value(function(d) { return d.amount; });    //we must tell it out to access the value of each element in our data array
    
       var arcs = vis.selectAll("g.slice")     //this selects all <g> elements with class slice (there aren't any yet)
            .data(pie)                          //associate the generated pie data (an array of arcs, each having startAngle, endAngle and value properties) 
            .enter()                            //this will create <g> elements for every "extra" data element that should be associated with a selection. The result is creating a <g> for every object in the data array
                .append("svg:g")                //create a group to hold each slice (we will have a <path> and a <text> element associated with each slice)
                   .attr("class", "slice")    //allow us to style things in the slices (like text)
                   .on("mouseover", mouseover)
                   .on("mousedown", function() { d3.event.stopPropagation(); })
                        .on("mouseout", mouseout)
                        .on("click", up)
                        // .on("click", function(d, i) { updateData(d.data.user_id, color(i)); })
                        ;
                        
            arcs.append("svg:path")
                   .attr("fill", function(d, i) { return color(i); } ) //set the color for each slice to be chosen from the color function defined above
                   .attr("d", arc)     //this creates the actual SVG path using the associated data (pie) with the arc drawing function
                        .append("svg:title") //mouseover title showing the figures
                       .text(function(d) { return d.data.name + ": " + '$' +d.data.amount; })
                       		
    
            d3.selectAll("g.slice").selectAll("path").transition()
                    .duration(750)
                    .delay(10)
                    .attr("d", arcFinal )
                    ;
        
          // Add a label to the larger arcs, translated to the arc centroid and rotated.
          arcs.filter(function(d) { return d.endAngle - d.startAngle > .2; })
              .append("svg:text")
              .attr("dy", ".35em")
              .attr("text-anchor", "middle")
              .attr("transform", function(d) { return "translate(" + arcFinal.centroid(d) + ")rotate(" + angle(d) + ")"; })
              .attr("class", "piechart_text")
              //.text(function(d) { return formatAsPercentage(d.value); })
              .text(function(d) { return d.data.name; })
              ;
           
           // Computes the label angle of an arc, converting from radians to degrees.
            function angle(d) {
                var a = (d.startAngle + d.endAngle) * 90 / Math.PI - 90;
                return a > 90 ? a - 180 : a;
            }
                
            
            // Pie chart title			
            vis.append("svg:text")
                 .attr("dy", ".35em")
              .attr("text-anchor", "middle")
              .text("Group member expenses")
              .attr("class","title")
              ;		    
    
    
        function mouseover() {
          d3.select(this).select("path").transition()
              .duration(750)
                        .attr("d", arcFinal3)
                        ;
        }
        
        function mouseout() {
          d3.select(this).select("path").transition()
              .duration(750)
                        .attr("d", arcFinal)
                        ;
        }
        
        function up(d, i) {
        
                    updateData(d.data.user_id, color(i));
                    lineChart(d.data.user_id, color(i));
        }
    }
});
   
}




//********************** PIE CHART ***********************************
function updateData(user_id, colorChosen) {
    // $('#barChart2').remove();
    $.ajax({
        url: "/get_user_chart_data2", //{{ url_for ('site.getdata') }}",
        type: 'POST',
        data: {user: user_id},
        dataType: 'json',
        success: function (jsonData) {

        $("#barChart").empty();
        var svgWidth = 600;
        var svgHeight = 300;

        var heightPad = 50;
        var widthPad = 50;

        var tooltip = d3.select("body").append("div").attr("class", "toolTip");

        var svg = d3.select("#barChart")
            .append("svg")
            .attr("width", svgWidth + (widthPad * 2))
            .attr("height", svgHeight + (heightPad * 2))
            .append("g")
            .attr("transform", "translate(" + widthPad + "," + heightPad + ")");


    //Set up scales
    var xScale = d3.scale.ordinal()
        .domain(jsonData.map(function(d) { return d.item; }))
        .rangeRoundBands([0, svgWidth], .4);

   var yScale = d3.scale.linear()
        .domain([0, d3.max(jsonData, function (d) { return d.amount; }) ])
        .range([svgHeight,0]);
    
        
   // Create bars
    svg.selectAll("rect")
        .data(jsonData)
        .enter().append("rect")
        .attr("x", function (d) { return xScale(d.item) + widthPad; })
        .attr("width", xScale.rangeBand()).attr("fill", colorChosen)
        .attr("y", function (d) { return yScale(d.amount); }).transition().duration(750)
        .attr("height", function (d) { return svgHeight - yScale(d.amount); })
        
        
    svg.selectAll("rect")
       .on('mouseover', function(d){ d3.select(this) .style('opacity', 0.4),
                    tooltip
                    .style("left", d3.event.pageX - 50 + "px")
                    .style("top", d3.event.pageY - 70 + "px")
                    .style("display", "inline-block")
                    .style('opacity', 0.9)
                    .html((d.item) + "<br>" + "$" + (d.amount));   })
        .on('mouseleave', function(d){  d3.select(this) .style('opacity', 1) , tooltip.style("display", "none")})
        .on('click', function(d) { console.log(d3.select(this)) })
        
    // Y axis
    var yAxis = d3.svg.axis()
        .scale(yScale)
        .orient("left");

    svg.append("g")
        .attr("class", "axis")
        .attr("transform", "translate(" + widthPad + ",0)")
        .call(yAxis)
     .append("text")
        .attr("transform", "rotate(-90)")
        .attr("y", -50)
        .style("text-anchor", "bottom")
        .style("text-size", 20)
        .text("Expenses");

    // X axis
    var xAxis = d3.svg.axis()
    .scale(xScale)
    .orient("bottom");

    svg.append("g")
        .attr("class", "axis")
        .attr("transform", "translate(" + widthPad + "," + svgHeight + ")")
        .call(xAxis)
        .append("text")
        .attr("x", svgWidth / 2 - widthPad)
        .attr("y", 50)
        .text("Categories");

        }
                
});
}



//********************** PIE CHART ***********************************
//line chart code

function lineChart(user_id, colorChosen){

// Set the dimensions of the canvas / graph
var margin = {top: 30, right: 20, bottom: 30, left: 50},
    width = 960 - margin.left - margin.right,
    height = 400 - margin.top - margin.bottom;

// Parse the date / time
var parseDate = d3.time.format("%Y-%m-%d %H:%M").parse; 
bisectDate = d3.bisector(function(d) { return d.date; }).left,
formatValue = d3.format(",.2f"),
formatCurrency = function(d) { return "$" + formatValue(d); };

$("#linechart").empty();
// Set the ranges
var x = d3.time.scale().range([0, width]);
var y = d3.scale.linear().range([height, 0]);

// Define the axes
var xAxis = d3.svg.axis().scale(x)
    .orient("bottom").ticks(5);

var yAxis = d3.svg.axis().scale(y)
    .orient("left").ticks(5);

// Define the line
var expenseLine = d3.svg.line()
    .x(function(d) { return x(d.date); })
    .y(function(d) { return y(d.amount); });
    
// Adds the svg canvas
var svg = d3.select("#linechart")
    .append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
    .append("g")
        .attr("transform", 
              "translate(" + margin.left + "," + margin.top + ")");

// Get the data
$.ajax({
    url: "/lineChart", //{{ url_for ('site.getdata') }}",
    type: 'POST',
    data: {user: user_id},
    dataType: 'json',
    success: function (jsonData) {
        jsonData.forEach(function(d) {
            d.date = parseDate(d.date);
            d.amount = +d.amount;
            d.name = d.name
            console.log(d.amount)
            console.log(d.name)
        });

    // Scale the range of the data
    x.domain(d3.extent(jsonData, function(d) { return d.date; }));
    y.domain([0, d3.max(jsonData, function(d) { return d.amount; })]); 

    // Nest the entries by symbol
    var dataNest = d3.nest()
        .key(function(d) {return d.name;})
        .entries(jsonData);


    // Loop through each symbol / key
    dataNest.forEach(function(d) {
        svg.append("path")
            .attr("class", "line")
            .style("stroke", function() { // Add dynamically
                return d.color = colorChosen; })
            .attr("d", expenseLine(d.values))
           
    });

   

    // Add the X Axis
    svg.append("g")
        .attr("class", "x axis")
        .attr("transform", "translate(0," + height + ")")
        .call(xAxis);

    // Add the Y Axis
    svg.append("g")
        .attr("class", "y axis")
        .call(yAxis);

        var focus = svg.append("g")
        .attr("class", "focus")
        .style("display", "none");
  
    focus.append("circle")
        .attr("r", 4.5);
  
    focus.append("text")
        .attr("x", 9)
        .attr("dy", ".35em");
  
    svg.append("rect")
        .attr("class", "overlay")
        .attr("width", width)
        .attr("height", height)
        .on("mouseover", function() { focus.style("display", null); })
        .on("mouseout", function() { focus.style("display", "none"); })
        .on("mousemove", mousemove);
  
    function mousemove() {
      var x0 = x.invert(d3.mouse(this)[0]),
          i = bisectDate(jsonData, x0, 1),
          d0 = jsonData[i - 1],
          d1 = jsonData[i],
          d = x0 - d0.date > d1.date - x0 ? d1 : d0;
      focus.attr("transform", "translate(" + x(d.date) + "," + y(d.amount) + ")");
      focus.select("text").text(formatCurrency(d.amount));
    }
    }

});
}
    

