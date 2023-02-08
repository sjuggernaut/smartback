# Needed for tests
import django

django.setup()

from django.test import TestCase
from unittest.mock import patch, Mock
from django.contrib.auth.models import User

from infra.assemblers.command_assemblers.treatment.one_min_end import TreatmentOneMinuteEndDataProcessor
from infra.domain.dataclasses import *
from infra.models import Session, SessionTreatmentIPCReceived, TreatmentInertialData, SessionTypes, StatusChoices
from infra.serializers import InertialSensorDataSerializer


class TreatmentOneMinuteEndDataProcessorTest(TestCase):
    def test_givenUserGoldStandardAndMean_whenCalculateDifferentialValues_thenReturnDifferentialValues(self):
        gold_standard = DataClassTreatmentGoldStandardForUser(semg=[3.1, 3.2, 3.3, 3.4, 3.8], inertial=[1.9, 2.9, 2.3])
        user_data_mean = DataClassUserTreatmentMean(semg=[1, 1.4, 1.8, 2.9, 3.2], inertial=[1.6, 1.7, 1.8])

        differential_values = TreatmentOneMinuteEndDataProcessor.calculate_differential_values(gold_standard,
                                                                                               user_data_mean)
        self.assertIsInstance(differential_values, DataClassDifferentialValuesForTreatment)

        self.assertIsNotNone(differential_values.semg)
        self.assertIsNotNone(differential_values.inertial)

        self.assertTrue(type(differential_values.semg) is list)
        self.assertTrue(type(differential_values.inertial) is list)

    @patch('infra.assemblers.command_assemblers.treatment.one_min_end.INERTIAL_DATA_FIELDS',
           ['field1', 'field2', 'field2'])
    def test_givenDifferentialValues_whenCalculateStimulationSite_thenReturnSiteOfStimulationRight(self):
        differential_values = DataClassDifferentialValuesForTreatment(semg=[-2.2999999999999998, 0.9999999999999998],
                                                                      inertial=[1.9, 2.9, 2.3])
        stimulation_site = TreatmentOneMinuteEndDataProcessor.calculate_stimulation_site(differential_values)
        self.assertEqual(stimulation_site, StimulationSide.right)

    @patch('infra.assemblers.command_assemblers.treatment.one_min_end.INERTIAL_DATA_FIELDS',
           ['field1', 'field2', 'field2'])
    def test_givenDifferentialValues_whenCalculateStimulationSite_thenReturnSiteOfStimulationLeft(self):
        differential_values = DataClassDifferentialValuesForTreatment(semg=[-2.2999999999999998, 0.9999999999999998],
                                                                      inertial=[-1.9, -2.9, -2.3])
        stimulation_site = TreatmentOneMinuteEndDataProcessor.calculate_stimulation_site(differential_values)
        self.assertEqual(stimulation_site, StimulationSide.left)

    @patch('infra.assemblers.command_assemblers.treatment.one_min_end.INERTIAL_DATA_FIELDS',
           ['field1', 'field2', 'field2'])
    def test_givenDifferentialValues_whenCalculateStimulationSite_thenReturnSiteOfStimulationBoth(self):
        differential_values = DataClassDifferentialValuesForTreatment(semg=[-2.2999999999999998, 0.9999999999999998],
                                                                      inertial=[-1.9, -2.9, 2.3])
        stimulation_site = TreatmentOneMinuteEndDataProcessor.calculate_stimulation_site(differential_values)
        self.assertEqual(stimulation_site, StimulationSide.both)

    @patch('infra.assemblers.command_assemblers.treatment.one_min_end.INERTIAL_DATA_FIELDS',
           ['field1', 'field2', 'field2'])
    def test_givenZerosAsSEMGDifferentialValues_whenCalculateStimulationSite_thenReturnSiteOfStimulationBoth(self):
        differential_values = DataClassDifferentialValuesForTreatment(semg=[0.0, 0.0],
                                                                      inertial=[1.9, 2.9, 2.3])
        stimulation_site = TreatmentOneMinuteEndDataProcessor.calculate_stimulation_site(differential_values)
        self.assertEqual(stimulation_site, StimulationSide.both)

    def test_givenDifferentialValues_whenCalculateStimulationOutputEnergy_thenReturnEnergyOutputPercentage(self):
        com_differential = [1.9, 2.9, 2.3]
        inertial_differential = [1.9, 2.9, 2.3]
        stimulation_energy = TreatmentOneMinuteEndDataProcessor.calculate_stimulation_energy(com_differential,
                                                                                             inertial_differential)
        self.assertIsNotNone(stimulation_energy)
        self.assertGreater(stimulation_energy, 9)

    @patch('infra.assemblers.command_assemblers.treatment.one_min_end.CENTER_OF_MASS_FIELD_INDICES',
           [0, 2, 4, 6])
    def test_givenInertialDifferentialValues_whenCalculateCenterOfMassDiff_thenReturnCOMDifferentialValues(self):
        inertial_differentials = [1.1, 2.1, 1.2, 2.2, 1.3, 2.3, 1.4, 2.4, 1.5, 2.5]
        com_differentials = TreatmentOneMinuteEndDataProcessor.get_center_of_mass_differential(inertial_differentials)
        self.assertIsNotNone(com_differentials)
        self.assertEqual(com_differentials, [1.1, 1.2, 1.3, 1.4])

    def test_givenIPCCommands_whenIsIpcCommandsReceivedWithProcessingStatusFalse_thenReturnIPCCommandsResultTrue(self):
        user = User.objects.create_user(username='test_user')
        session = Session(user=user)
        session.save()
        session_ipc_received_data = SessionTreatmentIPCReceived(session=session,
                                                                processing_status=False,
                                                                semg_received=True,
                                                                inertial_received=True,
                                                                ir_received=True)
        session_ipc_received_data.save()
        is_ipc_commands_received = TreatmentOneMinuteEndDataProcessor.is_ipc_commands_received(session)

        self.assertTrue(is_ipc_commands_received.session_exists)
        self.assertIsNotNone(is_ipc_commands_received.session_instance)
        self.assertIsInstance(is_ipc_commands_received.session_instance, SessionTreatmentIPCReceived)

    def test_givenIPCCommands_whenIsIpcCommandsReceivedWithProcessingStatusFalse_thenReturnIPCCommandsResultFalse(self):
        user = User.objects.create_user(username='test_user')
        session = Session(user=user)
        session.save()
        session_ipc_received_data = SessionTreatmentIPCReceived(session=session,
                                                                processing_status=False,
                                                                semg_received=False,
                                                                inertial_received=False,
                                                                ir_received=True)
        session_ipc_received_data.save()
        is_ipc_commands_received = TreatmentOneMinuteEndDataProcessor.is_ipc_commands_received(session)

        self.assertFalse(is_ipc_commands_received.session_exists)
        self.assertIsNone(is_ipc_commands_received.session_instance)
        self.assertNotIsInstance(is_ipc_commands_received.session_instance, SessionTreatmentIPCReceived)

    def test_givenIPCCommands_whenIsIpcCommandsReceivedWithProcessingStatusTrue_thenReturnIPCCommandsResultFalse(self):
        user = User.objects.create_user(username='test_user')
        session = Session(user=user)
        session.save()
        session_ipc_received_data = SessionTreatmentIPCReceived(session=session,
                                                                processing_status=True,
                                                                semg_received=True,
                                                                inertial_received=True,
                                                                ir_received=True)
        session_ipc_received_data.save()
        is_ipc_commands_received = TreatmentOneMinuteEndDataProcessor.is_ipc_commands_received(session)

        self.assertFalse(is_ipc_commands_received.session_exists)
        self.assertIsNone(is_ipc_commands_received.session_instance)
        self.assertNotIsInstance(is_ipc_commands_received.session_instance, SessionTreatmentIPCReceived)

    # def test_givenOneIPCCommand_whenCheckAllIpcCommands_thenReturn

    def test_givenSessionTreatmentIPCReceived_whenUpdate_ipc_processing_status_thenProcessingStatusIsTrue(self):
        user = User.objects.create_user(username='test_user')
        session = Session.objects.create(user=user)
        SessionTreatmentIPCReceived.objects.create(session=session, processing_status=False, semg_received=True,
                                                   inertial_received=True, ir_received=True)
        TreatmentOneMinuteEndDataProcessor.update_ipc_processing_status(session)

        ipc_received_updated = SessionTreatmentIPCReceived.objects.filter(session=session, processing_status=True,
                                                                          semg_received=True, inertial_received=True,
                                                                          ir_received=True)

        self.assertEqual(ipc_received_updated.count(), 1)
        self.assertTrue(ipc_received_updated.first().processing_status)

    def test_givenSessionTreatmentIPCReceived_whenUpdate_ipc_processing_status_thenProcessingStatusIsFalse(self):
        user = User.objects.create_user(username='test_user')
        session = Session.objects.create(user=user)
        SessionTreatmentIPCReceived.objects.create(session=session, processing_status=False, semg_received=True,
                                                   inertial_received=True, ir_received=False)
        TreatmentOneMinuteEndDataProcessor.update_ipc_processing_status(session)

        ipc_received_updated = SessionTreatmentIPCReceived.objects.filter(session=session, processing_status=True,
                                                                          semg_received=True, inertial_received=True,
                                                                          ir_received=True)

        self.assertEqual(ipc_received_updated.count(), 0)
        self.assertIsNone(ipc_received_updated.first())

    def test_givenInertialSensorDataRows_whenSet_treatment_data_read_status_thenUpdateReadStatus(self):
        user = User.objects.create_user(username='test_user')
        session = Session.objects.create(user=user)

        data = {
            "l5s1_lateral": "1.4",
            "l5s1_axial": "1.4",
            "l5s1_flexion": "2.4",
            "l4l3_lateral": "1.4",
            "l4l3_axial": "1.4",
            "l4l3_flexion": "2.4",
            "l1t12_lateral": "1.4",
            "l1t12_axial": "1.4",
            "l1t12_flexion": "2.4",
            "t9t8_lateral": "1.4",
            "t9t8_axial": "1.4",
            "t9t8_flexion": "2.4",
            "t1c7_lateral": "1.4",
            "t1c7_axial": "1.4",
            "t1c7_flexion": "2.4",
            "c1head_lateral": "1.4",
            "c1head_axial": "1.4",
            "c1head_flexion": "2.4",
            "com_posx": "2.4",
            "com_posy": "2.4",
            "com_posz": "2.4",
            "session": session.pk
        }

        records_created = 0
        while records_created < 10:
            serializer = InertialSensorDataSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            records_created += 1

        self.assertEqual(TreatmentInertialData.objects.count(), 10)
        TreatmentOneMinuteEndDataProcessor.set_treatment_data_read_status(session)
        self.assertEqual(TreatmentInertialData.objects.filter(session=session, read_status=True).count(), 10)

    def test_givenTreatmentSession_whenCreate_new_ipc_treatment_record_thenCreateIPCRow(self):
        user = User.objects.create_user(username='test_user')
        session = Session.objects.create(user=user, type=SessionTypes.TREATMENT, status=StatusChoices.STARTED)
        TreatmentOneMinuteEndDataProcessor.create_new_ipc_treatment_record(session)
        ipc_record = SessionTreatmentIPCReceived.objects.filter(session=session)
        self.assertFalse(ipc_record.first().inertial_received)
        self.assertFalse(ipc_record.first().semg_received)
        self.assertFalse(ipc_record.first().ir_received)

    def test_givenCalibrationSession_whenCreate_new_ipc_treatment_record_thenSkipCreateIPCRow(self):
        user = User.objects.create_user(username='test_user')
        session = Session.objects.create(user=user, type=SessionTypes.CALIBRATION, status=StatusChoices.STARTED)
        with self.assertLogs(level='INFO') as logs:
            TreatmentOneMinuteEndDataProcessor.create_new_ipc_treatment_record(session)
            ipc_record = SessionTreatmentIPCReceived.objects.filter(session=session)
            self.assertIsNone(ipc_record.first())
            self.assertIn('Skipping creation', logs.output[0])


