var fs = require("fs"); 

let a = { 'numpy with csv for 100M dataset': [ 15.2367424028, 17.41172925025, 17.467818289550003 ],
  'numpy with csv for 10M dataset': [ 2.3968292698, 2.67535527915, 2.6849636275999997 ],
  'numpy with csv for 1M dataset': [ 1.1879779898, 1.304066218, 1.2251368859 ],
  'numba with csv for 100M dataset': [ 14.542829555550004, 16.52939353445, 16.526655236049997 ],
  'numba with csv for 10M dataset': [ 2.3145492323499997, 3.1175659923, 3.1336545377 ],
  'numba with csv for 1M dataset': [ 1.15775656405, 1.8913221543000005, 1.90071265615 ],
  'numpy with arrow for 100M dataset':[ 2.4641018850000003, 4.3246479651000005, 4.364675504350002 ],
  'numpy with arrow for 10M dataset': [ 1.0522198108, 1.3530186463, 1.30614039795 ],
  'numpy with arrow for 1M dataset': [ 0.9176073012499998, 0.98609540405, 0.9737122964999999 ],
  'numba with arrow for 100M dataset': [ 2.2610973432499994, 3.7905026022, 3.7740573673 ],
  'numba with arrow for 10M dataset': [ 1.06925477985, 1.8661746722999997, 1.8732099938000002 ],
  'numba with arrow for 1M dataset': [ 0.9386964286499999, 1.7017912581, 1.6808607904500001 ] }

function logBenchmarks(final_results){
  var filename = String("Benchmark-"+new Date().toISOString())+".csv";
  var stream = fs.createWriteStream(filename, {flags:'a+'});
  //stream.write("logged on "+new Date().toISOString()+"\n");
  stream.write(",IngestData+ReadSchema,IngestData+HistogramA,IngestData+HistogramB \n");
  for(var key in final_results){
    stream.write(key+",");
    stream.write(a[key]+ "\n");
  }
}

logBenchmarks(a);