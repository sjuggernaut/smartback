import numpy as np

INERTIAL_DATA_FIELDS = (
    'l5s1_lateral', 'l5s1_axial', 'l5s1_flexion', 'l4l3_lateral', 'l4l3_axial', 'l4l3_flexion', 'l1t12_lateral',
    'l1t12_axial', 'l1t12_flexion', 't9t8_lateral', 't9t8_axial', 't9t8_flexion', 't1c7_lateral', 't1c7_axial',
    't1c7_flexion', 'c1head_lateral', 'c1head_axial', 'c1head_flexion')

SEMG_DATA_FIELDS = ('rightc4_paraspinal', 'leftc4_paraspinal', 'right_multifidus', 'left_multifidus')

THERMAL_INPUT_THRESHOLD = 42.0


def get_mean(data: list):
    """
    Calculate mean for the list.
    """
    mean = np.mean(data, axis=0)
    return np.round_(mean, decimals=2).tolist()


def compare_with_gold_standard(data_to_compare: list, gold_standard: list):
    np_data_to_compare = np.array(data_to_compare)  # patient data
    np_gold_standard = np.array(gold_standard)  # gold standard

    result = np_gold_standard - np_data_to_compare
    if np.count_nonzero(result) < 1:
        return False
    return True


def is_temp_higher(input_temp: float) -> bool:
    return input_temp > THERMAL_INPUT_THRESHOLD


def multiply_list_with(number, list_to_multiply) -> list:
    return list(np.array(list(list_to_multiply)) * float(number))


def subtract_then_average(list1, list2) -> float:
    difference = np.array(list1) - np.array(list2)
    return np.average(difference)


def average(values) -> float:
    return np.average(np.array(values))
