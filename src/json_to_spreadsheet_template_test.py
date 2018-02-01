from unittest import TestCase
from unittest.mock import patch

import requests

from src.json_to_spreadsheet_template import SpreadsheetCreator


class JsonToSpreadsheetTemplateTest(TestCase):

    def test_generate_spreadsheet(self):
        with patch('requests.get') as mock_client, \
                patch('openpyxl.Workbook.save') as mock_workbook:
            # given:
            http_schema_response = {'status_code': requests.codes.ok}
            mock_client.return_value = http_schema_response

            # and:
            creator = SpreadsheetCreator()

            # when:
            spreadsheet = creator.generateSpreadsheet('base_uri', [], [], 'path/to/output.xlsx')

            # then:
            self.assertTrue(spreadsheet)