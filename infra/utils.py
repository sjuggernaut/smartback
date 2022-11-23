import numpy as np

INERTIAL_DATA_FIELDS = (
    'l5s1_lateral', 'l5s1_axial', 'l5s1_flexion', 'l4l3_lateral', 'l4l3_axial', 'l4l3_flexion', 'l1t12_lateral',
    'l1t12_axial', 'l1t12_flexion', 't9t8_lateral', 't9t8_axial', 't9t8_flexion', 't1c7_lateral', 't1c7_axial',
    't1c7_flexion', 'c1head_lateral', 'c1head_axial', 'c1head_flexion')

SEMG_DATA_FIELDS = ('rightc4_paraspinal', 'leftc4_paraspinal', 'right_multifidus', 'left_multifidus')


def get_mean(data: list):
    """
    Calculate mean for the list.
    """
    mean = np.mean(data, axis=0)
    return np.round_(mean, decimals=2).tolist()


def compare_with_gold_standard(data_to_compare: list, gold_standard: list):
    np_data_to_compare = np.array(data_to_compare) # patient data
    np_gold_standard = np.array(gold_standard) # gold standard

    result = np_gold_standard - np_data_to_compare
    if np.count_nonzero(result) < 1:
        return False
    return True
