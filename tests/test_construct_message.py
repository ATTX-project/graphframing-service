import json
import unittest
from ldframe.applib.construct_message import ld_message
from mock import patch
from ldframe.applib.ld_frame import Frame


class ConstructFrameTestCase(unittest.TestCase):
    """Test for constuct message frame function."""

    def setUp(self):
        """Set up test fixtures."""
        pass

    @patch('ldframe.applib.construct_message.Publisher.push')
    @patch('ldframe.utils.file.results_path')
    @patch.object(Frame, '_bulk_data')
    def test_retrieve_called(self, mock, file_mock, publis_mock):
        """Test if retrieve graph data was called."""
        with open('tests/resources/frame_bulk_data.json') as datafile:
            result_data = datafile.read()
        with open('tests/resources/message_bulk_data.json') as datafile:
            message = json.load(datafile)
        mock.return_value = result_data
        ld_message(message)
        self.assertTrue(mock.called)

    @patch.object(Frame, '_bulk_data')
    def test_ld_error(self, mock):
        """Test if replace raises an error was called."""
        with open('tests/resources/message_bulk_data.json') as datafile:
            message = json.load(datafile)
        with self.assertRaises(UnboundLocalError):
            ld_message(message)


if __name__ == "__main__":
    unittest.main()
