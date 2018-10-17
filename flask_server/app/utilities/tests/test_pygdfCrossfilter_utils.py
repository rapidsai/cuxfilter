import pygdfCrossfilter_utils as pygdf

class pygdfCrossfilter_utils_test():
    def test_read(self):
        result = pygdf.read_data('arrow','../../../../node_server/uploads/predictions-v1')
        assert(result,'data read successfully')
        
