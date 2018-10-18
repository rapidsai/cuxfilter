# Usage

<b>helper_scripts.py</b> provides 3 types of functions:

## 1. 'csv_to_arrow':

### Usage: saves the file at the same location with '.arrow' extension
<pre>
  python helper_scripts --fn='csv_to_arrow' --source='../source/location/file.csv'
</pre>

## 2. 'arrow_to_csv':

### Usage: saves the file at the same location with '.csv' extension
<pre>
  python helper_scripts --fn='arrow_to_csv' --source='../source/location/file.arrow'
</pre>

## 3. 'generate_random_dataset':

### Usage: generates random dataset and saves it in specified format
<pre>
  python helper_scripts --fn='generate_random_dataset' --num_rows=(int - (default=1000)) --num_columns=(int - (default=1))  --type='arrow/csv (default=arrow)' --range_min=(float - (default=0.0)) --range_max==(float - (default=1000.0)) --destination='/destination/folder/ - (default= './')'
</pre>
