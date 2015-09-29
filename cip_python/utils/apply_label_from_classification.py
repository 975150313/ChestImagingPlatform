import numpy as np
from optparse import OptionParser
from cip_python.ChestConventions import ChestConventions
import nrrd
import pdb
import pandas as pd
#from cip_python.io.image_reader_writer import ImageReaderWriter


          
def apply_label_from_classification(segmentation, lm, classified_features_df):
        """
        given a patch segmentation file, a labelmap file, and a classification csv file,
        apply the classification labels to each of the patches in areas where 
        labelmap > 0. The labels follow cip conventions.
        """
    
        mychestConvenstion =ChestConventions()
        classification_lm = np.zeros(np.shape(segmentation), dtype = 'int') 
    
        #classified_features_df['ChestRegion'].values
    
        patch_labels = np.array(classified_features_df.filter(regex='patch_label'))[:]
        class_types_list = classified_features_df.filter(regex='ChestType').values
        class_regions_list = classified_features_df.filter(regex='ChestRegion').values
 
        num_patches = len(classified_features_df)
        for row in range(0, num_patches):
            class_type= mychestConvenstion.GetChestTypeValueFromName(class_types_list[row][0]) 
            class_region= mychestConvenstion.GetChestRegionValueFromName(class_regions_list[row][0])             
                
            classification_lm[np.logical_and(segmentation == int(patch_labels[row]), lm >0)]  = mychestConvenstion.GetValueFromChestRegionAndType( class_region, class_type) 
        
        return classification_lm

if __name__ == "__main__":
    desc = """Classifies CT images into emphysema subtyoes"""
    
    parser = OptionParser(description=desc)
    parser.add_option('--in_lm',
                      help='Input mask file. The classification will only be \
                      computed in areas where the mask is > 0. ', 
                      dest='in_lm', metavar='<string>', default=None)
    parser.add_option('--in_patch',
                      help='Input patch file.', 
                      dest='in_patch', metavar='<string>', default=None)
    parser.add_option('--in_csv',
                      help='Input csv file with a classification for every \
                        patch ', dest='in_csv', 
                      metavar='<string>', default=None)          
    parser.add_option('--out_label',
                      help='Output label file with the emphysema \
                        classifications ', dest='out_label', 
                      metavar='<string>', default=None)                                         
                                      
    (options, args) = parser.parse_args()
    
    assert(options.in_csv is not None), "csv input missing"
    assert(options.in_lm is not None), "lm input missing"       

    print "Reading mask..." 
    lm_array, lm_header = nrrd.read(options.in_lm) 
    patch_array, patch_header = nrrd.read(options.in_patch) 

    dataLists = pd.read_csv(options.in_csv)  
   
    labels_array = apply_label_from_classification(patch_array, lm_array, \
        dataLists)

    assert(options.out_label is not None), \
        " outputs missing"   
        
    print "Writing output labels "
    nrrd.write(options.out_label, labels_array, lm_header , True, True)
                               