"""
This class will do processing of the data after it is collected for 1 minute during treatment stage.
The 1 minute sending process is started by the command, Commands.treatment_start.
Everytime a one mind end is completed, engine processes that data received for a whole minute and the result is an stimulation output value through the sensors.
"""
import logging
from time import sleep

from infra.utils import *
from infra.models import *
from infra.domain.dataclasses import *

logger = logging.getLogger(__name__)


class TreatmentOneMinuteEndDataProcessor:

    @staticmethod
    def check_all_ipc_commands(session: Session):
        """
        To check if all the 3 IPC commands are received.
        If received from all the three (3) sensors - process the data for all the 3 sensors for 1 minute data.
        Else - return and let the sensors send the command again. then this will succeed.
        :param session:
        :param name:
        :return:
        """

        logger.info(f"Processing Treatment one minute send IPC command for session {session.id}")
        ipc_commands = TreatmentOneMinuteEndDataProcessor.is_ipc_commands_received(session)

        if ipc_commands.session_exists:
            """
            If this condition is True: All the 3 required sensor one mind end commands have been received from the 
            sensors during treatment stage. 
            """
            # It is important to set this to true to avoid duplicate processing of the same session one minute
            ipc_commands.session_instance.save()

            """
            Start processing the data from IRSensorData, SEMGSensorData, InertialSensorData for the session
            """
            TreatmentOneMinuteEndDataProcessor.process_data(session)
            TreatmentOneMinuteEndDataProcessor.update_ipc_processing_status()

            # TODO: Create new record for SessionTreatmentIPCReceived for next one minute loop cycle
            TreatmentOneMinuteEndDataProcessor.create_new_ipc_treatment_record()

            # TODO: Set read_status=True for all the data from TreatmentSEMGData, TreatmentInertialData with session.
            TreatmentOneMinuteEndDataProcessor.set_treatment_data_read_status()
        else:
            # TODO: raise Exception("Session {session.id} hasn't received all three sensor commands for one minute data processing")
            logger.info(
                f"Session {session.id} hasn't received all three sensor commands for one minute data processing")

    @staticmethod
    def set_treatment_data_read_status(session: Session):
        """
        Update the read status for all the sensor data rows in SEMG and Inertial Tables
        :param session:
        :return:
        """
        TreatmentSEMGData.objects.filter(session=session).update(read_status=True)
        TreatmentInertialData.objects.filter(session=session).update(read_status=True)

    @staticmethod
    def create_new_ipc_treatment_record(session: Session):
        """
        Create new record for SessionTreatmentIPCReceived for next one minute loop cycle.
        Record created for current treatment session for the user.
        :param session:
        :return:
        """
        if session.type == SessionTypes.TREATMENT:
            SessionTreatmentIPCReceived.objects.create(session=session,
                                                       processing_status=False,
                                                       semg_received=False,
                                                       inertial_received=False,
                                                       ir_received=False)
        else:
            logger.info(
                f"The provided session type is not {SessionTypes.TREATMENT}. Skipping creation of IPC Treatment record.")

    @staticmethod
    def update_ipc_processing_status(session: Session):
        SessionTreatmentIPCReceived.objects.filter(session=session,
                                                   processing_status=False,
                                                   semg_received=True,
                                                   inertial_received=True,
                                                   ir_received=True).update(processing_status=True)

    @staticmethod
    def is_ipc_commands_received(session: Session) -> DataClassIPCCommandReceived:
        session_query = SessionTreatmentIPCReceived.objects.filter(session=session,
                                                                   processing_status=False,
                                                                   semg_received=True,
                                                                   inertial_received=True,
                                                                   ir_received=True)
        session_exists = session_query.exists()
        session_instance = session_query.first()
        return DataClassIPCCommandReceived(session_exists=session_exists, session_instance=session_instance)

    # @staticmethod
    # def get_ir_thermal_mean(session: Session):

    @staticmethod
    def process_data(session: Session) -> bool:
        """
        DO :: Fetch data from IRSensorData, SEMGSensorData, InertialSensorData by Session and read_status=False
        All this data is expected to be from the latest One minute send process from sensors.
        DO ::
            1. Inertial Data: compute Mean data => compute difference between mean data and gold standard
            2. SEMG Data: compute Mean data =>
                2.1: compare with gold standard
                2.2: determine left or right side for stimulation
            3. IR Data: Compute Mean data: check if mean data is less than 42 degrees celsius
        DO :: Compute Stimulation Output based on the above data (formula yet to be given)
        DO :: Send the result to IPC topic for stimulation
        :param session:
        :return:
        """
        try:
            TreatmentOneMinuteEndDataProcessor.check_ir_thermal_value()

            inertial_data = TreatmentInertialData.objects.filter(session=session, read_status=False)
            semg_data = TreatmentSEMGData.objects.filter(session=session, read_status=False)
            ir_data = GenericIRSensorData.objects.filter(session=session, read_status=False)

            inertial_data_list = list(inertial_data.values_list(*INERTIAL_DATA_FIELDS))
            inertial_data_mean = get_mean(inertial_data_list)  # Single row value derived from

            semg_data_list = list(semg_data.values_list(*SEMG_DATA_FIELDS))
            semg_data_mean = get_mean(semg_data_list)

            ir_data_list = list(ir_data.values_list('thermal'))
            ir_data_mean = get_mean(ir_data_list)
            #
            # # compare the 3 mean values with their respective gold standard
            # # compute the IR energy stimulation and produce the value to Raspberry PI - IR LED. topic: ir-led-alerts


        except Exception as e:
            logger.info(f"Treatment IPC: There is an error during treatment one minute end data processing: [{e}]")

    @staticmethod
    def check_ir_thermal_value(user_ir_thermal_mean: float) -> bool:
        """
        Step 1
        Check if the thermal value from the IR sensor is below the configured value (42 degrees)
        :return:
        """
        return is_temp_higher(user_ir_thermal_mean)

    @staticmethod
    def get_user_treatment_gold_standard(session: Session):
        """
        UserGoldStandardInertialData and UserGoldStandardSEMGData
        Retrieve user's gold standard values for Treatment.
        :param session:
        :return:
        """
        user_inertial_gs = UserGoldStandardInertialData.objects.filter(user=session.user, is_final_data=True)
        user_semg_gs = UserGoldStandardSEMGData.objects.filter(user=session.user, is_final_data=True)

        inertial_gs_list = list(user_inertial_gs.values_list(*INERTIAL_DATA_FIELDS))
        semg_gs_list = list(user_semg_gs.values_list(*SEMG_DATA_FIELDS))

        if len(inertial_gs_list) > 1:
            inertial_gs_list = inertial_gs_list[0]

        if len(semg_gs_list) > 1:
            semg_gs_list = semg_gs_list[0]

        return DataClassTreatmentGoldStandardForUser(semg=semg_gs_list, inertial=inertial_gs_list)

    @staticmethod
    def calculate_differential_values(user_treatment_gs: DataClassTreatmentGoldStandardForUser,
                                      user_data_mean: DataClassUserTreatmentMean
                                      ):
        """
        ===========================================================================================================
        SEMG Differential Value
        ===========================================================================================================

        [(Right side of the golden standard treatment sEMG values) - (Right side of client’s sEMG data)] -
        [(Left side of golden standard treatment sEMG values) - (Left side of client’s sEMG data)]

        ===========================================================================================================
        Inertial Differential Value
        ===========================================================================================================

        Inertial Gold Standard Values - Client's Inertial Data Mean

        :return:
        """
        # ====================== SEMG Calculation ======================
        right_semg_gs = [right_semg_item for right_semg_index, right_semg_item in enumerate(user_treatment_gs.semg) if
                         right_semg_index in SEMG_DATA_FIELDS_RIGHT_INDICES]
        right_semg_mean = [right_semg_mean_item for right_semg_mean_index, right_semg_mean_item in
                           enumerate(user_data_mean.semg) if right_semg_mean_index in SEMG_DATA_FIELDS_RIGHT_INDICES]
        right_diff = subtract(right_semg_gs, right_semg_mean)

        left_semg_gs = [left_semg_item for left_semg_index, left_semg_item in enumerate(user_treatment_gs.semg) if
                        left_semg_index in SEMG_DATA_FIELDS_LEFT_INDICES]
        left_semg_mean = [left_semg_mean_item for left_semg_mean_index, left_semg_mean_item in
                          enumerate(user_data_mean.semg) if left_semg_mean_index in SEMG_DATA_FIELDS_LEFT_INDICES]
        left_diff = subtract(left_semg_gs, left_semg_mean)

        semg_differential_value = subtract(right_diff, left_diff)

        # ====================== Inertial Calculation ======================
        inertial_differential_value = subtract(user_treatment_gs.inertial, user_data_mean.inertial)

        return DataClassDifferentialValuesForTreatment(semg=semg_differential_value,
                                                       inertial=inertial_differential_value)

    @staticmethod
    def calculate_stimulation_site(differential_values: DataClassDifferentialValuesForTreatment):
        """
        Compute stimulation site for the current loop cycle.
        - Step 1: Compute Inertial data
        - Step 2: Compute SEMG data
        - Step 3: Return side of stimulation site (instance of dataclass)

        ========================================================================================================
        1. Inertial Inertial Differential Value = User Treatment Gold Standard - User 1 Minute Cycle Mean Data
        ========================================================================================================

            If the Inertial Differential Value is NEGATIVE = LEFT SIDE
                   Inertial Differential Value is POSITIVE = RIGHT SIDE
                                     NEGATIVE AND POSITIVE = BOTH SIDES

        ========================================================================================================
        2. SEMG Differential Value = User Treatment Gold Standard - User 1 Minute Cycle Mean Data
        ========================================================================================================

             If the SEMG Differential Value is NEGATIVE = LEFT SIDE
                   SEMG Differential Value is POSITIVE  = RIGHT SIDE
                                            Value is 0  = BOTH SIDES

        :param differential_values:DataClassDifferentialValuesForTreatment
        :return:
        """
        inertial_result_side = None

        # ==============================================================================
        # Inertial Sensors provide 18 joint values and 3 Center of mass values
        # ==============================================================================
        inertial_positive_count = positive_count(differential_values.inertial)
        inertial_negative_count = negative_count(differential_values.inertial)

        if inertial_positive_count == len(INERTIAL_DATA_FIELDS):
            inertial_result_side = StimulationSide.right

        if inertial_negative_count == len(INERTIAL_DATA_FIELDS):
            inertial_result_side = StimulationSide.left

        if inertial_positive_count > 0 and inertial_negative_count > 0:
            inertial_result_side = StimulationSide.both

        # ==============================================================================
        # SEMG Differential values count is 2 based on the formula in calculate_differential_values()
        # ==============================================================================
        semg_positive_count = positive_count(differential_values.semg)
        semg_negative_count = negative_count(differential_values.semg)
        semg_result_side = None

        if semg_positive_count == len(differential_values.semg):
            semg_result_side = StimulationSide.right

        if semg_negative_count == len(differential_values.semg):
            semg_result_side = StimulationSide.left

        if count_nonzero(differential_values.semg) == 0:
            semg_result_side = StimulationSide.both

        # ==============================================================================
        # FINALIZE THE SIDE OF STIMULATION SITE
        # ==============================================================================
        if semg_result_side is None:
            return inertial_result_side
        elif inertial_result_side == semg_result_side:
            return inertial_result_side
        else:
            return semg_result_side

    @staticmethod
    def get_center_of_mass_differential(inertial_differential: list):
        return [com_value for com_index, com_value in enumerate(inertial_differential) if
                com_index in CENTER_OF_MASS_FIELD_INDICES]

    @staticmethod
    def calculate_stimulation_energy(com_differential: list, inertial_differential: list) -> float:
        """
        Compute stimulation energy output value for the current loop cycle.

        ========================================================================================================
        Required IR-Energy = (
            [Difference between final golden standard treatment values of CoM with client’s values of CoM]
            *
            [Difference between final golden standard treatment values of 18 inertial measurements with client’s 18 values]
        )
        /
        [60 seconds duration of IR-energy muscle stimulation]
        ========================================================================================================

        :param self:
        :return: float -  Percentage of the stimulation output value
        """
        energy = (average(com_differential) * average(inertial_differential)) / 60

        return energy * 100
