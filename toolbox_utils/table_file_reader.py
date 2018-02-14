#!/usr/bin/python3
# -*- coding:utf-8 -*-
# Project: http://plankton-toolbox.org
# Copyright (c) 2010-2018 SMHI, Swedish Meteorological and Hydrological Institute 
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

import os
import locale
import zipfile

# This utility should work even if openpyxl is not installed, but with no Excel support.
openpyxl_installed = True
try: 
    import openpyxl
except ImportError: 
    openpyxl_installed = False
    print('Excel files not suported since openpyxl is not installed.')

class TableFileReader():
    """ 
    This class can read table oriented data from text files, Excel files or from text entries in zip files.
    The class will hold the result and it is accessible through the 'self.header()' and 'self.rows()' methods.
    It is possible to minimise the memory footprint by only loading selected columns, by name or index. 
    Directories based on the loaded data can be directly generated by the class.
     
    For usage examples see the test part at the end of the source code file.
    """
    def __init__(self,
                file_path = None, # Used for all files. 
                text_file_name = None, # Used for text files.
                excel_file_name = None, # Used for excel files.
                excel_sheet_name = None, # Used to select sheet in excel files. None = first sheet.
                zip_file_name = None, # Used for zip files.
                zip_file_entry = None, # Used for text file entries in zip files.
                select_columns_by_name = None, # Save memory, don't load all columns. Alternative 1.
                select_columns_by_index = None, # Save memory, don't load all columns. Alternative 2.
                field_delimiter = None, # None = autodetect. '\t' is recommended. 
                encoding = 'cp1252', # 'cp1252': Mostly used by windows users and accepts latin-1. 
                encoding_error_handling = 'strict', # Alternatives: 'strict', 'replace', 'ignore', 
                                                    # 'xmlcharrefreplace', 'backslashreplace'. 
                header_row = 0, # Header at row index.
                data_rows_from = 1, # First data row at row index.
                data_rows_to = None, # None = Read all rows.
                 ):
        """ """
        self._file_path = file_path
        self._text_file_name = text_file_name
        self._excel_file_name = excel_file_name
        self._excel_sheet_name = excel_sheet_name
        self._zip_file_name = zip_file_name
        self._zip_file_entry = zip_file_entry
        self._select_columns_by_name = select_columns_by_name
        self._select_columns_by_index = select_columns_by_index
        self._field_delimiter = field_delimiter
        self._encoding = encoding
        self._encoding_error_handling = encoding_error_handling
        self._header_row = header_row
        self._data_rows_from = data_rows_from
        self._data_rows_to = data_rows_to
        #
        self._header = []
        self._rows = []
        # Read data from file.
        self.read_file()
    
    def header(self):
        """ Header as list. """
        return self._header
    
    def rows(self):
        """ Rows as a list of lists. """
        return self._rows
    
    def clear(self):
        """ Call this to free memory. """
        self._header = []
        self._rows = []
        
    def read_file(self):
        """ Read files in different formats depending on parameter values
            defined in constructor. """
        # Text file.                
        if self._text_file_name is not None:
            (self._header, self._rows) = self._read_text_file()
        # Excel.    
        elif self._excel_file_name is not None:
            (self._header, self._rows) = self._read_excel_file()
        # Text file in zip.    
        elif self._zip_file_name:
            (self._header, self._rows) = self._read_zip_entry()
        else:
#             raise UserWarning('File name is missing.')
            print('Warning: TableFileReader.reload_file: File name is missing.')

    def create_dictionary(self,
                        # By name. One item.
                        key_column_by_name = None, # Example: 'aaa'
                        value_column_by_name = None, # Example: 'bbb'
                        # By index. One item.
                        key_column_by_index = None, # Example: 0
                        value_column_by_index = None, # Example: 1
# TODO:
#                         # By name. List of items.
#                         key_columns_by_name = None, # Example: ['aaa', 'bbb']
#                         value_columns_by_name = None, # Example: ['ccc', 'ddd']
#                         # By index. List of items.
#                         key_columns_by_index = None, # Example: [0, 1]
#                         value_columns_by_index = None, # Example: [2, 3]
#                         # Column and value delimiters for lists.
#                         column_delimiter_for_keys = None, # Example: None (= Tuple), '+', etc.
#                         value_delimiter_for_keys = None, # Example: None(= Tuple), '+', etc. 
                        ):
        """ Generates a dictionary based on one or multiple columns for key and value. """
        dictionary = {}
        keyindex = None
        valueindex = None
        # Key.
        if key_column_by_name is not None:
            for index, field in enumerate(self._header):
                if field == key_column_by_name:
                    keyindex = index
                    break
        elif key_column_by_index is not None:
            if key_column_by_index < len(self._header):
                keyindex = key_column_by_index
        # Value.
        if value_column_by_name is not None:
            for index, field in enumerate(self._header):
                if field == value_column_by_name:
                    valueindex = index
                    break
        elif value_column_by_index is not None:
            if value_column_by_index < len(self._header):
                valueindex = value_column_by_index
        # Create dictionary.
        if (keyindex is not None) and (valueindex is not None):
            for row in self._rows:
                if row[keyindex]:
                    dictionary[row[keyindex]] = row[valueindex]
        #         
        if len(dictionary) == 0:            
            print('Failed to create dictionary. Keyindex/valueindex: ' + 
                   unicode(keyindex) + '/' + unicode(valueindex))            
        #
        return dictionary
        
    def translate_header(self, from_to_dict):
        """ TODO: """
        
    def translate_rows(self, from_to_dict):
        """ TODO: """
        
    def _read_text_file(self):
        """ Private method. Use read_file() above. """
        table_header = [] 
        table_rows = []
        # File path and name.
        filename = self._text_file_name
        if self._file_path and self._text_file_name:
            filename = os.path.join(self._file_path, self._text_file_name)
        if filename is None:
            raise UserWarning('File name is missing.')
        if not os.path.exists(filename):
            raise UserWarning('File is not found.  File: ' + filename)
        # Get encoding.
        if self._encoding is None:
            self._encoding = locale.getpreferredencoding()
        # 
        columnsbyindex = None
        # Read file.
        with open(filename, 'r') as infile:
            fielddelimiter = None
            # Iterate over rows in file.            
            for rowindex, row in enumerate(infile):
                if (self._data_rows_to is not None) and (rowindex > self._data_rows_to):
                    break # Break loop if data_row_to is defined and exceeded.
                # Convert to unicode.
                row = unicode(row, self._encoding, self._encoding_error_handling)
                if rowindex == self._header_row:
                    # Header.
                    fielddelimiter = self._get_field_delimiter(row)
                    row = [item.strip() for item in row.split(fielddelimiter)]
                    columnsbyindex = self._prepare_columnsbyindex(row)
                    table_header = self._get_row_based_on_columnsbyindex(row, columnsbyindex)
                elif rowindex >= self._data_rows_from:
                    # Row.
                    if len(row.strip()) == 0: 
                        continue # Don't add empty rows.
                    row = [item.strip() for item in row.split(fielddelimiter)]
                    table_rows.append(self._get_row_based_on_columnsbyindex(row, columnsbyindex))
        #                                                      
        return (table_header, table_rows)
    
    def _prepare_columnsbyindex(self, header_row):
        """ Private method. """
        columnsbyindex = None
        if self._select_columns_by_index:
            columnsbyindex = self._select_columns_by_index
        #
        elif self._select_columns_by_name:
            columnsbyindex = [] # Overrides selected_columns_by_index.
            for columnname in self._select_columns_by_name:
                foundindex = None
                for headerrowindex, headeritem in enumerate(header_row):
                    if columnname == headeritem:
                        foundindex = headerrowindex
                        break        
                columnsbyindex.append(foundindex)
        # 
        return columnsbyindex       

    def _get_row_based_on_columnsbyindex(self, row, columns_by_index):
        """ Private method. """
        new_row = []
        if columns_by_index is None:
            return row
        else:
            for index in columns_by_index:
                if index is None:
                    new_row.append('')
                elif len(row) > index:
                    new_row.append(row[index])
                else:
                    new_row.append('')
        return new_row

    def _read_excel_file(self):
        """ Private method. Use read_file() above. """
        table_header = [] 
        table_rows = []
        #
        if openpyxl_installed == False:
            raise UserWarning('Can\'t read .xlsx files ("openpyxl" is not installed).')
        # File path and name.
        filename = self._excel_file_name
        if self._file_path and self._excel_file_name:
            filename = os.path.join(self._file_path, self._excel_file_name)
        if filename is None:
            raise UserWarning('File name is missing.')
        if not os.path.exists(filename):
            raise UserWarning('File is not found.  File: ' + filename)
        # 
        self._columnsbyindex = None
        #
        try:
            workbook = openpyxl.load_workbook(filename, use_iterators = True) # Supports big files.
            if workbook == None:
                raise UserWarning('Can\'t read Excel (.xlsx) file.')
            worksheet = None
            if self._excel_sheet_name:
                # 
                if self._excel_sheet_name in workbook.get_sheet_names():
                    worksheet = workbook.get_sheet_by_name(name = self._excel_sheet_name)
                else:
                    raise UserWarning('Excel sheet ' + self._excel_sheet_name + ' not available.')      
            else:
                # Use the first sheet if not specified.
                worksheet = workbook.get_sheet_by_name(name = workbook.get_sheet_names()[0])
            #
            for rowindex, row in enumerate(worksheet.iter_rows()):
                if (self._data_rows_to is not None) and (rowindex > self._data_rows_to):
                    break # Break loop if data_row_to is defined and exceeded.
                elif rowindex == self._header_row:
                    # Header.
                    newrow = []
                    for cell in row:
                        value = cell.value
                        if value == None:
                            newrow.append('')
                        else:
                            newrow.append(unicode(value).strip())
                    #
                    columnsbyindex = self._prepare_columnsbyindex(newrow)
                    table_header = self._get_row_based_on_columnsbyindex(newrow, columnsbyindex)
                elif rowindex >= self._data_rows_from:
                    # Row.
                    newrow = []
                    for cell in row:
                        value = cell.value
                        if value == None:
                            newrow.append('')
                        else:
                            newrow.append(unicode(value).strip())
                    #
                    if len(''.join(newrow)) == 0:
                        continue # Don't add empty rows.
                    newrow = self._get_row_based_on_columnsbyindex(newrow, columnsbyindex)
                    table_rows.append(newrow)
            #
            workbook._archive.close()
            #
            return (table_header, table_rows)
        #  
        except Exception as e:
            msg = 'Failed to read from file. File name: ' + filename + '. Exception: ' + unicode(e)
            print(msg)
            raise

    def _read_zip_entry(self):
        """ Private method. Use read_file() above. """
        table_header = [] 
        table_rows = []
        #
        filename = self._zip_file_name
        if self._file_path and self._zip_file_name:
            filename = os.path.join(self._file_path, self._zip_file_name)
        #
        if not zipfile.is_zipfile(filename):
            raise UserWarning('Selected file is not a valid zip file: ' + filename)
        # Get encoding.
        if self._encoding is None:
            self._encoding = locale.getpreferredencoding() # Encoding depends user or system preferences.
        #
        with zipfile.ZipFile(filename, 'r') as infile:
            if self._zip_file_entry not in infile.namelist():
                raise UserWarning('The entry ' + self._zip_file_entry + ' is missing in ' + filename)
            #
            try:
                fielddelimiter = None
                # Iterate over rows in zip file entry.            
                with infile.open(self._zip_file_entry) as zipentry:
                    for rowindex, row in enumerate(zipentry):
                        if (self._data_rows_to is not None) and (rowindex > self._data_rows_to):
                            break # Break loop if data_row_to is defined and exceeded.
                        # Convert to unicode.
                        row = unicode(row, self._encoding, self._encoding_error_handling)
                        if rowindex == self._header_row:
                            # Header.
                            fielddelimiter = self._get_field_delimiter(row)
                            row = [item.strip() for item in row.split(fielddelimiter)]
                            columnsbyindex = self._prepare_columnsbyindex(row)
                            table_header = self._get_row_based_on_columnsbyindex(row, columnsbyindex)
                        elif rowindex >= self._data_rows_from:
                            # Row.
                            if len(row.strip()) == 0: 
                                continue # Don't add empty rows.
                            row = [item.strip() for item in row.split(fielddelimiter)]
                            table_rows.append(self._get_row_based_on_columnsbyindex(row, columnsbyindex))
            #
            except Exception as e:
                msg = 'Can\'t read zip file. Entry name: ' + self._zip_file_entry + '. Exception: ' + unicode(e)
                print(msg)
                raise UserWarning(msg)
            #

        return (table_header, table_rows)

    def _get_field_delimiter(self, header_row):
        """ Private method. """
        if (self._field_delimiter is not None):
            return self._field_delimiter
        # Autodetect. 
        if '\t' in header_row: return '\t'
        elif ';' in header_row: return ';'
        elif ',' in header_row: return ','
        # Default if not found.
        return '\t' # Default.


# ===== TEST =====

if __name__ == "__main__":
    """ Used for testing. 
        Run table_file_writer to create test files.
    """
    
    print('\n=== TEST: Text files. ===')
    try:
        tablefilereader = TableFileReader(
                    file_path = '../test_data',
                    text_file_name = 'test_text_writer.txt',                 
    #                 select_columns_by_index = [1, 0],
                    select_columns_by_name = ['bbb', 'aaa'],
                     )
        print('Header: ' + unicode(tablefilereader.header()))
        print('Rows:   ' + unicode(tablefilereader.rows()))
        testdict = tablefilereader.create_dictionary(key_column_by_name = 'aaa', value_column_by_name = 'bbb')
        print('Dict by name: ' + unicode(testdict))
        testdict = tablefilereader.create_dictionary(key_column_by_index = 1, value_column_by_index = 0)
        print('Dict by index: ' + unicode(testdict))
    except Exception as e:
        print('Test failed: ' + unicode(e))

    print('\n=== TEST: Excel files. ===')
    try:
        tablefilereader = TableFileReader(
                    file_path = '../test_data',
                    excel_file_name = 'test_text_writer.xlsx',
                    select_columns_by_index = [1, 0],
    #                 select_columns_by_name = ['bbb', 'aaa'],
                    )
        print('Header: ' + unicode(tablefilereader.header()))
        print('Rows:   ' + unicode(tablefilereader.rows()))
        testdict = tablefilereader.create_dictionary(key_column_by_name = 'aaa', value_column_by_name = 'bbb')
        print('Dict by name: ' + unicode(testdict))    #
        testdict = tablefilereader.create_dictionary(key_column_by_index = 1, value_column_by_index = 0)
        print('Dict by index: ' + unicode(testdict))
    except Exception as e:
        print('Test failed: ' + unicode(e))

    print('\n=== TEST: Zip files. ===')
    try:
        tablefilereader = TableFileReader(
                    file_path = '../test_data',
                    zip_file_name = 'test_text_writer.zip', 
                    zip_file_entry = 'test_text_writer.txt',
    #                 select_columns_by_index = [1, 0],
                    select_columns_by_name = ['aaa', 'bbb', 'eee', 'ccc'], # Column 'eee' not in file.
                    )
        print('Header: ' + unicode(tablefilereader.header()))
        print('Rows:   ' + unicode(tablefilereader.rows()))
        testdict = tablefilereader.create_dictionary(key_column_by_name = 'aaa', value_column_by_name = 'ccc')
        print('Dict by name:  ' + unicode(testdict))
        testdict = tablefilereader.create_dictionary(key_column_by_index = 0, value_column_by_index = 2)
        print('Dict by index: ' + unicode(testdict))
    except Exception as e:
        print('Test failed: ' + unicode(e))

