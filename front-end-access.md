# PyCrossfilter library - serverside crossfilter library for the browser.

Uses numba and pygdf on the server side. 


To see how to use -> check dist/index.html

## Functions: server-side crossfilter:



<pre># Dataset -> columns ‘A’, ‘B’
var myData = new pycrossfilter('uber-dataset', 'http://url-of-server);
myData.init(); // loads data in gpu mem on server
myData.size; // precomputed size

Var d = myData.setDimension(‘A’)
</pre>

## Current status:

| **Pycrossfilter object Functions** | **Description** | **Status** |
| --- | --- | --- |
| myData.schema | Returns the schema of the dataset | Implemented |



Dimension functions use Pygdf on the backend:

| **Dimension Functions** | **Description** | **Status** |
| --- | --- | --- |
| dimension.top(n) | returns top n rows of the entire dataset, sorted in descending order as per dimension | Implemented |
| dimension.bottom(n) |   | Implemented |
| var condition = &gt;/&lt;/=var value = (float)[num_rows] -&gt; optional dimension.filter(condition, value, [num_rows])   | Returns rows of the entire dataset as per the filter | Implemented |
| dimension.min() | Executes dimension.bottom(1) | Implemented |
| dimension.max() | Executes dimension.top(1) | Implemented |
| dimension.group(column, aggregate_type); | Performs pygdf groupby functions on the serverside and returns the results | Implemented |

## Installation

<pre>npm i pycrossfilter </pre>

## Usage

### **1.** Load data:
<pre>
Const myData = new pycrossfilter(&#39;uber-dataset&#39;, 'http://url-of-server');
myData.init();
//init also has an optional callback
myData.init(function(status){
        console.log(status);
});
</pre>

### **2.** Get Data size:
<pre>
myData.size; //returns an integer
</pre>

### **3.** Get Data schema:
<pre>
myData.schema; //returns an array of column names of the dataset

E.g: [&#39;sourceid&#39;, &#39;dstid&#39;, &#39;hod&#39;, &#39;mean_travel_time&#39;, &#39;standard_deviation_travel_time&#39;, &#39;geometric_mean_travel_time&#39;, &#39;geometric_standard_deviation_travel_time&#39;]
</pre>

### **4.** End session:

<pre>
myData.endSession();
</pre>

### **5.** Create Dimension:

<pre>
Const dimA = myData.dimension(&#39;column_name&#39;);
</pre>

### **Dimension Functions:**

### **6.** Get top n rows sorted as per dimension:
<pre>
dimA.top(n_rows, [optional_callback]);

e.g:-&gt; dimA.top(5, function(data){
                parsedData = JSON.parse(data);
});

parsedData value -&gt;

{	&quot;sourceid&quot;: [234.0, 234.0, 234.0, 1449.0],
	&quot;dstid&quot;: [729.0, 1132.0, 2288.0, 729.0, 1132.0],
	&quot;hod&quot;: [15.0, 15.0, 15.0, 15.0, 15.0],
	&quot;mean_travel_time&quot;: [10578.169921875, 10531.169921875, 10481.8798828125, 10249.830078125, 10202.830078125],
	&quot;standard_deviation_travel_time&quot;: [1514.469970703125, 1517.1300048828125, 1304.6600341796875, 1522.8199462890625, 1525.4599609375],
	&quot;geometric_mean_travel_time&quot;: [10469.6201171875, 10421.73046875, 10398.7197265625, 10136.9501953125, 10089.01953125],
	&quot;geometric_standard_deviation_travel_time&quot;: [1.149999976158142, 1.159999966621399, 1.1399999856948853, 1.159999966621399, 1.159999966621399]}
</pre>


### **7.** Get bottom n rows sorted as per dimension

<pre>
dimA.bottom(n_rows, [optional_callback]);

e.g:-&gt; dimA.bottom(5, function(data){
                parsedData = JSON.parse(data);
});
</pre>


### **8.** Filter pycrossfilter instance as per a condition:
<pre>
dimA.filter(comparison_operator, value, [optional_callback]);

 > Comparison_operator: >, < , ==, !=, %n==, %n!=
 > value: Int/float
 > Optional_callback: returns the remaining number of rows in the dataset after filtering_

    E.g: 
  
    1. mean_travel_time_dimension.filter('>','9999'); // selects mean_travel_time_dimension whose value is greater than 9999
    2. mean_travel_time_dimension.filter([100, 200]); // selects mean_travel_time_dimension whose value is between 100 and 200
    3. mean_travel_time_dimension.filter(120); // selects mean_travel_time_dimension whose value equals 120
    4. mean_travel_time_dimension.filter('%2!=',0); // selects mean_travel_time_dimension whose value is odd
    5. mean_travel_time_dimension.filter(null); // selects all mean_travel_time_dimension -> equivalent to filterAll();

    You can check -> myData.size
            after the filter, it will show the updated number of rows left.
</pre>

### **9.** Min value of dimension
<pre>
dimA.min; 
 -&gt; returns the min value for that specific dimension
</pre>

### **10.** Max value of dimension
<pre>
dimA.max; 
 -&gt; returns the min value for that specific dimension
</pre>


### **11.** Get Histogram for a dimension

<pre>
dimA.getHist([optional_callback]);

e.g: -&gt; mean_travel_time_dimension.getHist(10, functions(data){
                parsedData = JSON.parse(data);
                parsedData[&#39;X&#39;], parsedData[&#39;Y&#39;];
});


Result :  {
&quot;X&quot;: [&quot;6.380000114440918&quot;, &quot;1063.559004020691&quot;, &quot;2120.738007926941&quot;, &quot;3177.9170118331913&quot;, &quot;4235.096015739441&quot;, &quot;5292.275019645691&quot;, &quot;6349.454023551942&quot;, &quot;7406.6330274581915&quot;, &quot;8463.812031364441&quot;, &quot;10578.169921875&quot;],
&quot;Y&quot;: [&quot;3601083&quot;, &quot;4572333&quot;, &quot;1645723&quot;, &quot;349814&quot;, &quot;60184&quot;, &quot;9699&quot;, &quot;2229&quot;, &quot;395&quot;, &quot;96&quot;, &quot;14&quot;]
}

</pre>


### **12.** Clear all filters for a dimension

<pre>
dimA.filterAll([optional_parameter]);

Optional_paramter> returns a number representing number of rows in the dataset after removing dimA filters
</pre>

### Group functions

### **13.** Create group
These groups change as per the filters on the other dimension. Current dimension filters do not affect the group in anyway.

<pre>
const g = dimension.group(type);
	<i>dimension>dimension > data.dimension() object;
	type > 'count', 'mean', 'median', 'sum', 'std', 'min', 'max'
	</i>
e.g:->
const g = hod_dimension.group('count');
</pre>

### 14. group.size
Returns the current size of the group(number of rows). Updated automatically on every filter request on other dimensions.

<pre>
const g = hod_dimension.group('count');
let size_g = 0;
g.size(function(size){
	size_g = size;
});;
</pre>

### 15. Get Top n rows of the group
Returns the top n rows of the group sorted by the descending order of value
<pre>
g.top(num_of_rows=10, callback);
	<i> callback > result rows</i>
	<i>num_if_rows: Integer (default value = 10)</i>

e.g:->
const g = hod_dimension.group('count');
g.top(24, function(data){
	data = JSON.parse(data);
});

parsed data:
{"hod": [19, 18, 17, 16, 15, 20, 14, 21, 10, 9, 12, 11, 13, 22, 8, 7, 23, 0, 6, 1, 2, 5, 3], 
"hod_count": [487377.0, 487348.0, 485483.0, 483019.0, 479681.0, 478943.0, 476477.0, 476329.0, 475103.0, 470711.0, 469911.0, 469267.0, 468466.0, 461968.0, 454894.0, 433271.0, 424425.0, 381642.0, 372519.0, 349338.0, 304540.0, 302475.0, 274982.0]}

</pre>

### 16. Get bottom n rows of the group
Similar to group.top(). Returns the top n rows of the group sorted by the ascending order of value

<pre>
g.top(num_of_rows=10, callback);
	<i> callback > result rows</i>
	<i>num_if_rows: Integer (default value = 10)</i>

e.g:->
const g = hod_dimension.group('count');
g.bottom(24, function(data){
	data = JSON.parse(data);
});

parsed data:
{"hod": [4, 3, 5, 2, 1, 6, 0, 23, 7, 8, 22, 13, 11, 12, 9, 10, 21, 14, 20, 15, 16, 17, 18],
"hod_count": [273401.0, 274982.0, 302475.0, 304540.0, 349338.0, 372519.0, 381642.0, 424425.0, 433271.0, 454894.0, 461968.0, 468466.0, 469267.0, 469911.0, 470711.0, 475103.0, 476329.0, 476477.0, 478943.0, 479681.0, 483019.0, 485483.0, 487348.0]}
</pre>

### 17. group.all()
Returns entire group in ascending natural order by key.

<pre>
const g = hod_dimension.group('count');
g.all(function(data){
	data = JSON.parse(data);
});

parsed data:
{"hod": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23], 
"hod_count": [381642.0, 349338.0, 304540.0, 274982.0, 273401.0, 302475.0, 372519.0, 433271.0, 454894.0, 470711.0, 475103.0, 469267.0, 469911.0, 468466.0, 476477.0, 479681.0, 483019.0, 485483.0, 487348.0, 487377.0, 478943.0, 476329.0, 461968.0, 424425.0]}
</pre>