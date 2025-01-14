from collections import defaultdict
import csv



def parse_discrete_traits(traits, trait_file, trait_loc_in_name_input, trait_delimiter, config):
#error catching:
#needs trait file or trait loc in name
#with trait loc in name, needs trait delimiter in the name
#not all traits present in trait_loc_in_name
    
    trait_index = {}
    all_trait_options_prep = defaultdict(set)
    all_trait_options = defaultdict(list)
    trait_dict = defaultdict(dict)

    if config["ambiguities"]:
        ambiguities = list(config["ambiguities"].keys())
        amb_options = set()
        for string in config["ambiguities"].values():
            lst = string.split(" ")
            for ele in lst:
                amb_options.add(ele) 
    else:
        ambiguities = []
        amb_options = set()
    
    traits = [i.strip(" ") for i in traits.split(",")]
    for number, trait in enumerate(traits):
        trait_index[trait] = int(number)
    
    if trait_file: #ie row per sequence
        with open(trait_file) as f:
            data = csv.DictReader(f)
            for line in data:
                name = line["sequence_name"]
                for trait in traits:
                    trait_dict[name][trait] = line[trait]
                    if line[trait] not in ambiguities:
                        all_trait_options_prep[trait].add(line[trait])
    
    elif trait_loc_in_name_input:
        trait_loc_in_name = {}
        for combo in trait_loc_in_name_input.split(","):
            trait,loc = combo.split("=")
            trait_loc_in_name[trait] = loc
        for tax in config["taxa"]:
            for trait, loc in trait_loc_in_name.items(): 
                value = tax.split(trait_delimiter)[loc-1]
                trait_dict[tax].append(value)
                if value not in ambiguities:
                    all_trait_options_prep[trait].add(value) 

    #not sure how this will work beast-wise
    for i in amb_options:
        if i not in all_trait_options_prep[trait]:
            all_trait_options_prep[trait].add(i)
            
                
    for trait, options in all_trait_options_prep.items():
        new_lst = sorted(options)
        all_trait_options[trait] = new_lst      

    if config["multi_tree"]:
        options_per_tree = parse_multitree_traits(trait_locs, trait_dict, taxon_set_file)
    else:
        options_per_tree = ""

    # print(trait_dict)

    return traits, trait_index, all_trait_options, trait_dict, options_per_tree

def parse_ambiguities(ambiguity_file): #currently only works for one trait

    code_to_options = {}
    with open(ambiguity_file) as f:
        data = csv.DictReader(f, delimiter="\t")
        for l in data:
            code_to_options[l['ambiguity']] = " ".join(l['options'].split(","))

    return code_to_options


def parse_multitree_traits():
    options_per_tree = defaultdict(dict) #trait to tree to options
    #write this function

def continuous_phylogeography_processing(trait_file):
#error: headers missing
    traits = ["latitude", "longitude", "coordinates"]
    overall_trait = "coordinates"

    trait_dict = defaultdict(dict)

    with open(trait_file) as f:
        data = csv.DictReader(f, delimiter="\t")
        for l in data:
            inner_dict = {}
            inner_dict["longitude"] = l['longitude']
            inner_dict["latitude"] = l["latitude"]
            inner_dict["coordinates"] = f"{l['latitude']} {l['longitude']}"

            trait_dict[l['taxon']] = inner_dict

    return traits, trait_dict, overall_trait


