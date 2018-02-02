from unittest import TestCase
from unittest.mock import patch, Mock

import requests

from src.json_to_spreadsheet_template import SpreadsheetCreator, SchemaProcessor

class SchemaProcessorTest(TestCase):

    def test_process_no_dependencies(self):
        with open('files/schema_organism.json') as schema_file:
            # given:
            schema = schema_file.read()

            # and:
            schema_processor = SchemaProcessor()

            # when:
            values = schema_processor.processTemplate(schema)

            #then:
            self.assertTrue(values)

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