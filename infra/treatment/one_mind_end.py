"""
This class will all the processing after the data is collected for one minute during treatment stage
"""
from infra.models import SessionTreatmentIPCReceived, Session


class TreatmentOneMinuteEnd:
    @staticmethod
    def process_data(name: str, session: Session):
        """
        Keep checking every 2 seconds if the IPC command from all the three sensors is received.
        :param session:
        :param name:
        :return:
        """

        # check in SessionTreatmentIPCReceived per session - all the 3 ipc commands to be set to True,
        # if yes then start processing the data from IRSensorData, SEMGSensorData, InertialSensorData
        # if no sleep(2)
