#!/usr/bin/env python3
"""
    File: laughing_lemur.py
    Author: Bill Fanselow 2020-10-30

    Description: 
      Create "adjective animal" alliteration (AAA) strings by combining a randomly chosen
      animal name from a static list, with a randomly chosen adjective (beginning with
      same letter) from a list of adjectives generated by a dynamic API query. By default
      outputs a single "AAA", but cmd-line args can specify outputing  a list of AAA's.
      Since the combinations are created with a random shuffling of both lists, the 
      output will be totally different (even for long lists) each time the script is run. 

    Usage:
      $ laughing_lemur.py <LETTER>
     Example: 
      $ laughing_lemur.py B
      brave baboon
      
     Optional args: 
       --list <N>: create a list of <N> "adjective animal" alliterations 
       --show: show all animals and adjectives for the specified letter 

    Requires:
     pip install requests

    External Resources:
     * Adjectives: https://www.datamuse.com/api - Free api for various word queries.
     * Animals:    https://a-z-animals.com/animals -  Did a one-time beautiful-soup scrap 
                    of this site to generate a static dictionary contained within this file 
                    for simplicity.

"""

#--------------------------------------------------------------------------------------
import os
import sys
import string
import random
import argparse
import requests

# Adjectives API
#  + "md=p" to inlcude part of speech - api doesn't allow selection of adjective only
#  + "&sp=<L>*" will be appended to this, where <L> is our input letter, indicating 
#     words starting with <L>
datamuse_api_url = 'https://api.datamuse.com/words?max=1000&md=p'

DEBUG = 0

myname = os.path.basename(__file__)

#--------------------------------------------------------------------------------------
ANIMALS = {
    'A': ["aardvark", "albatross", "alligator", "alpaca", "ant", "anteater", "antelope", 
          "akita",  "ape", "armadillo", "avocet"],
    'B': ["baboon", "badger", "barnowl", "barracuda", "bat", "bear", "beaver", "bee", "bison", 
          "boar", "bobcat", "bonobo", "buffalo", "bulldog", "bullfrog", "butterfly"], 
    'C': ["camel", "capybara", "caribou", "cassowary", "cat", "catfish", "caterpillar", 
          "cattle", "centipede", "chamois", "chameleon", "cheetah", "chicken", "chimpanzee", 
          "chinchilla", "chipmunk", "chough", "clam", "cobra", "cockroach", "cod", "cormorant", 
          "coyote", "crab", "crane", "crocodile", "crow", "curlew"],
    'D': ["deer", "dinosaur", "dog", "dogfish", "dolphin", "donkey", "dotterel", "dove",
           "dragonfly", "duck", "dugong", "dunlin"],
    'E': ["eagle", "earwig", "echidna", "eel", "eland", "elephant", "elephant-seal", "elk", 
          "emu"],
    'F': ["falcon", "ferret", "finch", "fish", "flamingo", "fly", "fox", "frog"],
    'G': ["gaur", "gazelle", "gecko", "gerbil", "giant-panda", "giraffe", "gnat", "gnu", 
          "goat", "goose", "goldfinch", "goldfish", "gorilla", "goshawk", "grasshopper", 
          "greyhound" "grouse", "guanaco", "guinea-fowl", "guinea-pig", "gull", "guppy"],
    'H': ["hamster", "hare", "hawk", "hedgehog", "heron", "herring", "hippopotamus", 
          "honey-badger", "hornet", "horse", "hummingbird", "hyena"],
    'I': ["ibex", "ibis", "iguna", "impala", "indri"],
    'J': ["jackal", "jaguar", "jay", "jellyfish", "jerboah"],
    'K': ["kangaroo", "kingfisher", "koala", "komodo-dragon", "kookabura", "kouprey", "kudu"],
    'L': ["ladybug", "lapwing", "lark", "lemur", "lemming", "leopard", "lion", "lizard",
          "llama", "lobster", "locust", "loris", "louse", "lyrebird", "lynx"],
    'M': ["macaw", "magpie", "mallard", "manatee", "mandrill", "mantis", "marten", "meerkat",
          "mink", "millipede", "mole", "mongoose", "mongrel", "monkey", "moose", "mouse",
          "mosquito", "moth", "mountain-lion", "mule"],
    'N': ["narwhal", "newt", "nightingale", "numbat"],
    'O': ["ocelot", "octopus", "okapi", "opossum", "orangutan" "oryx", "ostrich", "otter",
          "owl", "ox", "oyster"],
    'P': ["panther", "pademelon",  "parrot", "partridge", "peafowl", "pelican", "penguin",
          "pheasant", "pig", "pigeon", "pika", "piranha", "platypus", "polar-bear", "pony",
          "poodle", "porcupine", "porpoise", "prairie-dog", "puffin", "puma"],
    'Q': ["quail", "quelea", "quetzal", "quokka", "quoll"],
    'R': ["rabbit", "raccoon", "rail", "ram", "rat", "rattlesnake", "raven", "red-deer",
          "red-panda", "reindeer", "rhinoceros", "robin", "rook"],
    'S': ["salamander", "salmon", "sandpiper", "sardine", "scorpion", "sea-lion",
          "sea-urchin", "seahorse", "seal", "shark", "sheep", "shrew", "skunk", "snail",
          "snake", "sparrow", "spider", "spoonbill", "squid", "squirrel", "starling", "stingray",
          "stinkbug", "stork", "swallow", "swan"],
    'T': ["tapir", "tarsier", "termite", "tiger", "toad", "toucan" "trout", "turkey", "turtle"],
    'U': ["uakari", "uguisu", "umbrellabird"],
    'V': ["vicuna", "viper", "vole" "vulture", "vampire-bat"],
    'W': ["wallaby", "walrus", "wasp", "water-buffalo", "weasel", "whale", "wildebeest", "wolf", 
          "wolverine", "wombat", "woodcock", "woodpecker", "worm", "wren"],
    'X': ["X-ray-Tetra", "Xerus"],
    'Y': ["yak", "Yorkshire-terrier"],
    'Z': ["zebra", "zebu"]
}
#--------------------------------------------------------------------------------------

def parse_input_args():
    """ Command-line parsing """ 

    # Create the parser with a description and optional usage
    my_parser = argparse.ArgumentParser( 
        prog=myname, 
        usage='%(prog)s <letter> [options]',
        description='Create one or more random adjective-animal-alliterations for a specific letter'
    )

    # Add the arguments
    my_parser.add_argument(
        'Letter',                  
        metavar='letter',
        type=str, 
        help='Starting letter for adjective-animal-alliteration'
    )
    my_parser.add_argument(
        '-s', '--show',
        required=False,
        action='count',
        help='Print table of all adjectives and animals used'
    )
    my_parser.add_argument(
        '-l', '--list',                 
        required=False,
        metavar='list',
        type=int,
        help='Generate a list of size N'
    ) 

    input_args = my_parser.parse_args()

    return input_args


def validate_letter(letter):
    """ 
     Validate that the input letter is an ascii character and convert to lowercase 
     Req-args: letter (str) 
     Return: lowercase ascii char (str) 
    """
    lc_letter = letter.lower()
    if lc_letter not in list(string.ascii_letters):
        print("ERROR - Input character (%s) is not a valid letter" % (letter))
        sys.exit(1) 
    return lc_letter


def get_animals_starting_with(first_letter):
    """ 
     Simple animal-dict lookup to get animals for passed first_letter
     Req-args: first_letter (str) 
     Return: adjectives list (list) 
    """
    animals_list = ANIMALS[first_letter]
    return animals_list 


def get_adjectives_starting_with(first_letter):
    """
     Build a list of adjectives starting with passed letter 
     Req-args: first_letter (str) 
     Return: adjectives list (list) 
    """
    api_data = get_adjectives_data(first_letter)
    adjectives = parse_adjectives_data(api_data)
    return adjectives
 

def get_adjectives_data(first_letter):
    """
     Send request to datamuse API to get adjectives data
     Req-args: first_letter (str) 
     Return: adjectives data (dict) 
    """

    # mocked data   
    data = ["happy", "sad", "ornry", "lazy"] 

    url = "%s&sp=%s*" % (datamuse_api_url, first_letter) 
    response = requests.get(url)
 
    status = response.status_code
    if status != 200:
        print("ERROR - API response status" % (status))
        sys.exit(1) 
 
    data = response.json()
 
    return data
 

def parse_adjectives_data(api_data):
    """
     Parse data from datamuse API reponse and build adjectives list 
     Req-args: raw api data (list) 
     Return: adjectives (list) 
    """

    adjectives_list = []

    for word_obj in api_data:
        #print("%s\n" % word_obj)
        word = word_obj.get('word', None)
        if not word:
            print("ERROR - Missing required prop [word] in word object")
            print(word_obj)
            sys.exit(1) 
        tags = word_obj.get('tags', [])
        if not tags:
            if DEBUG > 1:
              print("WARNING - Missing required prop [tags] in word object (%s)" % (word))
              print(word_obj)
       
        # only take those words that have a single (part-of-speech="adj") tag
        if len(tags) == 1:
            if tags[0] == "adj":
                adjectives_list.append(word)

    return adjectives_list   


def create_random_combos(**kwargs):
    """
     Build combinations of "adjective animal" strings from passed lists after
      some validation of valid lists.
     Req **kwargs: 
       * animals (list) 
       * adjectives (list) 
       * size (int) 
     Return: list of "adjective anmial" strings  (list) 
    """
    
    aa_combos = []

    animals = kwargs.get('animals', [])
    adjectives = kwargs.get('adjectives', [])
    size = kwargs.get('size', 1)

    if not len(animals):
        print("ERROR - Empty animal list generated")
        sys.exit(1) 
    if not len(adjectives):
        print("ERROR - Empty adjective list generated")
        sys.exit(1) 


    # whichever list is smallest becomes our list (loop) limit=<N> 
    smaller_length  = len(animals) if (len(animals) < len(adjectives)) else len(adjectives) 
    list_length  = smaller_length - 1 
    
    # shuffle our animal list
    random.shuffle(animals)

    # shuffle our adjective list
    random.shuffle(adjectives)

    # combine the two list elements into strings
    for i,animal in enumerate(animals):
        aaa = adjectives[i] + " " + animals[i]
        aa_combos.append(aaa)
        if i >= list_length:
            break

    return aa_combos[0:size]

        
def create_list_table(animals, adjectives):
    """
     Format a user-freindly table of the (sorted) lists of animals and adjectives 
     Req-args: 
       * animal-list (list) 
       * adjective-list (list) 
     Return: data table (str)
    """

    N_animals = len(animals) 
    N_adjectives = len(adjectives)
    
    if N_animals > N_adjectives:
        diff = N_animals - N_adjectives
        # pad adjectives list by N_animals
        adjectives += [''] * (diff)
    else:
        diff = N_adjectives - N_animals
        # pad animals list by N_adjectives
        animals += [''] * (diff)

    print( "\n(%d) %-25s (%d) %s" % (N_adjectives, "ADJECTIVES", N_animals, "ANIMALS")) 
    for i,term in enumerate(adjectives):
        if term:
            print( "%-4d %-26s %s" % (i+1, adjectives[i], animals[i])) 

#--------------------------------------------------------------------------------------
if __name__ == '__main__':

    show = 0
    list_size = 1

    args = parse_input_args()

    letter = args.Letter

    if args.list: 
        list_size = args.list 

    validate_letter(letter)

    animals_list = get_animals_starting_with(letter)
    adjectives_list = get_adjectives_starting_with(letter)

    random_combos = create_random_combos(animals=animals_list, adjectives=adjectives_list, size=list_size)

    if list_size > len(animals_list):
        print("WARNING: Full animal list for letter (%s) is smaller than your requested list size" % letter)
    if list_size > len(adjectives_list):
        print("WARNING: Full adjective list for letter (%s) is smaller than your requested list size" % letter)

    for aaa in random_combos:
        print( aaa )

    if args.show:
        create_list_table(animals=animals_list, adjectives=adjectives_list)
 
