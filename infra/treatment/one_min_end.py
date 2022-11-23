"""
This class will all the processing after the data is collected for one minute during treatment stage
"""
import logging
from time import sleep

from infra.utils import get_mean, compare_with_gold_standard, INERTIAL_DATA_FIELDS, SEMG_DATA_FIELDS
from infra.models import SessionTreatmentIPCReceived, Session, SEMGSensorData, InertialSensorData, IRSensorData

logger = logging.getLogger(__name__)


class TreatmentOneMinuteSend:

    @staticmethod
    def has_received_all_ipc_commands(name: str, session: Session):
        """
        Keep checking every 2 seconds if the IPC command from all the three sensors is received.
        :param session:
        :param name:
        :return:
        """
        while True:
            logger.info(f"Processing Treatment one minute send IPC command for process name: [{name}]")
            ipc_received = TreatmentOneMinuteSend.get_session_ipc_received(session)

            if ipc_received:
                """
                If this condition is True: All the 3 required sensor one mind end commands have been received from the 
                sensors during treatment stage. 
                """
                ipc_received.processing_status = True # it is important to set this to true to avoid duplicate processing of the same session one minute
                ipc_received.save()

                """
                Start processing the data from IRSensorData, SEMGSensorData, InertialSensorData for the session
                """
                TreatmentOneMinuteSend.process_data(session)
            else:
                sleep(5)

    @staticmethod
    def get_session_ipc_received(session: Session):
        return SessionTreatmentIPCReceived.objects.filter(session=session, processing_status=False, semg_received=True,
                                                          inertial_received=True, ir_received=True).first()

    @staticmethod
    def process_data(session: Session):
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
            inertial_data = InertialSensorData.objects.filter(session=session, read_status=False)
            semg_data = SEMGSensorData.objects.filter(session=session, read_status=False)
            ir_data = IRSensorData.objects.filter(session=session, read_status=False)

            inertial_data_list = list(inertial_data.values_list(*INERTIAL_DATA_FIELDS))
            inertial_data_mean = get_mean(inertial_data_list)

            semg_data_list = list(semg_data.values_list(*SEMG_DATA_FIELDS))
            semg_data_mean = get_mean(semg_data_list)

            ir_data_list = list(ir_data.values_list('thermal'))
            ir_data_mean = get_mean(ir_data_list)

            # compare the 3 mean values with their respective gold standard
            # the gold standard value is fromm the Users gold standard model (computed after the calibration stage)
            # compute the IR energy stimulation



        except Exception as e:
            logger.info(f"Treatment IPC: There is an error during treatment one minute end data processing: [{e}]")
