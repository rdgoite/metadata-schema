from unittest import TestCase
from unittest.mock import patch, Mock

import requests

from src.json_to_spreadsheet_template import SpreadsheetCreator, SchemaProcessor

class SchemaProcessorTest(TestCase):

    def test_process_no_dependencies(self):
        with open('files/schema_organism_simplified.json') as organism_schema_file, \
            open('files/schema_familial_relationship.json') as relationship_schema_file, \
            patch('src.json_to_spreadsheet_template.SchemaDownloader.download') as mock_downloader:
            # given:
            organism_schema = organism_schema_file.read()
            relationship_schema = relationship_schema_file.read()

            # and:
            mock_downloader.side_effect = [relationship_schema]

            # and:
            schema_processor = SchemaProcessor()

            # when:
            values = schema_processor.processTemplate(organism_schema)

            #then:
            self.assertTrue(values)
            self._assert_correct_header(values)

    def _assert_correct_header(self, values):
        headers = [header for header in values if 'header' in header.keys()]
        self.assertEqual(1, len(headers))
        header = headers[0]
        expected_header = {'header': 'Process IDs',
                           'description': 'IDs of processes for which this biomaterial is an input',
                           'example': None}
        for key in expected_header:
            self.assertEqual(expected_header[key], header[key])


class JsonToSpreadsheetTemplateTest(TestCase):

    def test_generate_spreadsheet_single_schema(self):
        with patch('requests.get') as mock_client, \
                patch('openpyxl.Workbook.save') as mock_workbook:
            # given:
            http_schema_response = Mock()
            http_schema_response.status = requests.codes.ok
            with open('files/schema_organism.json') as schema_file:
                http_schema_response.json.return_value = schema_file.read()
            mock_client.return_value = http_schema_response

            # and:
            creator = SpreadsheetCreator()

            # when:
            spreadsheet = creator.generateSpreadsheet('http://schemas.humancellatlas.org', ['organism.json'],
                                                      [], 'path/to/output.xlsx')

            # then:
            self.assertTrue(spreadsheet)
