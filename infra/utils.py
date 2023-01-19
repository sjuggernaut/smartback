import numpy as np

INERTIAL_DATA_FIELDS = (
    'l5s1_lateral', 'l5s1_axial', 'l5s1_flexion', 'l4l3_lateral', 'l4l3_axial', 'l4l3_flexion', 'l1t12_lateral',
    'l1t12_axial', 'l1t12_flexion', 't9t8_lateral', 't9t8_axial', 't9t8_flexion', 't1c7_lateral', 't1c7_axial',
    't1c7_flexion', 'c1head_lateral', 'c1head_axial', 'c1head_flexion', 'com_posx', 'com_posy', 'com_posz')
CENTER_OF_MASS_FIELD_INDICES = [com_field_index for com_field_index, _ in enumerate(INERTIAL_DATA_FIELDS) if
                                _ in ('com_posx', 'com_posy', 'com_posz')]

SEMG_DATA_FIELDS = ('rightc4_paraspinal', 'leftc4_paraspinal', 'right_multifidus', 'left_multifidus')
SEMG_DATA_FIELDS_RIGHT_INDICES = [0, 2]
SEMG_DATA_FIELDS_LEFT_INDICES = [1, 3]

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
    return float(input_temp) > THERMAL_INPUT_THRESHOLD


def multiply_list_with(number, list_to_multiply) -> list:
    return list(np.array(list(list_to_multiply)) * float(number))


def subtract_then_average(list1, list2) -> float:
    difference = np.array(list1) - np.array(list2)
    return np.average(difference)


def subtract(list1, list2) -> list:
    return (np.array(list1) - np.array(list2)).tolist()


def average(values) -> float:
    return np.average(np.array(values))


def positive_count(list_to_count):
    np_array = np.array(list_to_count)
    return (np_array > 0).sum()


def negative_count(list_to_count):
    np_array = np.array(list_to_count)
    return (np_array < 0).sum()


def count_nonzero(list_to_count):
    np_array = np.array(list_to_count)
    return np.count_nonzero(np_array)
