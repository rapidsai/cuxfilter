//intialize a cuXfilter object for a dataset called predictions-v1 (arrow format), with cudf engine and useSessions=true at the url
var cuObj = new cuXfilter('predictions-v1','http://your-server-url:port','cudf',true,'arrow');
var bar1 = document.getElementById('bar1');
var bar2 = document.getElementById('bar2');

cuObj.init().then((status) => { 
    //load dimension 1
    dimension1 = cuObj.dimension(cuObj.schema[1]);

    //load dimension 2
    dimension2 = cuObj.dimension(cuObj.schema[5]);

    //wait for the dimension loading to finish before requesting for histogram by resolving the promises given below
    return Promise.all([dimension1.loadDimension(),dimension2.loadDimension()]);
}).then((error,message) => {
    //get histograms for dimension1 and dimension2
    dimension1.getHist(100);
    dimension2.getHist(100);
    init();
});

function init(){

    Plotly.newPlot(bar1, [{x: [], y: [], type: 'bar'}], {title: cuObj.schema[1]+' histogram', dragmode:'select',selectdirection:'h'}, {modeBarButtons: [[]]});
    
    Plotly.newPlot(bar2, [{x: [], y: [], type: 'bar'}], {title: cuObj.schema[5]+' histogram', dragmode:'select',selectdirection:'h'}, {modeBarButtons: [[]]});

    //plotly event when a range is selected for crossfilter
    bar1.on('plotly_selected', (eventData) => {
        if(eventData){ dimension1.resetThenFilter(eventData.range.x); }
    });

    //plotly event when a range is deselected by double clicking on the screen
    bar1.on('plotly_deselect', () => {
        dimension1.resetFilters();
    });

    //plotly event when a range is selected for crossfilter
    bar2.on('plotly_selected', (eventData) => {
        if(eventData){ dimension2.resetThenFilter(eventData.range.x); }
    });

    //plotly event when a range is deselected by double clicking on the screen
    bar2.on('plotly_deselect', () => {
        dimension2.resetFilters();
    });
}

//intialize eventlistener for the updateHistEvent, which listens for changes to histogram values for all bar charts in the current session
addEventListener('updateHistEvent', (e) => {        
    if(e.detail.column == cuObj.schema[1]){
        updateBar1()
    }else{
        updateBar2();
    }
});

//update bar chart 1 when updated values are received
function updateBar1(){
    Plotly.restyle(bar1,'x', [dimension1.histogram.X]);
    Plotly.restyle(bar1,'y', [dimension1.histogram.Y]);
};

//update bar chart 2 when updated values are received
function updateBar2(){
    Plotly.restyle(bar2,'x', [dimension2.histogram.X]);
    Plotly.restyle(bar2,'y', [dimension2.histogram.Y]);
};

//custom function which fires when the range slider value is updated firing a getHist method for the specific dimension, with update bin size
function updateBins(chart) {
    if(chart == 'bar1'){
        var x = document.getElementById("bar1_slider").value;
        dimension1.getHist(x);
    }
    else{
        var x = document.getElementById("bar2_slider").value;
        dimension2.getHist(x);
    }
}