#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# Copyright (c) 2015 SMHI, Swedish Meteorological and Hydrological Institute 
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).
#
from __future__ import unicode_literals

from SOAPpy import WSDL
import table_file_reader
import table_file_writer

class WormsMarineSpecies(object):
    """ Utility for WoRMS access. 
        WoRMS, World Register of Marine Species. http://marinespecies.org """
        
    def __init__(self):
        """ """
        self._worms_ws = WormsWebservice()
        
    def generate_tree_from_species_list(self,
                                       in_file_path = 'test_data',
                                       in_file_name = 'worms_indata.txt',
                                       out_file_path = 'test_data',
                                       out_file_name = 'worms_outdata.txt',
                                       in_scientific_name_column = 'NOMAC Scientific name',
                                       in_rank_column = 'NOMAC Rank',
                                       in_taxon_id_column = 'NOMAC AphiaID', # To be used for homonym problems.
                                       ):
        """ """
        # Indata file.
        tablefilereader = table_file_reader.TableFileReader(
            file_path = in_file_path,
            text_file_name = in_file_name,
            select_columns_by_name = [in_scientific_name_column, in_rank_column, in_taxon_id_column]                 
            )
        # Outdata file.
        tablefilewriter = table_file_writer.TableFileWriter(
            file_path = out_file_path,
            text_file_name = out_file_name,
            )
        #
        taxa_dict = {} # taxon_id: {taxon_id: '', scientific_name: '', rank: '', parent_id: '', etc.}
        #
        for row in tablefilereader.rows():
            scientific_name = row[0]
            rank = row[1]
            taxon_id = row[2]
            #
            if rank == 'Species':
                #
                species_dict = None
                try:
                    species_dict = self.find_valid_taxon(scientific_name, rank)
                except Exception as e:
                    print('Exception: ' + unicode(e))
                #
                if species_dict is None:
                    if taxon_id:
                        species_dict = self.get_aphia_name_by_id(taxon_id.replace('AphiaID:', '').strip())
                #
                if species_dict is None:
                    print('Species not in WoRMS: ' + scientific_name)
                    
                else:
                    species_id = species_dict['AphiaID']
                    taxa_dict[species_id] = species_dict
                    # Iterate over classification. Create taxa and classification info string.
                    worms_classification_list = self._worms_ws.get_aphia_classification_by_id(species_id)
                    parent_id = None
                    classification_strings = []
                    for taxon in worms_classification_list:
                        taxon_id = taxon['AphiaID']
                        classification_strings.append('[' + taxon['rank'] +'] ' + taxon['scientificname'])
                        if taxon_id not in taxa_dict:
                            taxa_dict[taxon_id] = taxon
                            taxa_dict[taxon_id]['classification'] = ' - '.join(classification_strings)
                            if parent_id:
                                taxa_dict[taxon_id]['parent_id'] = parent_id
                        parent_id = taxon['AphiaID']
                    # The last one is the species parent.
                    taxa_dict[species_id]['parent_id'] = parent_id
                    # Note: This is not a part of the classification, but useful.
                    classification_strings.append('[' + species_dict['rank'] +'] ' + species_dict['scientificname'])
                    taxa_dict[species_id]['classification'] = ' - '.join(classification_strings)

        # Add info.
        for taxon in taxa_dict.values():
            taxon_class = None
            taxon_class_id = ''
            parent_id = taxon.get('AphiaID', None)
            while parent_id:
                parent_taxon = taxa_dict[parent_id]
                if parent_taxon.get('rank', '') == 'Class':
                    taxon_class = parent_taxon['scientificname']
                    taxon_class_id = 'AphiaID:' + unicode(parent_taxon['AphiaID'])
                #
                parent_id = parent_taxon.get('parent_id', None)
            #
            if taxon_class:
                taxon['class'] =  taxon_class
                taxon['class_id'] =  taxon_class_id
        #
        table_header = ['scientific_name', 'rank', 'taxon_id', 'parent_id', 'class', 'class_id', 'classification']
        table_rows = []
        for row in taxa_dict.values():
            outrow = []
            for item in ['scientificname', 'rank', 'AphiaID', 'parent_id', 'class', 'class_id', 'classification']:
                outrow.append(unicode(row.get(item, '')))
            table_rows.append(outrow)
        #
        tablefilewriter.write_file(table_header, table_rows)


    def find_valid_taxon(self, 
                         scientific_name, 
                         rank = None): # Used to reduce some homonym problems.
        """ """
        worms_records = self._worms_ws.get_aphia_records(scientific_name, 
                                                        like='false', 
                                                        fuzzy='false', 
                                                        marine_only='false', 
                                                        offset = 1, 
                                                        )
        number_of_matches = 0
        accepted_taxon = None
        for taxon in worms_records:
            if taxon.get('status', '') == 'accepted':
                if rank:
                    if taxon.get('rank', '') == rank:
                        accepted_taxon = taxon
                        number_of_matches += 1
                else:
                    accepted_taxon = taxon
                    number_of_matches += 1
        #
        if number_of_matches == 0:
            raise UserWarning('No taxa matched. Scientific name: ' + scientific_name)
        if number_of_matches > 1:
            raise UserWarning('Multiple taxa matched. Scientific name: ' + scientific_name)
        #
        return accepted_taxon

#     def create_worms_dict(self, scientific_name, 
#                                 aphia_id = None):
#         """ """
#         worms_dict = {}        
#         # GetAphia ID.
#         if aphia_id is None:
#             aphia_id = self.get_aphia_id(scientific_name, marine_only = 'false')
#         #
#         if not aphia_id:
#             return worms_dict
#         #          
#         # Aphia record.
#         aphia_dict = self.get_aphia_record_by_id(aphia_id)
#         if not aphia_dict:
#             return worms_dict           
#         #
#         worms_dict['worms_status'] = self._get_value(aphia_dict, 'status')
#         worms_dict['worms_unaccept_reason'] = self._get_value(aphia_dict, 'unacceptreason')
# 
#         worms_dict['worms_valid name'] = self._get_value(aphia_dict, 'valid_name')
#         worms_dict['worms_valid authority'] = self._get_value(aphia_dict, 'valid_authority')
# 
#         worms_dict['worms_rank'] = self._get_value(aphia_dict, 'rank')
# 
#         worms_dict['worms_kingdom'] = self._get_value(aphia_dict, 'kingdom')
#         worms_dict['worms_phylum'] = self._get_value(aphia_dict, 'phylum')
#         worms_dict['worms_class'] = self._get_value(aphia_dict, 'class')
#         worms_dict['worms_order'] = self._get_value(aphia_dict, 'order')
#         worms_dict['worms_family'] = self._get_value(aphia_dict, 'family')
#         worms_dict['worms_genus'] = self._get_value(aphia_dict, 'genus')
#         worms_dict['worms_sscientific name'] = self._get_value(aphia_dict, 'scientificname')
#         worms_dict['worms_authority'] = self._get_value(aphia_dict, 'authority')
# 
#         worms_dict['worms_url'] = self._get_value(aphia_dict, 'url')
#         worms_dict['worms_lsid'] = self._get_value(aphia_dict, 'lsid')
#         worms_dict['worms_aphia_id'] = self._get_value(aphia_dict, 'AphiaID')
#         worms_dict['worms_valid_aphia_id'] = self._get_value(aphia_dict, 'valid_AphiaID')
#         
#         worms_dict['worms_citation'] = self._get_value(aphia_dict, 'citation')
#         
#         # Classification.
#         classification_string = ''
#         classification = self.get_aphia_classification_by_id(aphia_id)
#         if classification:    
#             classification_string = unicode(classification.rank) + ': ' + unicode(classification.scientificname)
#             while classification.child:
#                 classification = classification.child
#                 if (classification.rank and classification.scientificname):
#                     classification_string += ' - ' + unicode(classification.rank) + ': ' + unicode(classification.scientificname)        
#         worms_dict['worms_classification'] = classification_string
#         
#         # Synonyms.
#         synonym_list = []
#         synonyms = self.get_aphia_synonyms_by_id(aphia_id)
#         if synonyms:
#             for synonym in synonyms:
#                 if (synonym.scientificname and synonym.authority):
#                     synonym_list.append(unicode(synonym.scientificname) + ' ' + unicode(synonym.authority))
#         worms_dict['worms_synonym_list'] = synonym_list
#         #        
#         return worms_dict


class WormsWebservice(object):
    """ SOAP calls to the web service at WoRMS, World Register of Marine Species.
        More info at: http://www.marinespecies.org/aphia.php?p=webservice. 
    """
    def __init__(self):
        """ """
        self._wsdl_object = WSDL.Proxy('http://www.marinespecies.org/aphia.php?p=soap&wsdl=1')
        
    def get_aphia_id(self, scientific_name,
                           marine_only = 'false'):
        """ Get the (first) exact matching AphiaID for a given name.
            Parameters:
                marine_only: limit to marine taxa. Default=true.
        """
        aphia_id = self._wsdl_object.getAphiaID(scientific_name, 
                                                marine_only)
        return aphia_id # Integer or None.

    def get_aphia_records(self, scientific_name, 
                                like = 'false', # Exact match by default.
                                fuzzy = 'false', # Exact match by default.
                                marine_only = 'false', # Brackish species wanted.
                                offset = 1): # Note: Iterate if len(aphia_records) = 50.
        """ Get one or more matching (max. 50) AphiaRecords for a given name.
            Parameters:
                like: add a '%'-sign added after the ScientificName (SQL LIKE function). Default=true.
                fuzzy: fuzzy matching. Default=true.
                marine_only: limit to marine taxa. Default=true.
                offset: starting recordnumber, when retrieving next chunck of (50) records. Default=1.
        """
        worms_records = self._wsdl_object.getAphiaRecords(scientific_name, 
                                              like, fuzzy, marine_only, offset)
        # Convert from SOAPs structType to Python.
        records = []
        if worms_records:
            for aphia_record in worms_records:
                record = dict((key, getattr(aphia_record, key)) for key in aphia_record._keys())
                records.append(record)
        #
        return records
        
    def get_aphia_name_by_id(self, aphia_id):
        """ Get the correct name for a given AphiaID. """
        scientific_name = self._wsdl_object.getAphiaNameByID(aphia_id)
        return unicode(scientific_name) # String

    def get_aphia_record_by_id(self, aphia_id):
        """ Get the complete Aphia Record for a given AphiaID. """
        worms_record = self._wsdl_object.getAphiaRecordByID(aphia_id)
        # Convert from SOAPs structType to Python.
        record = None
        if worms_record:
            record = dict((key, getattr(worms_record, key)) for key in worms_record._keys())
        #
        return record
        
    def get_aphia_record_by_ext_id(self, ext_id, ext_type = 'tsn'):
        """ Get the Aphia Record for a given external identifier. 
            type: Should have one of the following values:
                'bold': Barcode of Life Database (BOLD) TaxID
                'dyntaxa': Dyntaxa ID
                'eol': Encyclopedia of Life (EoL) page identifier
                'fishbase': FishBase species ID
                'iucn': IUCN Red List Identifier
                'lsid': Life Science Identifier
                'ncbi': NCBI Taxonomy ID (Genbank)
                'tsn': ITIS Taxonomic Serial Number
        """
        worms_record = self._wsdl_object.getAphiaRecordByExtID(ext_id, ext_type)
        # Convert from SOAPs structType to Python.
        record = None
        if worms_record:
            record = dict((key, getattr(worms_record, key)) for key in worms_record._keys())
        #
        return record

    def get_aphia_records_by_names(self, scientific_names, 
                                         like = 'true', 
                                         fuzzy = 'true',
                                         marine_only = 'false'):
        """ For each given scientific name, try to find one or more AphiaRecords.
            This allows you to match multiple names in one call. Limited to 500 names at once for performance reasons. 
            Parameters:
                like: add a '%'-sign after the ScientificName (SQL LIKE function). Default=false.
                fuzzy: fuzzy matching. Default=true.
                marine_only: limit to marine taxa. Default=true.
        """
        worms_records = self._wsdl_object.getAphiaRecordsByNames(
                                                    scientific_names,
                                                    like = 'false', # Exact match by default.
                                                    fuzzy= 'false', # Exact match by default.
                                                    marine_only= 'false', # Brackish species wanted.
                                                    )
        # Convert from SOAPs structType to Python.
        name_records = []
        if worms_records:
            for name_record in worms_records:
                records = []
                for worms_record in name_record:
                    record = dict((key, getattr(worms_record, key)) for key in worms_record._keys())
                    records.append(record)
                name_records.append(records)
        #
        return name_records
        
    def get_aphia_records_by_vernacular(self, vernacular, 
                                              like = 'true', 
                                              offset = 1):
        """ Get one or more Aphia Records (max. 50) for a given vernacular.
            Parameters:
                like: add a '%'-sign before and after the input (SQL LIKE '%vernacular%' function). Default=false.
                offset: starting record number, when retrieving next chunck of (50) records. Default=1.
        """
        worms_records = self._wsdl_object.getAphiaRecordsByVernacular(vernacular, like, offset)
        # Convert from SOAPs structType to Python.
        records = []
        if worms_records:
            for worms_record in worms_records:
                record = dict((key, getattr(worms_record, key)) for key in worms_record._keys())
                records.append(record)
        #
        return records
        
    def get_aphia_classification_by_id(self, aphia_id):
        """ Get the complete classification for one taxon. This also includes any sub or super ranks. """
        worms_classification = self._wsdl_object.getAphiaClassificationByID(aphia_id)
        # Convert from SOAPs structType to Python. List instead of hierarchy.
        records = []
        if worms_classification:
            child_record = worms_classification
            while child_record['child'] != '':
                record = {}
                for key in child_record._keys():
                    if key != 'child':
                        record[key] = getattr(child_record, key)
                records.append(record)
                child_record = child_record['child']
        #        
        return records # Classification as list of records.

    def get_sources_by_aphia_id(self, aphia_id):
        """ Get one or more sources/references including links, for one AphiaID. """
        worms_sources = self._wsdl_object.getSourcesByAphiaID(aphia_id)
        # Convert from SOAPs structType to Python.
        records = []
        if worms_sources:
            for worms_record in worms_sources:
                record = dict((key, getattr(worms_record, key)) for key in worms_record._keys())
                records.append(record)
        #
        return records

    def get_aphia_synonyms_by_id(self, aphia_id):
        """ Get all synonyms for a given AphiaID. """
        worms_records = self._wsdl_object.getAphiaSynonymsByID(aphia_id)
        # Convert from SOAPs structType to Python.
        records = []
        if worms_records:
            for worms_record in worms_records:
                record = dict((key, getattr(worms_record, key)) for key in worms_record._keys())
                records.append(record)
        #
        return records

    def get_aphia_vernaculars_by_id(self, aphia_id):
        """ Get all vernaculars for a given AphiaID. """
        vernaculars = self._wsdl_object.getAphiaVernacularsByID(aphia_id)
        # Convert from SOAPs structType to Python.
        records = []
        if vernaculars:
            for worms_record in vernaculars:
                record = dict((key, getattr(worms_record, key)) for key in worms_record._keys())
                records.append(record)
        #
        return records

    def get_aphia_children_by_id(self, aphia_id, 
                                       offset = 1, 
                                       marine_only = 'false'):
        """ Get the direct children (max. 50) for a given AphiaID.
            Parameters:
                offset: starting record number, when retrieving next chunck of (50) records. Default=1.
                marine_only: limit to marine taxa. Default=true.
        """
        worms_records = self._wsdl_object.getAphiaChildrenByID(aphia_id, offset, marine_only)
        # Convert from SOAPs structType to Python.
        records = []
        if worms_records:
            for worms_record in worms_records:
                record = dict((key, getattr(worms_record, key)) for key in worms_record._keys())
                records.append(record)
        #
        return records
       
    def get_value(self, worms_dict, key):
        """ Clean values by removing unwanted characters. """
        try:
            if worms_dict[key]:
                return unicode(worms_dict[key]).replace('\n', ' ').replace('\r', ' ') # Remove new lines.
        except:
            print('Error when reading WORMS value for: ' + key + '.')
        return ''



# ===== TEST =====
if __name__ == "__main__":
    """ Used for testing. """
    
    # === Test WormsWebservice. ===
    print('\n=== Test WormsWebservice ===')
    
    worms_ws = WormsWebservice()
    
#     worms_result = worms_ws.get_aphia_id('Nitzschia frustulum')
#     print('\nget_aphia_id: ' + unicode(worms_result))
#    
#     worms_result = worms_ws.get_aphia_records('Ctenophora')
#     print('\nget_aphia_records: ' + unicode(worms_result))
#     for record in worms_result:
#         print('---')
#         for key in record.keys():
#             print(key + ':' + unicode(record[key]))
#    
#     worms_result = worms_ws.get_aphia_name_by_id(145422)
#     print('\nget_aphia_name_by_id: ' + worms_result)
#    
#     worms_result = worms_ws.get_aphia_record_by_id(145422)
#     print('\nget_aphia_record_by_id: ' + unicode(worms_result))
#     for key in worms_result.keys():
#         print(key + ':' + unicode(worms_result[key]))
#     
#     worms_result = worms_ws.get_aphia_record_by_ext_id('85257', ext_type = 'tsn')
#     print('\nget_aphia_record_by_tsn: ' + unicode(worms_result))
#    
#     worms_result = worms_ws.get_aphia_records_by_names(['Nitzschia frustulum'])
#     print('\nget_aphia_records_by_names: ' + unicode(worms_result))
#     for name_record in worms_result:
#         for record in name_record:
#             print('---')
#             for key in record.keys():
#                 print(key + ':' + unicode(record[key]))
#  
#     worms_result = worms_ws.get_aphia_classification_by_id(145422)
#     print('\nget_aphia_classification_by_id: ' + unicode(worms_result))
#     for record in worms_result:
#             print(unicode(record))
#     
#     worms_result = worms_ws.get_sources_by_aphia_id(145422)
#     print('\nget_sources_by_aphia_id: ' + unicode(worms_result))
#     for record in worms_result:
#             print(unicode(record))
#   
#     worms_result = worms_ws.get_aphia_synonyms_by_id(145422)
#     print('\nget_aphia_synonyms_by_id: ' + unicode(worms_result))
#     for record in worms_result:
#         print('---')
#         for key in record.keys():
#             print(key + ':' + unicode(record[key]))
#    
#     worms_result = worms_ws.get_aphia_children_by_id(144101)
#     print('\nget_aphia_children_by_id: ' + unicode(worms_result))
#     for record in worms_result:
#         print('---')
#         for key in record.keys():
#             print(key + ':' + unicode(record[key]))
#           
#     worms_result = worms_ws.get_aphia_records_by_vernacular('copepods') 
#     print('\nget_aphia_records_by_vernacular: ' + unicode(worms_result))
#     for record in worms_result:
#         print('---')
#         for key in record.keys():
#             print(key + ':' + unicode(record[key]))
#    
#     worms_result = worms_ws.get_aphia_vernaculars_by_id(1080)
#     print('\nget_aphia_vernaculars_by_id: ' + unicode(worms_result))
#     for record in worms_result:
#         print('---')
#         for key in record.keys():
#             print(key + ':' + unicode(record[key]))


    # === Test WormsMarineSpecies. ===
    
    print('\n=== Test WormsMarineSpecies ===')

    marinespecies = WormsMarineSpecies()
    
#     try:
#         print('\nTest. WormsMarineSpecies: find_valid_taxon:')
#         worms_result = marinespecies.find_valid_taxon('Ctenophora')
#         for key in worms_result.keys():
#             print(key + ':' + unicode(worms_result[key]))
#     except Exception as e:
#         print('Test failed: ' + unicode(e))
# 
#     try:
#         print('\nTest. WormsMarineSpecies: find_valid_taxon:')
#         worms_result = marinespecies.find_valid_taxon('Ctenophora', rank = 'Phylum')
#         for key in worms_result.keys():
#             print(key + ':' + unicode(worms_result[key]))
#     except Exception as e:
#         print('Test failed: ' + unicode(e))

    try:
        print('\nTest. WormsMarineSpecies: generate_tree_from_species_list:')
        worms_result = marinespecies.generate_tree_from_species_list()
    except Exception as e:
        print('Test failed: ' + unicode(e))
        raise

