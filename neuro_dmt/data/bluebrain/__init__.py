"""Neuroscience Cells and Circuit data used for building and validating cells
and circuits at the Blue Brain Project."""

class BlueBrainData:
    """Mixin"""

    __available_data = {}

    def __init__(self, *args, **kwargs):
        """..."""
        super().__init__(*args, **kwargs)

        BlueBrainData.insert(self)
   
    @classmethod
    def insert(cls, data, data_label=None):
        """add data with label"""
        alabel = data.animal
        blabel = data.brain_region.label
        glabel = data.phenomenon.group
        dlabel = data.label if not data_label else data_label
        if alabel not in cls.__available_data:
            cls.__available_data[alabel] = {}
        if blabel not in cls.__available_data[alabel]:
            cls.__available_data[alabel][blabel] = {}
        if glabel not in cls.__available_data[alabel][blabel]:
            cls.__available_data[alabel][blabel][glabel] = {}
        cls.__available_data[alabel][blabel][glabel][dlabel] = data
        return cls.__available_data

    #given one
    @classmethod
    def __find_given_animal(cls,
            animal):
        """..."""
        return BlueBrainData.__available_data.get(animal, {})

    @classmethod
    def __find_given_region(cls,
            region):
        """..."""
        animal_data_items = BlueBrainData.__available_data.items()
        return {
            animal: animal_data[region]
            for animal, animal_data in animal_data_items
            if region in animal_data}

    @classmethod
    def __find_given_group(cls,
            group):
        """..."""
        animal_data_items = BlueBrainData.__available_data.items()
        return {
            animal: {
                region: region_data[group]
                for region, region_data in animal_data_items
                if group in region_data }
            for animal, animal_data in animal_data_items}

    @classmethod
    def __find_given_label(cls,
            label):
        """..."""
        animal_data_items = BlueBrainData.__available_data.items()
        return {
            animal: {
                region: {
                    group: group_data[label]
                    for group, group_data in region_data.items()
                    if label in group_data}
                for region, region_data in animal_data_items}
            for animal, animal_data in animal_data_items}

    #given two
    @classmethod
    def __find_given_animal_region(cls,
            animal, region):
        """..."""
        return cls.__find_given_animal(animal)\
                  .get(region, {})

    @classmethod
    def __find_given_animal_group(cls,
            animal, group):
        """..."""
        animal_data = cls.__find_given_animal(animal)
        return {
            region: region_data[group]
            for region, region_data in animal_data.items()
            if group in region_data}

    @classmethod
    def __find_given_animal_label(cls,
            animal, label):
        """..."""
        animal_data = cls.__find_given_animal(animal)
        return {
            region: {
                group: group_data[label]
                for group, group_data in region_data.items()
                if label in group_data}
            for region, region_data in animal_data}

    @classmethod
    def __find_given_region_group(cls,
            region, group):
        """..."""
        animal_data_items = BlueBrainData.__available_data.items()
        return {
            animal: animal_data[region][group]
            for animal, animal_data in animal_data_items
            if region in animal_data and group in animal_data[region]}

    @classmethod
    def __find_given_region_label(cls,
            region, label):
        """..."""
        animal_data_items = BlueBrainData.__available_data.items()
        return {
            animal: {
                group: group_data[label]
                for group, group_data in animal_data[region].items()
                if region in animal_data}
            for animal, animal_data in animal_data_items}

    @classmethod
    def __find_given_group_label(cls,
            group, label):
        """..."""
        animal_data_items = BlueBrainData.__available_data.items()
        return {
            animal: {
                region: region_data[group][label]
                for region, region_data in animal_data.items()
                if group in region_data and label in region_data[group]}
            for animal, animal_data in animal_data_items}

    #given three
    @classmethod
    def __find_given_animal_region_group(cls,
            animal, region, group):
        """..."""
        return BlueBrainData.__available_data\
            .get(animal, {})\
            .get(region, {})\
            .get(group, {})

    @classmethod
    def __find_given_animal_region_label(cls,
            animal, region, label):
        """..."""
        animal_region_data\
            = cls.__find_given_animal_region(
                animal, region)
        return {
            group: group_data[label]
            for group, group_data in animal_region_data.items()
            if label in group_data}

    @classmethod
    def __find_given_animal_group_label(cls,
            animal, group, label):
        """..."""
        animal_data = cls.__find_given_animal(animal)
        return {
            region: region_data[group][label]
            for region, region_data in animal_data.items()
            if group in region_data and label in region_data[group]}

    @classmethod
    def __find_given_region_group_label(cls,
            region, group, label):
        """..."""
        animal_data_items = BlueBrainData.__available_data.items()
        return {
            animal: animal_data[region][group][label]
            for animal, animal_data in animal_data_items
            if region in animal_data 
            and group in animal_data[region]
            and label in animal_data[region][group]}

    @classmethod
    def __find_given_animal_region_group_label(cls,
            animal, region, group, label):
        """..."""
        return cls.__available_data\
            .get(animal, {})\
            .get(region, {})\
            .get(group, {})\
            .get(label, None)

    @classmethod
    def find(cls,
            animal=None,
            region=None,
            group=None,
            label=None):
        """..."""

        if animal:
            if region:
                if group:
                    if label:
                        return cls.__find_given_animal_region_group_label(
                            animal, region, group, label)
                    else: #no label
                        return cls.__find_given_animal_region_group(
                            animal, region, group)
                else: #no group
                    if label:
                        return cls.__find_given_animal_region_label(
                            animal, region, label)
                    else: #no label
                        return cls.__find_given_animal_region(
                            animal, region)
            else: #no region
                if group:
                    if label:
                        return cls.__find_given_animal_group_label(
                            animal, group, label)
                    else: #no label
                        return cls.__find_given_animal_group(
                            animal, group)
                else: #no group
                    if label:
                        return cls.__find_given_animal_label(
                            animal, label)
                    else: #no label
                        return cls.__find_given_animal(
                            animal)
        else: #no animal
            if region:
                if group:
                    if label:
                        return cls.__find_given_region_group_label(
                            region, group, label)
                    else: #no label
                        return cls.__find_given_region_group(
                            region, group)
                else: #no group
                    if label:
                        return cls.__find_given_region_label(
                            region, label)
                    else: #no label
                        return cls.__find_given_region(
                            region)
            else: #no region
                if group:
                    if label:
                        return cls.__find_given_group_label(
                            group, label)
                    else: #no label
                        return cls.__find_given_group(
                            group)
                else: #no group
                    if label:
                        return cls.__find_given_label(
                            label)
                    else: #no label
                        return cls.__available_data
