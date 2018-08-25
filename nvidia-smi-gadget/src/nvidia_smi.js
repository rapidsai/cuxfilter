const exec = require('child_process').exec;
const xml  = require('xml2js').parseString;

module.exports = function(){
  return new Promise((resolve,reject) => {

      // shell out
      exec('nvidia-smi -i 0 -q -x', function(err, stdout, stderr) {

        // handle errors
        if (err) {
          return reject(err);
        }
        if (stderr) {
          return reject(stderr);
        }

        // XML parser options
        const options = {
          explicitArray : false,
          trim          : true,
        };

        // restructure the XML into json
        xml(stdout, options, function (err, data) {

          // handle errors
          if (err) {
            return reject(err);
          }

          data = data['nvidia_smi_log']['gpu']['fb_memory_usage']
          //get usage stats
          let usage = data['used']+"/"+data['total']
          // return the data
          return resolve(usage);
        });
      });

  });
}
