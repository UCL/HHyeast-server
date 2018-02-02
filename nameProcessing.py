# Classes and tools to process protein names

class NameMaps():
    def __init__(self):
        self._yeast = {}
        self._syst = {}
        self._std = {}

    @property
    def yeast(self):
        if not self._yeast:
            self._fill_maps()
        return self._yeast

    @property
    def syst(self):
        if not self._syst:
            self._fill_maps()
        return self._syst

    @property
    def std(self):
        if not self._std:
            self._fill_maps()
        return self._std

    # Fill name mapping dictionaries
    def _fill_maps(self):
        with open("yeast_names_ref.txt", "r") as f:
            for line in f:
                words = line.split()
                yeast_name = words[0]
                syst_name = words[1]
                if len(words)==3:
                    std_name = words[2]
                    new_name = std_name
                    description = std_name
                    self._syst[std_name] = syst_name
                else:
                    std_name = ''
                    new_name = syst_name
                    description = syst_name+' (hypothetical protein)'
                self._yeast[yeast_name] = new_name, description
                self._std[syst_name] = std_name


name_maps = NameMaps()

# Fix ORF name from yeast database
def yeast_name_fixed(name):
    return name_maps.yeast.get(name,name)

# Check if name is systematic/standard name
def is_systematic_name(name):
    return name in name_maps.std

def is_standard_name(name):
    return name in name_maps.syst

# A hypothetical protein has a systematic name but no standard name
def is_hypothetical_protein(name):
    return is_systematic_name(name) and not standard_name(name)

# An unknown protein has neither a systematic nor a standard name
def is_unknown_protein(name):
    return not is_systematic_name(name) and not is_standard_name(name)

# Return systematic/standard name from the other
def systematic_name(name):
    return name_maps.syst.get(name,name)

def standard_name(name):
    return name_maps.std.get(name,name)

# The reference file cannot be guaranteed to be complete, but
# the responsibility of what to do with ORF's not in it
# falls on the user. Therefore in the following, let
# unknown proteins pass through keeping their name.

# Return a single name for a protein. The convention is:
# standard name if it exists, the same name as the argument if it's
# a hypothetical or unknown protein.
def single_name(name):
    if is_hypothetical_protein(name) or is_unknown_protein(name):
        return name
    else:
        return standard_name(name)

# Return the name to be displayed in the drop-down list
def display_name(name):
    if is_hypothetical_protein(name) or is_unknown_protein(name):
        return name
    else:
        return standard_name(name)+"/"+systematic_name(name)

