import json
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
            values = schema_processor.process_template(json.loads(organism_schema))

            #then:
            self.assertTrue(values)
            self._assert_correct_biomaterial_header(values)

    def test_process_headers(self):
        # given:
        schema_processor = SchemaProcessor()

        # and:
        biomaterial_uri = 'https://schema.humancellatlas.org/type/biomaterial/organism.json'
        process_uri = 'https://schema.humancellatlas.org/type/process/sequencing/sequencing_process.json'
        file_uri = 'https://schema.humancellatlas.org/type/file/sequence_file.json'

        # when:
        biomaterial_headers = schema_processor._process_headers(biomaterial_uri)
        process_header = schema_processor._process_headers(process_uri)
        file_headers = schema_processor._process_headers(file_uri)

        # then:
        self._assert_correct_biomaterial_header(biomaterial_headers)
        self._assert_correct_process_header(process_header)
        self._assert_correct_file_headers(file_headers)

    def _assert_correct_biomaterial_header(self, biomaterial_headers):
        self._assert_correct_single_header(biomaterial_headers, {
            'header': 'Process IDs',
            'description': 'IDs of processes for which this biomaterial is an input',
            'example': None
        })

    def _assert_correct_process_header(self, process_headers):
        self._assert_correct_single_header(process_headers, {
            "header": "Protocol IDs",
            "description": "IDs of protocols which this process implements",
            "example": None
        })

    def _assert_correct_single_header(self, values, expected_header):
        headers = [header for header in values if 'header' in header.keys()]
        self.assertEqual(1, len(headers))
        header = headers[0]
        self.assertEqual(expected_header, header)

    def _assert_correct_file_headers(self, file_headers):
        headers = [header for header in file_headers if 'header' in header.keys()]
        self.assertEqual(2, len(headers))

        # and:
        biomaterial_headers = [header for header in headers if header['header'] == 'Biomaterial ID']
        self.assertEqual(1, len(biomaterial_headers))
        self.assertEqual({
            'header': 'Biomaterial ID',
            'description': 'ID of the biomaterial to which this file relates',
            'example': None
        }, biomaterial_headers[0])

        # and:
        sequencing_headers = [header for header in headers if header['header'] == 'Sequencing process ID']
        self.assertEqual(1, len(sequencing_headers))
        self.assertEqual({
            'header': 'Sequencing process ID',
            'description': 'ID of the sequencing process to which this file relates',
            'example': None
        }, sequencing_headers[0])


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
