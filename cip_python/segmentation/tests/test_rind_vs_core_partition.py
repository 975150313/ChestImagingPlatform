import os.path
import pandas as pd
#import nrrd
from cip_python.segmentation.rind_vs_core_partition import RindVsCorePartition
import numpy as np
import pdb
from cip_python.input_output.image_reader_writer import ImageReaderWriter

np.set_printoptions(precision = 3, suppress = True, threshold=1e6,
                    linewidth=200) 

this_dir = os.path.dirname(os.path.realpath(__file__))
lm_name = this_dir + '/../../../Testing/Data/Input/lm-64.nrrd'
partition_name = this_dir + '/../../../Testing/Data/Input/rind_partition-64.nrrd'

def test_execute():
    image_io = ImageReaderWriter()
    lm_array,lm_header=image_io.read_in_numpy(lm_name)
    partition_ref_array, partition_header = image_io.read_in_numpy(partition_name)
    
    
    spacing = np.zeros(3)
    spacing[0] = lm_header['spacing'][0]
    spacing[1] = lm_header['spacing'][1]
    spacing[2] = lm_header['spacing'][2]
    
    rind_core_partitioner = RindVsCorePartition(rind_width=10.0)
    rind_core_partitioner.execute(lm_array, spacing)
    
    rind_lm = rind_core_partitioner.get_partition_region_mask('Rind')
    assert np.sum(np.abs(partition_ref_array-rind_lm))==0, 'rind not as \
        expected'
