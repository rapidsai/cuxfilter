var apiBenchmark = require('api-benchmark');
var fs = require("fs"); 

var service = {
  server1: 'http://localhost:3000/calc/'
};

var datasets = [100000,10000,1000]
var types = ['ReadSchema','Histogram-A','Histogram-B']
var processing_types = ['numpy','numba']
var load_types = ['csv','arrow']

var routes = {}
var temp_form = {}
var temp_route_name = ''
load_types.forEach(function(load_type){
      processing_types.forEach(function(processing){
          datasets.forEach(function(datasetSize){
              types.forEach(function(type){
                  if(type.includes("Histogram")){
                    temp_form = {
                      file: "data-"+datasetSize+"k",
                      processing:processing,
                      load_type:load_type,
                      col: type.split("-")[1]
                    }
                    temp_route_name = processing+" with "+load_type+" for "+datasetSize/1000+"M dataset -"+type;
                    routes[temp_route_name] = {
                          method: 'post',
                          route: 'getHist',
                          data: temp_form 
                    };
                  }
                  else{
                    temp_form = {
                      file: "data-"+datasetSize+"k",
                      processing:processing,
                      load_type:load_type
                    }
                    temp_route_name = processing+" with "+load_type+" for "+datasetSize/1000+"M dataset -"+type;
                    routes[temp_route_name] = {
                          method: 'post',
                          route: 'getColumns',
                          data: temp_form 
                    };
                  }
              });
          });  
    });
});
// console.log(routes);

//temp_route: routes for testing if the script is executing properly
var temp_route = {
  
  '1-col': { method: 'post',
  route: 'getColumns',
  data:{ file: 'data-1000k',
     processing: 'numpy',
     load_type: 'csv'
      } 
  },
  '1-hist':{
    method: 'post',
    route: 'getHist',
    data:{ file: 'data-1000k',
     processing: 'numpy',
     load_type: 'csv',
     col: 'A' }
  }
};
var options = {
  maxTime:10000,
  minSamples: 20
}

function logBenchmarks(final_results){
  var filename = "Benchmark-"+new Date().toDateString().replace(/ /g,'')+".csv";
  var stream = fs.createWriteStream(filename, {flags:'a'});
  stream.on('open', function(fd){
    stream.write(",IngestData+ReadSchema,IngestData+HistogramA,IngestData+HistogramB \n");
    for(var key in final_results){
      stream.write(key+",");
      stream.write(final_results[key]+ "\n");
    }
  });
  
}

apiBenchmark.measure(service, routes , options, function(err, results) {
  apiBenchmark.getHtml(results, function(error, html) {
    var htmlfilename = "Benchmark-"+new Date().toDateString().replace(/ /g,'')+".html";
    fs.writeFileSync(htmlfilename,html);
  });
  var res = results.server1;
  var final_res = {};
  var key,val = '';
  for (var prop in res){
      console.log(prop+":"+res[prop].stats.mean);
      key = prop.split("-")[0].trim();
      val = res[prop].stats.mean;
      if(key in final_res){
        final_res[key].push(val);
      }else{
        final_res[key] = [val];
      }
    }
  console.log(final_res);
  logBenchmarks(final_res);
  });