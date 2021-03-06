# Plankton Toolbox: Species lists, etc. #

To run Plankton Toolbox in a useful way there should be some data loaded at start-up. 
When downloading Plankton Toolbox there is a set of species lists, dataset parsers and test datasets embedded. 
For some users this is sufficient, but other users have to adjust or replace the species lists and parsers. 
How species lists are organized is described here. 

## Where is pre-loaded data located? ##

When Plankton Toolbox is downloaded and the zip-file is decompressed the following directory structure will occur (Windows example):

    - PlanktonToolbox_ver_1_0_0_Windows_YYYY-MM-DD
        - PlanktonToolbox.exe 
        - toolbox_data 
            - cache 
            - code_lists 
            - img 
            - plankton_counter 
            - parsers 
            - species 

On Windows and Ubuntu the directory named **toolbox\_data** should be a directory folder located in the same folder as the executable file. 

On MacOS the directory must be moved to the **user** directory.

## Files in toolbox_data/species ##

This directory contains different files with species related data. The file format shall be Excel files with the file extension **.xlsx**. How Plankton Toolbox should handle the files is controlled by the file prefix. These prefixes are used:
  * **taxa_** Is used to build taxonomic hieracies.
  * **translate_** For managing translations of misspellings.
  * **synonyms_** Used to handle synonym names.
  * **bvol_** Adds extra information, biovolumes, etc.
  * **bvolcolumns_** Handles variations in the header row of **bvol_** files.
  * **planktongroups_** Our own grouping of organisms.

All files with the prefixes described above will be loaded at start-up. It is possible to have **taxa_the_big_list.xlsx** and **taxa_my_extra_species.xlsx** and both will be loaded.

Hint: If you don't want a list to be loaded at start-up, then just add some characters before the prefix, for example **NOTUSED_taxa_my_new_list.xlsx**

### Files with prefix taxa_ ###

These files is used to build up the taxonomic hierarchy in Plankton Toolbox. For each scientific name the rank and parent name must be specified.

| **scientific_name** | **rank** | **aphia_id** | **parent_name** |
|:--------------------|:---------|:-------------|:----------------|
| Chromista           | Kingdom  | 7            | Biota           |

### Files with prefix translate_ ###

Some taxa files and datasets contain taxa not matching the taxonomic hierarchy loaded in Plankton Toolbox. This list is used to handle misspellings, etc.

| **scientific_name_from**             | **scientific_name_to** |
|:-------------------------------------|:-----------------------------------|
| Actinocyclus octonarius v. crassus   | Actinocyclus octonarius var. crassus |
| Flagellates                          | Flagellates species incertae sedis |

### Files with prefix synonyms _ ###

Some taxa files and datasets contain taxa not matching the taxonomic hierarchy loaded in Plankton Toolbox. This list is used to handle synonyms.

| **scientific_name_from**    | **scientific_name_to** |
|:----------------------------|:--------------------|
| Fragilariforma virescens    | Fragilaria virescens |
| Anabaena lemmermannii       | Dolichospermum lemmermannii |

### Files with prefix bvol _ ###

The format of this should follow the HELCOM-PEG BVOL-file. When releasing a new version of Plankton Toolbox the latest public version of this list is included. Normally there is also an extension included for species not in the HELCOM area.

The latest version of  the HELCOM-PEG BVOL-file can be found here: [PEG\_BVOL](http://www.ices.dk/marine-data/vocabularies/Documents/PEG_BVOL.zip)

### Files with prefix bvolcolumns _ ###

This is a translation file needed since the header row in the HELCOM-PEG BVOL-file changes over time. If you download a newer version it may be necessary to modify this file, otherwise the Plankton Toolbox will fail to read it in a proper way.

| **column_name** | **used_on_rank_level** | **numeric** | **internal_toolbox_name** |
|:----------------|:-----------------------|:------------|:--------------------------|
| Division        | Taxon                  |             | BVOL Division             |
| SizeClassNo     | Size class             |             | Size class                |


### Files with prefix planktongroups _ ###

When aggregating parameter values for taxa in each sample to a higher taxonomic level Plankton Toolbox supports aggregation to Biota, Kingdom, Phylym, Class, Order, Family, Genus and Species.
In addition Plankton Toolbox also supports aggregation to a user defined level called _Plankton groups_. 
When specifying each group the built in knowledge on classification can be used, for example all taxa below the phylum Bacillariophyta can be put in the Diatoms group.

| **scientific_name** | **rank** | **plankton_group** |
|:--------------------|:---------|:-------------------|
| Bacillariophyta     | Phylum   | Diatoms            |
| Ciliophora          | Phylum   | Ciliates           |


## Files in toolbox_data/code_lists ##

In the screening part of Plankton Toolbox it is possible to screen for invalid code values.

