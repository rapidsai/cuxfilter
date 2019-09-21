# cuXfilter-client.js

> A javascript(es6) client library that provides crossfilter functionality to create interactive vizualizations on big data(100M+ rows) right from the browser, using the power of cudf & numba on the backend.


### Table of Contents
- [Installation](#installation)
- [Import](#import)
- [Functions](#functions)
	1. [Load data](#1-load-data)
	2. [Get Data size](#2-get-data-size)
	3. [Get Data schema](#3-get-data-schema)
	4. [End session](#4-end-session)
	5. [Update Size Event](#5-update-size-event)
	6. [Connection Closed Event](#6-connection-closed-event)
- [Dimensions](#dimensions)
	1. [Get top n rows sorted as per dimension](#1-get-top-n-rows-sorted-as-per-dimension)
	2. [Get bottom n rows sorted as per dimension](#2-get-bottom-n-rows-sorted-as-per-dimension)
	3. [Get all rows sorted as per dimension](#3-get-all-rows-sorted-as-per-dimension)
	4. [Cumulative Filters: cuXfilter instance as per a condition (preserves previous filter requests)](#4-cumulative-filters-cuxfilter-instance-as-per-a-condition-preserves-previous-filter-requests)
	5. [Non-Cumulative Filters: cuXfilter instance as per a condition (resets all previous filters on the current dimension, and then applies new filter)](#5-non-cumulative-filters-cuxfilter-instance-as-per-a-condition-resets-all-previous-filters-on-the-current-dimension-and-then-applies-new-filter)
	6. [Dimension Filter Events](#6-dimension-filter-events)
	7. [Min value of dimension](#7-min-value-of-dimension)
	8. [Max value of dimension](#8-max-value-of-dimension)
	9. [Get Histogram for a dimension](#9-get-histogram-for-a-dimension)
	10. [Clear all filters for a dimension](#10-clear-all-filters-for-a-dimension)
	11. [Clear all filters for ALL dimensions](#11-clear-all-filters-for-all-dimensions)
- [Groups](#groups)
	1. [Get Top n rows of the group](#1-get-top-n-rows-of-the-group)
	2. [Get bottom n rows of the group](#2-get-bottom-n-rows-of-the-group)
	3. [Get all n rows of the group](#3-get-all-n-rows-of-the-group)
- [Multi-tab sessionless crossfiltering](#multi-tab-sessionless-crossfiltering)


## Installation

<pre>
git clone cuXfilter-repo
cd client_side/library_src
npm install
npm run build
</pre>

use ./dist/cuXfilter-client.js

Note: if cuXfilter-client.js is updated you must also rebuild the GTC demo from source.

## Import

1. React/Angular
<pre>import cuXfilter from "cuXfilter-client.js"; </pre>

2. html
<pre> < script type="text/javascript" src="cuXfilter-client.js">< / script > </pre>


## Functions

### 1. Load data
<pre>
Const myData = new cuXfilter(&#39;dataset-name-without-extension&#39;, 'http://url-of-server', engine, useSessions, load_type);  
</pre>

> 1. engine = 'cudf'/ 'pandas' (string) <br>
> 2. useSessions = true/false (boolean) -> setting this as false allows multi-tab cross filtering in chrome and firefox <br>
> 3. load_type = 'ipc'/'arrow' (string) -> default value is arrow. optional field

<pre>
myData.init();
//init also has an optional callback
myData.init().then((status) => {
        console.log(status);
});
</pre>

### 2. Get Data size
<pre>
myData.init().then((status) => {
        myData.size; //returns an integer
});
</pre>

### 3. Get Data schema
<pre>
myData.init().then((status) => {
	myData.schema; //returns an array of column names of the dataset
});

E.g: [&#39;sourceid&#39;, &#39;dstid&#39;, &#39;hod&#39;, &#39;mean_travel_time&#39;, &#39;standard_deviation_travel_time&#39;, &#39;geometric_mean_travel_time&#39;, &#39;geometric_standard_deviation_travel_time&#39;]
</pre>

### 4. End session

<pre>
myData.endSession().then((status)=>{}).catch((err)=>{});
</pre>

### 5. Update Size Event

To keep track of changes to these dataset size, an event listener is provided:

A. `updateSizeEvent`

<pre> addEventListener('updateSizeEvent', (e) => {
		console.log(myData.size);

		let your_size_variable = myData.size; //updated size
});
</pre>

### 6. Connection Closed Event

Since only one session is allowed per container(can have multiple datasets), a `connectionClosed` event is dispatched if a new session replaces the current session and can be handled in the following manner:

 <pre>
addEventListener('connectionClosed', (e) => {
		console.log(e.detail);
		// code to reset on page charts after a connection resets
});
 </pre>


##  Dimensions
> Dimensions are objects on top of the dataset that lets us reference a single column. This helps in getting rows from dataset sorted as per the current dimension, or getting a histogram for the dimension column. Groupby operations can also be performed on dimensions(More on that in the Groups sections) <br>


To use a dimension, we need to initialize it using the actual column name. Column names are present as an array format in the the `cuXfilter.schema` variable, which in the above case would be `myData.schema`:

<pre>
Const dimA = myData.dimension(myData.schema[0]);
//load the dimension (you only need to do the following once)
dimA.loadDimension().then((err,status) => {
	if(!err){
			console.log(status); 	// successfully loaded the dimension object on server-side
	}
});
</pre>

A Dimension has the following properties:

1. min (float)
2. max (float)
3. histogram (object)   // {"X":{...}, "Y":{...}}
4. value (object)           // {"column1":{...}, ...}
5. name (string)
6. parent_dataset (string)
7. filters (object)
8. childGroup (list of all groupbys loaded on top of this dimension)

The `dimension.histogram` and `dimension.value` properties change whenever any crossfilter functions are executed.

To keep track of changes to these two variables, two event listeners are provided:

> These are global event listeners, which are binded to the window DOM element, and need to be intiated only once and work on all dimensions for the given dataset.

A.  `updateHistEvent`

<pre> addEventListener('updateHistEvent', (e) => {
		console.log("event update ", e.detail.column);      
		// `e.detail.column` is actual column name in the dataset, which the `dimension.name` variable can be matched with to re-render only the dimension, whose histogram value changed
		if(dimA.name === e.detail.column){
			console.log(dimA.histogram);
			console.log('dimA histogram value updated in the background');
		}
});
</pre>

Functions that trigger the `updateHistEvent`:
1. [dimension.getHist(num_of_bins)](#8-get-histogram-for-a-dimension)
2. [dimension.filter()](#4-cumulative-filters-cuxfilter-instance-as-per-a-condition-preserves-previous-filter-requests)
3. [dimension.resetThenFilter()](#5-non-cumulative-filters-cuxfilter-instance-as-per-a-condition-resets-all-previous-filters-on-the-current-dimension-and-then-applies-new-filter)
4. [dimension.resetFilters()](#10-clear-all-filters-for-a-dimension)
5. [cuXfilter.resetAllFilters()](#11-clear-all-filters-for-all-dimensions)


B. `updateDimensionEvent`

<pre> addEventListener('updateDimensionEvent', (e) => {
		console.log("event update ", e.detail.column);      
		// `e.detail.column` is actual column name in the dataset, which the `dimension.name` variable can be matched with to re-render only the dimension, whose dimension value changed
		if(dimA.name === e.detail.column){
			console.log(dimA.value);
			console.log('dimA value updated in the background');
		}
});
</pre>

Functions that trigger the `updateDimensionEvent`:
1. [dimension.top(n_rows, columns[])](#1-get-top-n-rows-sorted-as-per-dimension)
2. [dimension.bottom(n_rows, columns[])](#2--get-bottom-n-rows-sorted-as-per-dimension)
3. [dimension.all(columns[])](#3-get-all-rows-sorted-as-per-dimension)
4. [dimension.filter()](#4-cumulative-filters-cuxfilter-instance-as-per-a-condition-preserves-previous-filter-requests)
5. [dimension.resetThenFilter()](#5-non-cumulative-filters-cuxfilter-instance-as-per-a-condition-resets-all-previous-filters-on-the-current-dimension-and-then-applies-new-filter)
6. [dimension.resetFilters()](#10-clear-all-filters-for-a-dimension)
7. [cuXfilter.resetAllFilters()](#11-clear-all-filters-for-all-dimensions)


### 1. Get top n rows sorted as per dimension
<pre>
dimA.top(n_rows,list_of_columns);
</pre>
> list_of_columns -> optional, if none, all columns are returned; else requested columns along with current dimension column are returned <br>

<pre>
e.g:-&gt; dimA.top(5)

parsedData value -&gt;

{
&quot;sourceid&quot;: [234.0, 234.0, 234.0, 1449.0],
&quot;dstid&quot;: [729.0, 1132.0, 2288.0, 729.0, 1132.0],
&quot;hod&quot;: [15.0, 15.0, 15.0, 15.0, 15.0],
&quot;mean_travel_time&quot;: [10578.169921875, 10531.169921875, 10481.8798828125, 10249.830078125, 10202.830078125],
&quot;standard_deviation_travel_time&quot;: [1514.469970703125, 1517.1300048828125, 1304.6600341796875, 1522.8199462890625, 1525.4599609375],
&quot;geometric_mean_travel_time&quot;: [10469.6201171875, 10421.73046875, 10398.7197265625, 10136.9501953125, 10089.01953125],
&quot;geometric_standard_deviation_travel_time&quot;: [1.149999976158142, 1.159999966621399, 1.1399999856948853, 1.159999966621399, 1.159999966621399]
}
</pre>


### 2.  Get bottom n rows sorted as per dimension

<pre>
dimA.bottom(n_rows, list_of_columns);
</pre>

> list_of_columns -> optional, if none, all columns are returned; else requested columns along with current dimension column are returned

<pre>
e.g:-&gt; dimA.bottom(5,['sourceid','hod']);
</pre>

### 3. Get all rows sorted as per dimension

<i> not recommended, as it would download the entire dataset to the browser, resulting in a crash</i>

<pre>
dimA.all(list_of_columns);
</pre>
> list_of_columns -> optional, if none, all columns are returned; else requested columns along with current dimension column are returned

<pre>
e.g:-&gt; dimA.all(['sourceid','hod']);
</pre>


### 4. Cumulative Filters: cuXfilter instance as per a condition (preserves previous filter requests)
<pre>
dimA.filter(comparison_operator, value);
</pre>

 > 1. Comparison_operator: >, < , ==, !=, %n==, %n!= <br>
 > 2. value: Int/float <br>

<pre>
E.g:

1. mean_travel_time_dimension.filter('>','9999'); // selects mean_travel_time_dimension whose value is greater than 9999
2. mean_travel_time_dimension.filter([100, 200]); // selects mean_travel_time_dimension whose value is between 100 and 200
3. mean_travel_time_dimension.filter(120); // selects mean_travel_time_dimension whose value equals 120
4. mean_travel_time_dimension.filter('%2!=',0); // selects mean_travel_time_dimension whose value is odd
5. mean_travel_time_dimension.filter(null); // selects all mean_travel_time_dimension -> equivalent to resetFilters();
6. mean_travel_time_dimension.filter('==',[9999,200,6745]); //selects all mean_travel_time_dimension where value matches <b>ANY ONE</b> of the values in the given array
</pre>

### 5. Non-Cumulative Filters: cuXfilter instance as per a condition (resets all previous filters on the current dimension, and then applies new filter)
<pre>
dimA.resetThenFilter(comparison_operator, value);
</pre>

 > 1. Comparison_operator: >, < , ==, !=, %n==, %n!= <br>
 > 2. value: Int/float <br>

<pre>
E.g:

1. mean_travel_time_dimension.resetThenFilter('>','9999'); // resets previous filters and selects mean_travel_time_dimension whose value is greater than 9999
2. mean_travel_time_dimension.resetThenFilter([100, 200]); // resets previous filters and selects mean_travel_time_dimension whose value is between 100 and 200
3. mean_travel_time_dimension.resetThenFilter(120); // resets previous filters and selects mean_travel_time_dimension whose value equals 120
4. mean_travel_time_dimension.resetThenFilter('%2!=',0); // resets previous filters and selects mean_travel_time_dimension whose value is odd
5. mean_travel_time_dimension.resetThenFilter(null); // resets previous filters and selects all mean_travel_time_dimension -> equivalent to resetFilters();
6. mean_travel_time_dimension.resetThenFilter('==',[9999,200,6745]); //resets previous filters and selects all mean_travel_time_dimension where value matches <b>ANY ONE</b> of the values in the given array
</pre>


### 6. Dimension filter events

Whenever a `dimension.filter` or `dimension.resetThenFilter` request is made, the `allUpdatesComplete` event is fired when all the groups and dimensions changed due to the filter are done updating.

A. `allUpdatesComplete`

> this can be useful if you want to wait for changes to reflect on your page after a filter, before allowing the user to apply another filter, to prevent GPU memory spike.

E.g:

<pre>
dimension.filter(120);
blockInteractionsOnPage();

addEventListener('allUpdatesComplete', (e) => {
	unblockInteractionsOnPage();
});
</pre>


### 7. Min value of dimension
> returns the min value for that specific dimension; Updated on execution of one of the crossfilter functions

<pre>
dimA.min;
</pre>


### 8. Max value of dimension
 > returns the max value for that specific dimension; Updated on execution of one of the crossfilter functions

<pre>
dimA.max;
</pre>


### 9. Get Histogram for a dimension

<pre>
dimA.getHist();

e.g: -&gt; mean_travel_time_dimension.getHist(10);

Result :  
{
&quot;X&quot;: [&quot;6.380000114440918&quot;, &quot;1063.559004020691&quot;, &quot;2120.738007926941&quot;, &quot;3177.9170118331913&quot;, &quot;4235.096015739441&quot;, &quot;5292.275019645691&quot;, &quot;6349.454023551942&quot;, &quot;7406.6330274581915&quot;, &quot;8463.812031364441&quot;, &quot;10578.169921875&quot;],
&quot;Y&quot;: [&quot;3601083&quot;, &quot;4572333&quot;, &quot;1645723&quot;, &quot;349814&quot;, &quot;60184&quot;, &quot;9699&quot;, &quot;2229&quot;, &quot;395&quot;, &quot;96&quot;, &quot;14&quot;]
}

</pre>


### 10. Clear all filters for a dimension

<pre>
dimA.resetFilters()
</pre>
>num_of_rows_left: returns a number representing number of rows in the dataset after removing dimA filters


### 11. Clear all filters for ALL dimensions

<pre>
myData.resetAllFilters();
</pre>

> myData: cuXfilter() object


## Groups
> Groups are objects on top of the dimension that lets us execute cudf groupby function with customizable aggregations. <b> Applying filters on a dimension do not affect the groups associated with it, and only affect the groups associated with other dimensions.</b> <br>

To use a group, we need to create it on top of a dimension.

<pre>
const g = dimension.group(aggregate);
g.loadGroup().then((status)=>{}).catch((err)=>{})
</pre>

> aggregate(optional): {object of aggregate functions} <br>
> Available functions: <b> sum, count, min, max, std, mean, sum_of_squares </b> <br>

The default value of aggregate is {'current_dimension': ['mean']}
<pre>
e.g:->
const agg_obj = {
	'mean_travel_time': ['sum','count', 'std'],
	'column_name_2': ['min']
}
const g = hod_dimension.group(agg_obj);
g.loadGroup().then((status)=>{}).catch((err)=>{})

OR

const g = hod_dimension.group();
g.loadGroup().then((status)=>{}).catch((err)=>{})

</pre>

A group object has the following properties:

1. name (string)
2. parent_dataset (string)
3. agg (object)   // {"column_1":[ 'agg_func1', 'agg_func2', ...], "column2":{...}}
4. value (object)           // {"column1_agg_func1":{...}, ...}

The `group.value` and `group.size` properties change whenever any crossfilter functions are executed.

To keep track of changes to these two variables, an event listeners are provided:

> These are global event listeners, which are binded to the window DOM element, and need to be intiated only once and work on all groups for all the dimensions for the given dataset.

A.  `updateGroupEvent`

<pre> addEventListener('updateGroupEvent', (e) => {
		console.log("event update ", e.detail.column, e.detail.aggregate);      
		// `e.detail.column` is actual column name in the dataset, which the `group.name` variable can be matched with to re-render only the dimension, whose value changed
		if(group.name === e.detail.column && group.agg == e.detail.aggregate){
			console.log(group.value, group.size);
			console.log('group value updated in the background');
		}
});
</pre>

Functions that trigger the `updateGroupEvent`:
1. [group.top(n_rows, sort_by_column)](#1-get-top-n-rows-of-the-group)
2. [group.bottom(n_rows, sort_by_column)](#2-get-bottom-n-rows-of-the-group)
3. [group.all()](#3-get-all-n-rows-of-the-group)
4. [dimension.filter()](#4-cumulative-filters-cuxfilter-instance-as-per-a-condition-preserves-previous-filter-requests)
5. [dimension.resetThenFilter()](#5-non-cumulative-filters-cuxfilter-instance-as-per-a-condition-resets-all-previous-filters-on-the-current-dimension-and-then-applies-new-filter)
6. [dimension.resetFilters()](#10-clear-all-filters-for-a-dimension)
7. [cuXfilter.resetAllFilters()](#11-clear-all-filters-for-all-dimensions)

### 1. Get Top n rows of the group
> Returns the top n rows of the group sorted by the descending order of value <br>
<pre>
g.top(num_of_rows=10,sort_by_column)
</pre>
>	1. num_if_rows(optional): Integer (default value = 10) <br>
>	2. sort_by_column(optional): column_name+"_"+agg_function  <br>
			(default value = firstColumn and first agg function in the aggregate object provided while creating the group)

<pre>
e.g:->
1.
	const agg_obj = {
		'hod':['count']
	}
	const g = hod_dimension.group(agg_obj);
	g.loadGroup().then((status)=>{ //make sure group is loaded before calling top. You only need to load the group.
		g.top(24, 'hod_count');
	});

 //updates the g.value variable, and emits the `updateGroupEvent` event

`g.value`:

{"hod": [19, 18, 17, 16, 15, 20, 14, 21, 10, 9, 12, 11, 13, 22, 8, 7, 23, 0, 6, 1, 2, 5, 3],
"count_hod": [487377.0, 487348.0, 485483.0, 483019.0, 479681.0, 478943.0, 476477.0, 476329.0, 475103.0, 470711.0, 469911.0, 469267.0, 468466.0, 461968.0, 454894.0, 433271.0, 424425.0, 381642.0, 372519.0, 349338.0, 304540.0, 302475.0, 274982.0]}

2.
	const agg_obj = {
		'mean_travel_time': ['sum','count', 'std']
		}
	let g = hod_dimension.group(agg_obj);
	g.loadGroup().then((status)=>{   //make sure group is loaded before calling top. You only need to load the group. once
		g.top(24, 'mean_travel_time_count');
	});

`g.value`:

{"hod": [19, 18, 17, 16, 15, 20, 14, 21, 10, 9, 12, 11, 13, 22, 8, 7, 23, 0, 6, 1, 2, 5, 3],
"mean_travel_time_sum": [735853094.06, 828787561.3599999, 927465638.5, 914655524.0500001, 856192499.8499999, 675426962.64, 792288618.48, 655275672.3100001, 709391672.56, 731228575.8699999, 704177415.62, 694722513.09, 718975013.7, 612128111.6800001, 760211029.6199999, 724063042.5000001, 530266475.59999996, 451331445.65, 527771759.35, 404303020.34999996, 328403132.74, 357328868.86, 293221760.27],
"count_mean_travel_time": [487377.0, 487348.0, 485483.0, 483019.0, 479681.0, 478943.0, 476477.0, 476329.0, 475103.0, 470711.0, 469911.0, 469267.0, 468466.0, 461968.0, 454894.0, 433271.0, 424425.0, 381642.0, 372519.0, 349338.0, 304540.0, 302475.0, 274982.0],
"std_mean_travel_time": [771.078363087773, 857.5915846598338, 1012.8468928821409, 1066.7255469466172, 998.2851407808366, 721.9829221151624, 910.5177036214152, 701.3402122945868, 785.1126356461986, 815.1537911630599, 782.0238233898274, 780.1713432950849, 819.9130816683466, 666.1650694739816, 888.0069238408861, 954.6924313225265, 647.2090044045242, 636.6144405380031, 842.6703223999089, 640.6810597885919, 601.9580064100818, 697.783428367376, 602.9960825330071]}

</pre>

### 2. Get bottom n rows of the group
> Similar to group.top(). Returns the top n rows of the group sorted by the ascending order of value <br>

<pre>
g.bottom(num_of_rows=10,sort_by_column);
</pre>
>	1. num_of_rows(optional): Integer (default value = 10)<br>
>	2. sort_by_column(optional): column_name+"_"+agg_function <br>
			(default value = firstColumn and first agg function in the aggregate object provided while creating the group)

<pre>
e.g:->
let agg_obj = {
	'hod':['count']
}
const g = hod_dimension.group(agg_obj);
g.loadGroup().then((status)=>{
	//make sure group is loaded before calling top. You only need to load the group.
		g.top(24, 'hod_count');
	});

//updates the g.value variable, and emits the `updateGroupEvent` event

`g.value`:
{"hod": [4, 3, 5, 2, 1, 6, 0, 23, 7, 8, 22, 13, 11, 12, 9, 10, 21, 14, 20, 15, 16, 17, 18],
"count_hod": [273401.0, 274982.0, 302475.0, 304540.0, 349338.0, 372519.0, 381642.0, 424425.0, 433271.0, 454894.0, 461968.0, 468466.0, 469267.0, 469911.0, 470711.0, 475103.0, 476329.0, 476477.0, 478943.0, 479681.0, 483019.0, 485483.0, 487348.0]}
</pre>

### 3. Get all n rows of the group
> Returns entire group in ascending natural order by key. <br>

<pre>
const g = hod_dimension.group('count');
g.loadGroup().then((status)=>{ //make sure group is loaded before calling top. You only need to load the group.
	g.all();
})

`g.value`:

{"hod": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23],
"count_hod": [381642.0, 349338.0, 304540.0, 274982.0, 273401.0, 302475.0, 372519.0, 433271.0, 454894.0, 470711.0, 475103.0, 469267.0, 469911.0, 468466.0, 476477.0, 479681.0, 483019.0, 485483.0, 487348.0, 487377.0, 478943.0, 476329.0, 461968.0, 424425.0]}
</pre>

## Multi-tab sessionless crossfiltering

<b> Set useSessions=false in order to get this working. </b>
