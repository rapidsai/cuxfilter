# views.py

#import required libraries
from flask import render_template, jsonify, request
import logging, json, time
from app import app
from app.utilities.cuXfilter_utils import cuXfilter_utils as cudf
from app.utilities.pandas_utils import pandas_utils as pandas
from sanic.response import text

#global dictionaries to keep track of different user sessions. end_connection for a user_session results in the dictionary key-value pair being popped
user_sessions = {}
user_sessions_pandas = {}

@app.route('/')
async def index(request):
    '''
        description:
            if no route is provided, serve index.html
    '''
    return render_template("index.html")

async def init_session(session_id):
    '''
        description:
            initialize the session for cudf dataframe object in the user_sessions global dictionary
        input:
            1. session_id
        No output
    '''
    user_sessions[session_id] = cudf()

async def init_session_pandas(session_id):
    '''
        description:
            initialize the session for pandas dataframe object in the user_sessions_pandas global dictionary
        input:
            1. session_id
        No output
    '''
    user_sessions_pandas[session_id] = pandas()


@app.route('/init_connection', methods=['GET'])
async def init_connection(request):
    '''
        description:
            initialize connection with node client for this user-dataset combination
        Get parameters:
            1. session_id (string)
            2. dataset (string)
            3. engine (cudf/pandas)
        Response:
            status -> successfully initialized/ error
    '''
    # print(request.args)
    #get basic get parameters
    start_time,session_id,dataset_name,key, engine = await parse_basic_get_parameters(request.args)

    print("init connection for "+session_id)

    if engine == 'cudf':
        if key not in user_sessions:
            await init_session(key)
            response = "initialized successfully"
        else:
            response = "connection already intialized"
    else:
        if key not in user_sessions_pandas:
            await init_session_pandas(key)
            response = "initialized successfully"
        else:
            response = "connection already intialized"
    return text(await append_time_to_response(response,start_time, key, engine))


@app.route('/read_data', methods=['GET'])
async def read_data(request):
    '''
        description:
            read arrow file from disk to gpu memory
        Get parameters:
            1. session_id (string)
            2. dataset (string)
            3. engine (cudf/pandas)
            4. load_type (arrow/ipc)
        Response:
            status -> data read successfully / error
    '''
    #get basic get parameters
    start_time,session_id,dataset_name,key, engine = await parse_basic_get_parameters(request.args)

    load_type = request.args.get('load_type')

    # DEBUG: start
    print("read data for "+dataset_name+" and sessId: "+session_id+load_type)
    # DEBUG: end

    if engine == 'cudf':
        #start function execution
        response = user_sessions[key].read_data(load_type,dataset_name)
        print("read data response = "+str(response))
        if 'out of memory' in response or 'thrust::system::system_error' in response:
            user_sessions.pop(session_id+dataset_name,None)
            print('\n\nout of memory error')
        else:
            user_sessions[key].numba_jit_warm_func()
        #end function execution
    else:
        #start function execution
        response = user_sessions_pandas[key].read_data('arrow',dataset_name)
        #end function execution

    #return response
    return text(await append_time_to_response(response,start_time, key, engine))

@app.route('/get_schema', methods=['GET'])
async def get_schema(request):
    '''
        description:
            get schema of the dataset
        Get parameters:
            1. session_id (string)
            2. dataset (string)
            3. engine (cudf/pandas)
        Response:
            comma separated column names
    '''
    #get basic get parameters
    start_time,session_id,dataset_name,key, engine = await parse_basic_get_parameters(request.args)

    # DEBUG: start
    print("get schema of"+dataset_name+" for "+session_id)
    # DEBUG: end

    if engine == 'cudf':
        #start function execution
        response = user_sessions[key].get_columns()
        if 'out of memory' in response or 'thrust::system::system_error' in response:
            user_sessions.pop(session_id+dataset_name,None)
            print('\n\nout of memory error')
        #end function execution
    else:
        #start function execution
        response = user_sessions_pandas[key].get_columns()
        #end function execution

    #return response
    return text(await append_time_to_response(response,start_time, key, engine))


@app.route('/get_size', methods=['GET'])
async def get_size(request):
    '''
        description:
            get size of the dataset
        Get parameters:
            1. session_id (string)
            2. dataset (string)
            3. engine (cudf/pandas)
        Response:
            "(num_rows, num_columns)"
    '''
    #get basic get parameters
    start_time,session_id,dataset_name,key, engine = await parse_basic_get_parameters(request.args)

    # DEBUG: start
    print("get size of"+dataset_name+" for "+session_id)
    # DEBUG: end

    if engine == 'cudf':
        #start function execution
        response = user_sessions[key].get_size()
        if 'out of memory' in response or 'thrust::system::system_error' in response:
            user_sessions.pop(session_id+dataset_name,None)
            print('\n\nout of memory error')
        #end function execution
    else:
        #start function execution
        response = user_sessions_pandas[key].get_size()
        #end function execution

    #return response
    return text(await append_time_to_response(response,start_time, key, engine))


@app.route('/groupby_load', methods=['GET'])
async def groupby_load(request):
    '''
        description:
            load groupby operation for dimension as per the given groupby_agg
        Get parameters:
            1. session_id (string)
            2. dataset (string)
            3. dimension_name (string)
            4. groupby_agg (JSON stringified object)
            5. engine (cudf/pandas)
        Response:
            number_of_rows_left
    '''
    #get basic get parameters
    start_time,session_id,dataset_name,key, engine = await parse_basic_get_parameters(request.args)

    #getting remaining parameters
    dimension_name = request.args.get('dimension_name')
    groupby_agg = json.loads(request.args.get('groupby_agg'))

    # DEBUG: start
    print("groupby load of "+dataset_name+" for dimension_name: "+dimension_name+" for "+session_id)
    # DEBUG: end

    if engine == 'cudf':
        #start function execution
        groupby_agg_key = ':'.join(list(groupby_agg.keys())+list(groupby_agg.values())[0])
        response = user_sessions[key].groupby_load(dimension_name, groupby_agg, groupby_agg_key)
        if 'out of memory' in response or 'thrust::system::system_error' in response:
            user_sessions.pop(session_id+dataset_name,None)
            print('\n\nout of memory error')
        #end function execution
    else:
        #start function execution
        groupby_agg_key = ':'.join(list(groupby_agg.keys())+list(groupby_agg.values())[0])
        response = user_sessions_pandas[key].groupby_load(dimension_name, groupby_agg, groupby_agg_key)
        #end function execution

    #return response
    return text(await append_time_to_response(response,start_time, key, engine))


@app.route('/groupby_filter_order', methods=['GET'])
async def groupby_filter_order(request):
    '''
        description:
            get groupby values by a filter_order(all, top(n), bottom(n)) for a groupby on a dimension
        Get parameters:
            1. session_id (string)
            2. dataset (string)
            3. dimension_name (string)
            4. groupby_agg (JSON stringified object)
            5. sort_order (string): top/bottom/all
            6. num_rows (integer): OPTIONAL -> if sort_order= top/bottom
            7. sort_column: column name by which the result should be sorted
            8. engine (cudf/pandas)
        Response:
            all rows/error => "groupby not initialized"
    '''
    #get basic get parameters
    start_time,session_id,dataset_name,key, engine = await parse_basic_get_parameters(request.args)
    #getting remaining parameters
    dimension_name = request.args.get('dimension_name')
    groupby_agg = json.loads(request.args.get('groupby_agg'))
    sort_order = request.args.get('sort_order')
    num_rows = request.args.get('num_rows')
    sort_column = request.args.get('sort_column')

    # DEBUG: start
    print("groupby filter_order of "+dataset_name+" for dimension_name "+dimension_name+" for "+session_id)
    # DEBUG: end

    if engine == 'cudf':
        #start function execution
        groupby_agg_key = ':'.join(list(groupby_agg.keys())+list(groupby_agg.values())[0])
        response = user_sessions[key].groupby_filter_order(dimension_name, groupby_agg, groupby_agg_key, sort_order, num_rows, sort_column)
        # print(response)
        if 'out of memory' in response or 'thrust::system::system_error' in response:
            user_sessions.pop(session_id+dataset_name,None)
            print('\n\nout of memory error')
        #end function execution
    else:
        #start function execution
        groupby_agg_key = ':'.join(list(groupby_agg.keys())+list(groupby_agg.values())[0])
        response = user_sessions_pandas[key].groupby_filter_order(dimension_name, groupby_agg, groupby_agg_key, sort_order, num_rows, sort_column)
        #end function execution

    #return response
    return text(await append_time_to_response(response,start_time, key, engine))


@app.route('/dimension_load', methods=['GET'])
async def dimension_load(request):
    '''
        description:
            load a dimension
        Get parameters:
            1. session_id (string)
            2. dataset (string)
            3. dimension_name (string)
            4. engine (cudf/pandas)
        Response:
            status -> success: dimension loaded successfully/dimension already exists   // error: "groupby not initialized"
    '''
    #get basic get parameters
    start_time,session_id,dataset_name,key, engine = await parse_basic_get_parameters(request.args)

    #getting remaining parameters
    dimension_name = request.args.get('dimension_name')

    # DEBUG: start
    print("dataset: "+dataset_name+" load dimension_name: "+dimension_name+" for "+session_id)
    # DEBUG: end

    if engine == 'cudf':
        #start function execution
        response = user_sessions[key].dimension_load(dimension_name)
        if 'out of memory' in response or 'thrust::system::system_error' in response:
            user_sessions.pop(session_id+dataset_name,None)
            print('\n\nout of memory error')
        #end function execution
    else:
        #start function execution
        response = user_sessions_pandas[key].dimension_load(dimension_name)
        #end function execution

    #return response
    return text(await append_time_to_response(response,start_time, key, engine))


@app.route('/dimension_reset', methods=['GET'])
async def dimension_reset(request):
    '''
        description:
            reset all filters on a dimension
        Get parameters:
            1. session_id (string)
            2. dataset (string)
            3. dimension_name (string)
            4. engine (cudf/pandas)
        Response:
            number_of_rows
    '''
    #get basic get parameters
    start_time,session_id,dataset_name,key, engine = await parse_basic_get_parameters(request.args)

    #getting remaining parameters
    dimension_name = request.args.get('dimension_name')

    # DEBUG: start
    print("dataset: "+dataset_name+" reset dimension_name: "+dimension_name+" for "+session_id)
    # DEBUG: end

    if engine == 'cudf':
        #start function execution
        response = user_sessions[key].dimension_reset(dimension_name)
        if 'out of memory' in response or 'thrust::system::system_error' in response:
            user_sessions.pop(session_id+dataset_name,None)
            print('\n\nout of memory error')
        #end function execution
        # # DEBUG: start
        # print("reset rows: ")
        # print(response)
        # # DEBUG: end
    else:
        #start function execution
        response = user_sessions_pandas[key].dimension_reset(dimension_name)
        #end function execution

    #return response
    return text(await append_time_to_response(response,start_time, key, engine))

@app.route('/dimension_get_max_min', methods=['GET'])
async def dimension_get_max_min(request):
    '''
        description:
            get_max_min for a dimension
        Get parameters:
            1. session_id (string)
            2. dataset (string)
            3. dimension_name (string)
            4. engine (cudf/pandas)
        Response:
            max_min_tuple
    '''
    #get basic get parameters
    start_time,session_id,dataset_name,key, engine = await parse_basic_get_parameters(request.args)

    #getting remaining parameters
    dimension_name = request.args.get('dimension_name')

    # DEBUG: start
    print("dataset: "+dataset_name+" reset dimension_name: "+dimension_name+" for "+session_id)
    # DEBUG: end

    if engine == 'cudf':
        #start function execution
        response = user_sessions[key].dimension_get_max_min(dimension_name)
        if 'out of memory' in response or 'thrust::system::system_error' in response:
            user_sessions.pop(session_id+dataset_name,None)
            print('\n\nout of memory error')
        #end function execution
    else:
        #start function execution
        response = user_sessions_pandas[key].dimension_get_max_min(dimension_name)
        #end function execution

    #return response
    return text(await append_time_to_response(response,start_time, key, engine))

@app.route('/dimension_hist', methods=['GET'])
async def dimension_hist(request):
    '''
        description:
            get histogram for a dimension
        Get parameters:
            1. session_id (string)
            2. dataset (string)
            3. dimension_name (string)
            4. num_of_bins (integer)
            5. engine (cudf/pandas)
        Response:
            string(json) -> "{X:[__values_of_colName_with_max_64_bins__], Y:[__frequencies_per_bin__]}"
    '''
    #get basic get parameters
    start_time,session_id,dataset_name,key, engine = await parse_basic_get_parameters(request.args)

    #getting remaining parameters
    dimension_name = request.args.get('dimension_name')
    num_of_bins = request.args.get('num_of_bins')

    # DEBUG: start
    print("dataset: "+dataset_name+" get histogram dimension_name: "+dimension_name+" for "+session_id)
    # DEBUG: end

    if engine == 'cudf':
        #start function execution
        response = user_sessions[key].dimension_hist(dimension_name,num_of_bins)
        if 'out of memory' in response or 'thrust::system::system_error' in response:
            user_sessions.pop(session_id+dataset_name,None)
        print(response)
        #end function execution
    else:
        #start function execution
        response = user_sessions_pandas[key].dimension_hist(dimension_name,num_of_bins)
        print(response)
        #end function execution

    #return response
    return text(await append_time_to_response(response,start_time, key, engine))

@app.route('/dimension_filter_order', methods=['GET'])
async def dimension_filter_order(request):
    '''
        description:
            get columns values by a filter_order(all, top(n), bottom(n)) sorted by dimension_name
        Get parameters:
            1. session_id (string)
            2. dataset (string)
            3. dimension_name (string)
            4. sort_order (string): top/bottom/all
            5. num_rows (integer): OPTIONAL -> if sort_order= top/bottom
            6. columns (string): comma separated column names
            7. engine (cudf/pandas)
        Response:
            string(json) -> "{col_1:[__row_values__], col_2:[__row_values__],...}"
    '''
    #get basic get parameters
    start_time,session_id,dataset_name,key, engine = await parse_basic_get_parameters(request.args)

    #getting remaining parameters
    dimension_name = request.args.get('dimension_name')
    sort_order = request.args.get('sort_order')
    num_rows = request.args.get('num_rows')
    columns = request.args.get('columns')

    # DEBUG: start
    print("dataset:"+dataset_name+"filter_order dimension_name:"+dimension_name+" for "+session_id)
    # DEBUG: end

    if engine == 'cudf':
        #start function execution
        response = user_sessions[key].dimension_filter_order(dimension_name, sort_order, num_rows, columns)
        # if response == 'out of memory error, please reload':
        #     user_sessions.pop(session_id+dataset_name,None)
        print('\n\nfilter_order:'+response)
        #end function execution
    else:
        #start function execution
        response = user_sessions_pandas[key].dimension_filter_order(dimension_name, sort_order, num_rows, columns)
        #end function execution

    #return response
    return text(await append_time_to_response(response,start_time, key, engine))


@app.route('/dimension_filter', methods=['GET'])
async def dimension_filter(request):
    '''
        description:
            get columns values by a filter_order(all, top(n), bottom(n)) sorted by dimension_name
        Get parameters:
            1. session_id (string)
            2. dataset (string)
            3. dimension_name (string)
            4. comparison_operation (string)
            5. value (float/int)
            6. engine (cudf/pandas)
        Response:
            number_of_rows_left
    '''
    #get basic get parameters
    start_time,session_id,dataset_name,key, engine = await parse_basic_get_parameters(request.args)

    #getting remaining parameters
    dimension_name = request.args.get('dimension_name')
    comparison_operation = request.args.get('comparison_operation')
    value = request.args.get('value')
    pre_reset = json.loads(request.args.get('pre_reset').lower())   #json.loads converts string to equivalent bool: 'true' to True
    # DEBUG: start
    print("dataset: "+dataset_name+" filter dimension_name: "+dimension_name+" for "+session_id)
    # DEBUG: end

    if engine == 'cudf':
        #start function execution
        response = user_sessions[key].dimension_filter(dimension_name, comparison_operation, value, pre_reset)
        if 'out of memory' in response or 'thrust::system::system_error' in response:
            user_sessions.pop(session_id+dataset_name,None)
            print('\n\nout of memory error')
        #end function execution
    else:
        #start function execution
        response = user_sessions_pandas[key].dimension_filter(dimension_name, comparison_operation, value, pre_reset)
        #end function execution

    #return response
    return text(await append_time_to_response(response,start_time, key, engine))


@app.route('/dimension_filter_range', methods=['GET'])
async def dimension_filter_range(request):
    '''
        description:
            cumulative filter_range dimension_name between range [min_value,max_value]
        Get parameters:
            1. session_id (string)
            2. dataset (string)
            3. dimension_name (string)
            4. min_value (integer)
            5. max_value (integer)
            6. engine (cudf/pandas)
        Response:
            number_of_rows_left
    '''
    #get basic get parameters
    start_time,session_id,dataset_name,key, engine = await parse_basic_get_parameters(request.args)

    #getting remaining parameters
    dimension_name = request.args.get('dimension_name')
    min_value = request.args.get('min_value')
    max_value = request.args.get('max_value')
    pre_reset = json.loads(request.args.get('pre_reset').lower())   #json.loads converts string to equivalent bool: 'true' to True
    # DEBUG: start
    print("dataset:"+dataset_name+" filter_range dimension_name: "+dimension_name+" for "+session_id)
    # DEBUG: end

    if engine == 'cudf':
        #start function execution
        response = user_sessions[key].dimension_filter_range(dimension_name, min_value, max_value, pre_reset)
        if 'out of memory' in response or 'thrust::system::system_error' in response:
            user_sessions.pop(session_id+dataset_name,None)
            print('\n\nout of memory error')
        #end function execution
    else:
        #start function execution
        response = user_sessions_pandas[key].dimension_filter_range(dimension_name, min_value, max_value, pre_reset)
        #end function execution

    #return response
    return text(await append_time_to_response(response,start_time, key, engine))

@app.route('/reset_all_filters', methods=['GET'])
async def reset_all_filters(request):
    '''
        description:
            reset all filters on all dimensions for the dataset
        Get parameters:
            1. session_id (string)
            2. dataset (string)
            3. engine (cudf/pandas)
        Response:
            number_of_rows_left
    '''
    #get basic get parameters
    start_time,session_id,dataset_name,key, engine = await parse_basic_get_parameters(request.args)

    # DEBUG: start
    print("reset all filters of "+dataset_name+" for "+session_id)
    # DEBUG: end

    if engine == 'cudf':
        #start function execution
        response = user_sessions[key].reset_all_filters()
        if 'out of memory' in response or 'thrust::system::system_error' in response:
            user_sessions.pop(session_id+dataset_name,None)
            print('\n\nout of memory error')
        #end function execution
    else:
        #start function execution
        response = user_sessions_pandas[key].reset_all_filters()
        #end function execution

    #return response
    return text(await append_time_to_response(response,start_time, key, engine))


@app.route('/end_connection', methods=['GET'])
async def end_connection(request):
    '''
        description:
            end connection by removing the dataframe for the session from memory (gpu memory for cudf/ cpu memory for pandas DataFrame)
        Get parameters:
            1. session_id (string)
            2. dataset (string)
            3. engine (cudf/pandas)
        Response:
            status
    '''
    #get basic get parameters
    start_time,session_id,dataset_name,key, engine = await parse_basic_get_parameters(request.args)

    print("end connection for "+session_id)

    if key not in user_sessions:
        response = "Connection does not exist"
    else:
        try:
            if key in user_sessions and engine == 'cudf':
                user_sessions.pop(session_id+dataset_name,None)
                print('\n\nout of memory error')
            elif key in user_sessions_pandas and engine == 'pandas':
                user_sessions_pandas.pop(session_id+dataset_name,None)
            response = "successfully removed dataframe from memory"
        except e:
            response = str(e)

    elapsed = time.perf_counter() - start_time
    response = response+"&"+str(elapsed)
    return text(response)

async def append_time_to_response(response,start_time, key, engine):
    '''
        description:
            append time and activeFilters to the response string
        Get parameters:
            1. response (string)
            2. start_time (string)
            3. key (string -> session_id+dataset_name)
            4. engine (cudf/pandas)
        Response:
            response string with time taken and activeFilters appended with '&' as a separator
    '''
    elapsed = time.perf_counter() - start_time
    if engine == 'cudf':
        response = response+"&"+str(elapsed)+"&"+str(user_sessions[key].dimensions_filters_response_format)
    else:
        response = response+"&"+str(elapsed)+"&"+str(user_sessions_pandas[key].dimensions_filters_response_format)
    return response


async def parse_basic_get_parameters(get_params):
    '''
        description:
            parse the get parameters to extract basic information required for each function
        Get parameters:
            1. get_params
        Response:
            start_time
            session_id
            dataset_name
            key(session_id+dataset_name)
            engine(cudf/pandas)
    '''
    #start timer
    start_time = time.perf_counter()
    #start get parameters
    # print(get_params)
    session_id = get_params['session_id'][0]
    dataset_name = get_params['dataset'][0]
    engine = get_params['engine'][0]
    # print('\n\ndataset_name '+dataset_name)
    key = session_id+dataset_name
    #end get parameters
    # print(start_time,session_id,dataset_name,key,engine)
    return start_time,session_id,dataset_name,key,engine
