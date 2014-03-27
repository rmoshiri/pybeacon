import unittest
import os
import shutil
from datetime import datetime, timedelta
from logger import BeaconLogger


logfolder = 'logs'


class TestLoggerModule(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        # remove any residual logger handlers
        l = BeaconLogger()
        for handler in l._log.handlers:
            l._log.removeHandler(handler)

        # delete previous log files
        if os.path.exists(logfolder): shutil.rmtree(logfolder)

            

    def test_constructor(self):
        logger = BeaconLogger()

        # make sure log file was created
        self.assertEqual(os.path.exists(logfolder), True)

        # make sure log handlers are empty
        self.assertEqual(logger._log.handlers, [])

    def test_makedir(self):
        logger = BeaconLogger()
        logger._makedir('floob')

        # make sure the folder was created
        self.assertEqual(os.path.exists('floob'), True)

        # make sure error is raised creating folder that already exists
        self.assertEqual(logger._makedir('floob'), False)
        
        os.rmdir('floob')

    def test_get_new_log_file(self):
        logger = BeaconLogger()
        log_dir = logfolder + '/' + str(datetime.now().date())
        somefile = 'somefile.txt'
        
        # create non empty non-expired log directory
        os.makedirs(log_dir)
        open(log_dir + '/' + somefile, 'a').close()

        new_path = logger._get_new_log_file()
        expected = log_dir + '/' + str(datetime.now().hour) + '.txt'

        # make sure path is correct and old file is still there
        self.assertEqual(new_path, expected)
        self.assertEqual(os.path.exists(log_dir + '/' + somefile), True)

        # clear log directory
        shutil.rmtree(log_dir)

        new_path = logger._get_new_log_file()

        # make sure new directory is created
        self.assertEqual(new_path, expected)
        self.assertEqual(os.path.exists(log_dir), True)

    def test_future_log_expired(self):
        logger = BeaconLogger()
        future = datetime.now() + timedelta(days=1)

        logger._log_date = future
        self.assertEqual(logger._log_expired(), False)

    def test_present_log_expired(self):
        logger = BeaconLogger()
        present = datetime.now()

        logger._log_date = present
        self.assertEqual(logger._log_expired(), False)

    def test_past_log_expired(self):
        logger = BeaconLogger()

        # possible past times (past by a day and hr, just a day, just an hr)
        past = logger._log_date
        present = datetime.now()
        past_hr = present - timedelta(hours=1)
        past_day = present - timedelta(days=1)

        logger._log_date = past
        self.assertEqual(logger._log_expired(), True)
        logger._log_date = past_hr
        self.assertEqual(logger._log_expired(), True)
        logger._log_date = past_day
        self.assertEqual(logger._log_expired(), True)

    def test_assign_handler(self):
        logger = BeaconLogger()
        logger._assign_handler()

        # calculate expected handler path
        now = datetime.now()
        log_path = logfolder + '/' + str(now.date()) + '/' + str(now.hour) + '.txt'
        expected_path = os.getcwd() + '/' + log_path

        self.assertEqual(logger._log.handlers[0].baseFilename, expected_path)

        # check if we can remove and add a filehandler  
        logger._log_date = logger._log_date - timedelta(hours=2)
        logger._assign_handler()

        self.assertEqual(len(logger._log.handlers), 1)
        self.assertEqual(logger._log.handlers[0].baseFilename, expected_path)

    def test_logBeacon(self):
        print 'testing log beacon'
        logger = BeaconLogger()
        beaconID = 'SOMEBEACONID'
        rssi = 'SOMERSSI'
        logger.logBeacon(beaconID, rssi)

        # Expected log file path
        now = datetime.now()
        log_path = logfolder + '/' + str(now.date()) + '/' + str(now.hour) + '.txt'
        expected_fh_path = os.getcwd() + '/' + log_path

        # Actual logged message
        f = open(log_path, 'r')
        logged_data = f.readline().strip().split('\t')
        f.close()

        # TODO test that the date is accurate
        self.assertEqual(os.path.exists(log_path), True)
        self.assertEqual(logged_data[1], beaconID)
        self.assertEqual(logged_data[2], rssi)


if __name__ == '__main__':
    unittest.main()
