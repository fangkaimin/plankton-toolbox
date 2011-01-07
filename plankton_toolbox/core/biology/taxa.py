#!/usr/bin/env python
# -*- coding:iso-8859-1 -*-
#
# Project: Plankton toolbox. http://plankton-toolbox.org
# Author: Arnold Andreasson, info@mellifica.se
# Copyright (c) 2010-2011 SMHI, Swedish Meteorological and Hydrological Institute 
# License: MIT License as follows:
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

"""

"""

from abc import abstractmethod

class Taxa(object):
    """
    Abstract base class for lists of taxon. 
    """
    def __init__(self):
        self._metadata = {} # Metadata for the dataset.
        self._data = [] # List of taxon objects.
        self._idToTaxonDict = {} # For fast lookup.
        self._nameToTaxonDict = {} # For fast lookup.
        
    def clear(self):
        """ """
        self._metadata.clear()
        self._metadata.clear()
        del self._data[:] # Clear the list.
        self._idToTaxonDict.clear()
        self._nameToTaxonDict.clear()
        
    def getMetadata(self):
        """ """
        return self._metadata
        
    def getTaxonList(self):
        """ """
        return self._data
        
    def getIdToTaxonDict(self):
        """ """
        return self._idToTaxonDict
        
    def getNameToTaxonDict(self):
        """ """
        return self._nameToTaxonDict
        
    def getTaxonListSortedBy(self, sortField):
        """ """
        raise UserWarning('Not implemented: getTaxonListSortedBy.')
        
    def getTaxonById(self, taxonId):
        """ """
        if len(self._idToTaxonDict) == 0:
            self._createIdToTaxonLookup() # On demand
        if self._idToTaxonDict.has_key(taxonId):
            return self._idToTaxonDict[taxonId]
        else:
            return None
    
    def getTaxonByName(self, taxonName):
        """ """
        if len(self._nameToTaxonDict) == 0:
            self._createNameToTaxonDict() # On demand
        if self._nameToTaxonDict.has_key(taxonName):
            return self._nameToTaxonDict[taxonName]
        return None
    
    @abstractmethod
    def _createIdToTaxonLookup(self):
        """ """
#        raise UserWarning('Not implemented: _createNameToTaxonDict.')

    @abstractmethod
    def _createNameToTaxonDict(self):
        """ """
#        raise UserWarning('Not implemented: _createNameToTaxonDict.')

        
class Dyntaxa(Taxa):
    """ 
    Dynamisk Taxa, delivered by ArtDatabanken: 
    http://artdatabanken.se or http://www.artdata.slu.se/english 
    """
    def __init__(self):
        """ """
        # Initialize parent.
        super(Dyntaxa, self).__init__()

    def _createIdToTaxonLookup(self):
        """ """
        for taxon in self._data:
            id = taxon.get('Taxon id', None)
            if id:
                self._idToTaxonDict[id] = taxon
            else:
                print('DEBUG: Name missing.')
            
    def _createNameToTaxonDict(self):
        """ """
        for taxon in self._data:
            name = taxon.get('Valid name', None)
            if name:
                self._nameToTaxonDict[name] = taxon
            else:
                print('DEBUG: Name missing.')
            

class Peg(Taxa):
    """
    The Phytoplankton Expert Group plankton list.
    Responsible: http://www.helcom.fi
    Download from: http://www.ices.dk/env/repfor/index.asp
    """
    def __init__(self):
        """ """  
        self.__nameAndSizeList = None
        # Initialize parent.
        super(Peg, self).__init__()

    def clear(self):
        """ """
        self.__nameAndSizeList = None
        super(Peg, self).clear()
        
    def _createNameToTaxonDict(self):
        """ """
        for taxon in self._data:
            self._nameToTaxonDict[taxon['Species']] = taxon

    def getSizeclassItem(self, taxonName, size):
        """ """
        for sizeclass in self.getTaxonByName(taxonName)['Size classes']:
            if unicode(sizeclass['Size class']) == size:
                return sizeclass
        return None

    def getNameAndSizeList(self):
        """ 
        Used when a sorted list of taxon/size is needed.
        Format: [[taxon], [sizeclass], ...]
        """
        if self.__nameAndSizeList == None:
            self.__createNameAndSizeList()
        return self.__nameAndSizeList
            
    def __createNameAndSizeList(self):
        """ """
        self.__nameAndSizeList = []
        for taxon in self._data:
            for sizeclass in taxon['Size classes']:
                self.__nameAndSizeList.append([taxon, sizeclass])
        # Sort.
        self.__nameAndSizeList.sort(nameandsize_sort) # Sort function defined below.

# Sort function for name and size list.
def nameandsize_sort(s1, s2):
    """ """
    # Check names first.
    name1 = s1[0]['Species']
    name2 = s2[0]['Species']
    if name1 < name2: return -1
    if name1 > name2: return 1
    # Names are equal, check sizes.
    size1 = s1[1]['Size class']
    size2 = s2[1]['Size class']
    if size1 < size2: return -1
    if size1 > size2: return 1
    return 0 # Both are equal.


class MarineSpecies(Taxa):
    """ 
    """
    def __init__(self):
        """ """
        # Initialize parent.
        super(MarineSpecies, self).__init__()


class Ioc(Taxa):
    """ 
    """
    def __init__(self):
        """ """
        # Initialize parent.
        super(Ioc, self).__init__()

