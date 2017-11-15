import unittest
import json
from rdflib import ConjunctiveGraph
from falcon import testing
# from ldframe.app import init_api
from ldframe.applib.ld_frame import Frame
# from mock import patch


class FrameTestCase(testing.TestCase):
    """Test for LD Frame operations."""

    def setUp(self):
        """Set up test fixtures."""
        pass

    def test_bulk_data(self):
        """Test bulk data result."""
        with open('tests/resources/bulk_data.json') as datafile:
            result_data = datafile.read()
        with open('tests/resources/message_data.json') as datafile:
            message_data = json.load(datafile)
        ld_frame = message_data["payload"]["framingServiceInput"]["ldFrame"]
        doc_type = message_data["payload"]["framingServiceInput"]["docType"]
        source_data = message_data["payload"]["framingServiceInput"]["sourceData"]
        ld_frame = Frame(ld_frame, source_data, doc_type)
        self.assertEqual(ld_frame._bulk_data(), result_data)

    def test_bad_data(self):
        """Test merge bad data frame."""
        with open('tests/resources/message_bad_data.json') as datafile:
            message_data = json.load(datafile)
        ld_frame = message_data["payload"]["framingServiceInput"]["ldFrame"]
        doc_type = message_data["payload"]["framingServiceInput"]["docType"]
        source_data = message_data["payload"]["framingServiceInput"]["sourceData"]
        ld_frame = Frame(ld_frame, source_data, doc_type)
        with self.assertRaises(UnboundLocalError):
            ld_frame._create_ld()

    def test_doc_type(self):
        """Test get document type."""
        with open('tests/resources/message_data.json') as datafile:
            message_data = json.load(datafile)
        ld_frame = message_data["payload"]["framingServiceInput"]["ldFrame"]
        doc_type = message_data["payload"]["framingServiceInput"]["docType"]
        source_data = message_data["payload"]["framingServiceInput"]["sourceData"]
        ld_frame = Frame(ld_frame, source_data, doc_type)
        result_data = "ex:Library"
        assert(result_data == ld_frame._doc_type())

    def test_merge_data(self):
        """Test merge graphs."""
        with open('tests/resources/message_data.json') as datafile:
            message_data = json.load(datafile)
        ld_frame = message_data["payload"]["framingServiceInput"]["ldFrame"]
        doc_type = message_data["payload"]["framingServiceInput"]["docType"]
        source_data = message_data["payload"]["framingServiceInput"]["sourceData"]
        ld_frame = Frame(ld_frame, source_data, doc_type)
        assert type(ld_frame._merge_graphs()) is ConjunctiveGraph


if __name__ == "__main__":
    unittest.main()
