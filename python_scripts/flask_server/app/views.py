# views.py

from flask import render_template,jsonify,request
import logging
import json
from app import app
import time
from app.utilities.pygdfCrossfilter_utils import pygdfCrossfilter_utils as pygdf

user_sessions = {}

@app.route('/')
def index():
    return render_template("index.html")

def init_session(session_id):
    user_sessions[session_id] = pygdf()

@app.route('/process', methods=['GET'])
def process_input_from_client():
    #get basic get parameters
    start_time,session_id,dataset_name,key = parse_basic_get_parameters(request.args)

    query = request.args.get('query')

    app.logger.debug("query: "+query)

    if session_id not in user_sessions:
        init_session(session_id)
    response = user_sessions[session_id].process_input_from_client(query)
    return append_time_to_response(response,start_time)


@app.route('/init_connection', methods=['GET'])
def init_connection():
    '''
        description:
            initialize connection with node client for this user-dataset combination
        Get parameters:
            1. session_id (string)
            2. dataset (string)
        Response:
            status -> successfully initialized/ error
    '''
    #get basic get parameters
    start_time,session_id,dataset_name,key = parse_basic_get_parameters(request.args)

    app.logger.debug("init connection for "+session_id)

    if session_id not in user_sessions:
        init_session(session_id+dataset_name)
        response = "initialized successfully"
    else:
        response = "connection already intialized"
    return append_time_to_response(response,start_time)


@app.route('/read_data', methods=['GET'])
def read_data():
    '''
        description:
            read arrow file from disk to gpu memory
        Get parameters:
            1. session_id (string)
            2. dataset (string)
        Response:
            status -> data read successfully / error
    '''
    #get basic get parameters
    start_time,session_id,dataset_name,key = parse_basic_get_parameters(request.args)

    # DEBUG: start
    app.logger.debug("read data"+dataset_name+" for "+session_id)
    # DEBUG: end

    #start function execution
    response = user_sessions[key].read_data('arrow',dataset_name)
    user_sessions[key].numba_jit_warm_func()
    #end function execution

    #return response
    return append_time_to_response(response,start_time)

@app.route('/get_schema', methods=['GET'])
def get_schema():
    '''
        description:
            get schema of the dataset
        Get parameters:
            1. session_id (string)
            2. dataset (string)
        Response:
            comma separated column names
    '''
    #get basic get parameters
    start_time,session_id,dataset_name,key = parse_basic_get_parameters(request.args)

    # DEBUG: start
    app.logger.debug("get schema of"+dataset_name+" for "+session_id)
    # DEBUG: end

    #start function execution
    response = user_sessions[key].get_columns()
    #end function execution

    #return response
    return append_time_to_response(response,start_time)


@app.route('/get_size', methods=['GET'])
def get_size():
    '''
        description:
            get size of the dataset
        Get parameters:
            1. session_id (string)
            2. dataset (string)
        Response:
            "(num_rows, num_columns)"
    '''
    #get basic get parameters
    start_time,session_id,dataset_name,key = parse_basic_get_parameters(request.args)

    # DEBUG: start
    app.logger.debug("get size of"+dataset_name+" for "+session_id)
    # DEBUG: end

    #start function execution
    response = user_sessions[key].get_size()
    #end function execution

    #return response
    return append_time_to_response(response,start_time)


@app.route('/groupby_load', methods=['GET'])
def groupby_load():
    '''
        description:
            load groupby operation for dimension as per the given groupby_agg
        Get parameters:
            1. session_id (string)
            2. dataset (string)
            3. dimension_name (string)
            4. groupby_agg (JSON stringified object)
        Response:
            number_of_rows_left
    '''
    #get basic get parameters
    start_time,session_id,dataset_name,key = parse_basic_get_parameters(request.args)

    #getting remaining parameters
    dimension_name = request.args.get('dimension_name')
    groupby_agg = json.loads(request.args.get('groupby_agg'))

    # DEBUG: start
    app.logger.debug("groupby load of "+dataset_name+" for dimension_name: "+dimension_name+" for "+session_id)
    # DEBUG: end

    #start function execution
    groupby_agg_key = ':'.join(list(groupby_agg.keys())+list(groupby_agg.values())[0])
    response = user_sessions[key].groupby_load(dimension_name, groupby_agg, groupby_agg_key)
    #end function execution

    #return response
    return append_time_to_response(response,start_time)

@app.route('/groupby_size', methods=['GET'])
def groupby_size():
    '''
        description:
            get groupby size for a groupby on a dimension
        Get parameters:
            1. session_id (string)
            2. dataset (string)
            3. dimension_name (string)
            4. groupby_agg (JSON stringified object)
        Response:
            number_of_rows_left
    '''
    #get basic get parameters
    start_time,session_id,dataset_name,key = parse_basic_get_parameters(request.args)

    #getting remaining parameters
    dimension_name = request.args.get('dimension_name')
    groupby_agg = json.loads(request.args.get('groupby_agg'))

    # DEBUG: start
    app.logger.debug("groupby size of "+dataset_name+" for dimension_name: "+dimension_name+" for "+session_id)
    # DEBUG: end

    #start function execution
    groupby_agg_key = ':'.join(list(groupby_agg.keys())+list(groupby_agg.values())[0])
    response = user_sessions[key].groupby_size(dimension_name, groupby_agg_key)
    #end function execution

    #return response
    return append_time_to_response(response,start_time)


@app.route('/groupby_filterOrder', methods=['GET'])
def groupby_filterOrder():
    '''
        description:
            get groupby values by a filterOrder(all, top(n), bottom(n)) for a groupby on a dimension
        Get parameters:
            1. session_id (string)
            2. dataset (string)
            3. dimension_name (string)
            4. groupby_agg (JSON stringified object)
            5. sort_order (string): top/bottom/all
            6. num_rows (integer): OPTIONAL -> if sort_order= top/bottom
            7. sort_column: column name by which the result should be sorted
        Response:
            all rows/error => "groupby not initialized"
    '''
    #get basic get parameters
    start_time,session_id,dataset_name,key = parse_basic_get_parameters(request.args)

    #getting remaining parameters
    dimension_name = request.args.get('dimension_name')
    groupby_agg = json.loads(request.args.get('groupby_agg'))
    sort_order = request.args.get('sort_order')
    num_rows = request.args.get('num_rows')
    sort_column = request.args.get('sort_column')

    # DEBUG: start
    app.logger.debug("groupby filterOrder of "+dataset_name+" for dimension_name "+dimension_name+" for "+session_id)
    # DEBUG: end

    #start function execution
    groupby_agg_key = ':'.join(list(groupby_agg.keys())+list(groupby_agg.values())[0])
    response = user_sessions[key].groupby_filterOrder(dimension_name, groupby_agg, groupby_agg_key, sort_order, num_rows, sort_column)
    #end function execution

    #return response
    return append_time_to_response(response,start_time)


@app.route('/dimension_load', methods=['GET'])
def dimension_load():
    '''
        description:
            load a dimension
        Get parameters:
            1. session_id (string)
            2. dataset (string)
            3. dimension_name (string)
        Response:
            status -> success: dimension loaded successfully/dimension already exists   // error: "groupby not initialized"
    '''
    #get basic get parameters
    start_time,session_id,dataset_name,key = parse_basic_get_parameters(request.args)

    #getting remaining parameters
    dimension_name = request.args.get('dimension_name')

    # DEBUG: start
    app.logger.debug("dataset: "+dataset_name+" load dimension_name: "+dimension_name+" for "+session_id)
    # DEBUG: end

    #start function execution
    response = user_sessions[key].dimension_load(dimension_name)
    #end function execution

    #return response
    return append_time_to_response(response,start_time)


@app.route('/dimension_reset', methods=['GET'])
def dimension_reset():
    '''
        description:
            reset all filters on a dimension
        Get parameters:
            1. session_id (string)
            2. dataset (string)
            3. dimension_name (string)
        Response:
            number_of_rows
    '''
    #get basic get parameters
    start_time,session_id,dataset_name,key = parse_basic_get_parameters(request.args)

    #getting remaining parameters
    dimension_name = request.args.get('dimension_name')

    # DEBUG: start
    app.logger.debug("dataset: "+dataset_name+" reset dimension_name: "+dimension_name+" for "+session_id)
    # DEBUG: end

    #start function execution
    response = user_sessions[key].dimension_reset(dimension_name)
    #end function execution
    # # DEBUG: start
    # app.logger.debug("reset rows: ")
    # app.logger.debug(response)
    # # DEBUG: end
    #return response
    return append_time_to_response(response,start_time)

@app.route('/dimension_get_max_min', methods=['GET'])
def dimension_get_max_min():
    '''
        description:
            get_max_min for a dimension
        Get parameters:
            1. session_id (string)
            2. dataset (string)
            3. dimension_name (string)
        Response:
            max_min_tuple
    '''
    #get basic get parameters
    start_time,session_id,dataset_name,key = parse_basic_get_parameters(request.args)

    #getting remaining parameters
    dimension_name = request.args.get('dimension_name')

    # DEBUG: start
    app.logger.debug("dataset: "+dataset_name+" reset dimension_name: "+dimension_name+" for "+session_id)
    # DEBUG: end

    #start function execution
    response = user_sessions[key].dimension_get_max_min(dimension_name)
    #end function execution

    #return response
    return append_time_to_response(response,start_time)

@app.route('/dimension_hist', methods=['GET'])
def dimension_hist():
    '''
        description:
            get histogram for a dimension
        Get parameters:
            1. session_id (string)
            2. dataset (string)
            3. dimension_name (string)
            4. num_of_bins (integer)
        Response:
            string(json) -> "{X:[__values_of_colName_with_max_64_bins__], Y:[__frequencies_per_bin__]}"
    '''
    #get basic get parameters
    start_time,session_id,dataset_name,key = parse_basic_get_parameters(request.args)

    #getting remaining parameters
    dimension_name = request.args.get('dimension_name')
    num_of_bins = request.args.get('num_of_bins')

    # DEBUG: start
    app.logger.debug("dataset: "+dataset_name+" get histogram dimension_name: "+dimension_name+" for "+session_id)
    # DEBUG: end

    #start function execution
    response = user_sessions[key].dimension_hist(dimension_name,num_of_bins)
    #end function execution

    #return response
    return append_time_to_response(response,start_time)

@app.route('/dimension_filterOrder', methods=['GET'])
def dimension_filterOrder():
    '''
        description:
            get columns values by a filterOrder(all, top(n), bottom(n)) sorted by dimension_name
        Get parameters:
            1. session_id (string)
            2. dataset (string)
            3. dimension_name (string)
            4. sort_order (string): top/bottom/all
            5. num_rows (integer): OPTIONAL -> if sort_order= top/bottom
            6. columns (string): comma separated column names
        Response:
            string(json) -> "{col_1:[__row_values__], col_2:[__row_values__],...}"
    '''
    #get basic get parameters
    start_time,session_id,dataset_name,key = parse_basic_get_parameters(request.args)

    #getting remaining parameters
    dimension_name = request.args.get('dimension_name')
    sort_order = request.args.get('sort_order')
    num_rows = request.args.get('num_rows')
    columns = request.args.get('columns')

    # DEBUG: start
    app.logger.debug("dataset:"+dataset_name+"filterOrder dimension_name:"+dimension_name+" for "+session_id)
    # DEBUG: end

    #start function execution
    response = user_sessions[key].dimension_filterOrder(dimension_name, sort_order, num_rows, columns)
    #end function execution

    #return response
    return append_time_to_response(response,start_time)


@app.route('/dimension_filter', methods=['GET'])
def dimension_filter():
    '''
        description:
            get columns values by a filterOrder(all, top(n), bottom(n)) sorted by dimension_name
        Get parameters:
            1. session_id (string)
            2. dataset (string)
            3. dimension_name (string)
            4. comparison_operation (string)
            5. value (float/int)
        Response:
            number_of_rows_left
    '''
    #get basic get parameters
    start_time,session_id,dataset_name,key = parse_basic_get_parameters(request.args)

    #getting remaining parameters
    dimension_name = request.args.get('dimension_name')
    comparison_operation = request.args.get('comparison_operation')
    value = request.args.get('value')

    # DEBUG: start
    app.logger.debug("dataset: "+dataset_name+" filter dimension_name: "+dimension_name+" for "+session_id)
    # DEBUG: end

    #start function execution
    response = user_sessions[key].dimension_filter(dimension_name, comparison_operation, value)
    #end function execution

    #return response
    return append_time_to_response(response,start_time)


@app.route('/dimension_filter_range', methods=['GET'])
def dimension_filter_range():
    '''
        description:
            cumulative filter_range dimension_name between range [min_value,max_value]
        Get parameters:
            1. session_id (string)
            2. dataset (string)
            3. dimension_name (string)
            4. min_value (integer)
            5. max_value (integer)
        Response:
            number_of_rows_left
    '''
    #get basic get parameters
    start_time,session_id,dataset_name,key = parse_basic_get_parameters(request.args)

    #getting remaining parameters
    dimension_name = request.args.get('dimension_name')
    min_value = request.args.get('min_value')
    max_value = request.args.get('max_value')

    # DEBUG: start
    app.logger.debug("dataset:"+dataset_name+" filter_range dimension_name: "+dimension_name+" for "+session_id)
    # DEBUG: end

    #start function execution
    response = user_sessions[key].dimension_filter_range(dimension_name, min_value, max_value)
    #end function execution

    #return response
    return append_time_to_response(response,start_time)

@app.route('/reset_all_filters', methods=['GET'])
def reset_all_filters():
    '''
        description:
            reset all filters on all dimensions for the dataset
        Get parameters:
            1. session_id (string)
            2. dataset (string)
        Response:
            number_of_rows_left
    '''
    #get basic get parameters
    start_time,session_id,dataset_name,key = parse_basic_get_parameters(request.args)

    # DEBUG: start
    app.logger.debug("reset all filters of "+dataset_name+" for "+session_id)
    # DEBUG: end

    #start function execution
    response = user_sessions[key].reset_all_filters()
    #end function execution

    #return response
    return append_time_to_response(response,start_time)


@app.route('/end_connection', methods=['GET'])
def end_connection():
    start_time = time.perf_counter()
    session_id = request.args.get('session_id')
    dataset_name = request.args.get('dataset')
    app.logger.debug("end connection for "+session_id)
    if session_id+dataset_name not in user_sessions:
        response = "Connection does not exist"
    else:
        try:
            user_sessions.pop(session_id+dataset_name,None)
            response = "successfully ended"
        except e:
            response = str(e)
    return append_time_to_response(response,start_time)

def append_time_to_response(res,start_time):
    elapsed = time.perf_counter() - start_time
    # #appending
    # if len(res.split(":::"))>2:
    #     res = res+","+str(elapsed)+"////"
    # else:
    #     res = res+":::"+str(elapsed)+"////"
    # # encode the result string
    # res = res.encode("utf8")
    res = res+":::"+str(elapsed)
    return res


def parse_basic_get_parameters(get_params):
    #start timer
    start_time = time.perf_counter()
    #start get parameters
    session_id = get_params.get('session_id')
    dataset_name = get_params.get('dataset')

    print(dataset_name)
    key = session_id+dataset_name
    #end get parameters
    return start_time,session_id,dataset_name,key
