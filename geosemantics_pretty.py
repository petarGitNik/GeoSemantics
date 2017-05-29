from SPARQLWrapper import SPARQLWrapper
from SPARQLWrapper import JSON

from sys import argv
from sys import exit

"""
geosemantics [latitude] [longitude] [tolerance] [language]
"""

# If there are too many arguments - exit
if len(argv) > 6:
    print "Too many arguments."
    exit(0)

# If there are not enough arguments - exit
if len(argv) < 4:
    print "Not enough arguments."
    exit(0)

def is_it_a_number(candidate):
    try:
        float(candidate)
    except ValueError:
        print "Input values must be numbers!"
        return False
    return True

# If any of the arguments is not a number - exit
for value in [argv[1], argv[2], argv[3]]:
    if not is_it_a_number(value):
        exit(0)

latitude = float(argv[1])
longitude = float(argv[2])
tolerance = float(argv[3])

# If there is no input value for language, default to English
language = 'en'
if len(argv) == 5:
    language = argv[4]

# Colors for pretty colored output
class Colors(object):
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    BOLD = '\033[1m'
    NOCOLOR = '\033[0m'

# Relevant code starts here
sparql = SPARQLWrapper('http://dbpedia.org/sparql')

# Prepare boundaries
top = latitude + tolerance
bottom = latitude - tolerance
left = longitude - tolerance
right = longitude + tolerance

# Prepare filters
filter_latitude = "?lat > " + str(bottom) + " && ?lat < " + str(top)
filter_longitude = "?long > " + str(left) + " && ?long < " + str(right)
filter_lang_label = "filter(lang(?label) = \'" + language + "\')\n"
filter_lang_comment = "filter(lang(?comment) = \'" + language + "\')\n"

sparql.setQuery("""
    SELECT DISTINCT
    ?name ?lat ?long ?label ?comment
    WHERE {
        ?name rdf:type <http://dbpedia.org/class/yago/Company108058098>.
        ?name <http://www.w3.org/2003/01/geo/wgs84_pos#lat> ?lat.
        ?name <http://www.w3.org/2003/01/geo/wgs84_pos#long> ?long.

        filter(""" + filter_latitude + """ && """ + filter_longitude + """)
        OPTIONAL {
                ?name <http://www.w3.org/2000/01/rdf-schema#label> ?label.
                ?name <http://www.w3.org/2000/01/rdf-schema#comment> ?comment.

                """ + filter_lang_label + filter_lang_comment + """
        }
    } LIMIT 20
""")

sparql.setReturnFormat(JSON)
results = sparql.query().convert()

for result in results['results']['bindings']:
    name = unicode(result['name']['value'])
    label = unicode(result['label']['value'])
    comment = unicode(result['comment']['value'])
    latitude = str(result['lat']['value'])
    longitude = str(result['long']['value'])

    print '\n'
    print Colors.GREEN + Colors.BOLD + 'Name' + Colors.NOCOLOR,
    print name
    print Colors.GREEN + Colors.BOLD + 'Label' + Colors.NOCOLOR,
    print label
    print Colors.GREEN + Colors.BOLD + 'Comment' + Colors.NOCOLOR,
    print comment
    print Colors.GREEN + Colors.BOLD + 'Latitude' + Colors.NOCOLOR,
    print latitude
    print Colors.GREEN + Colors.BOLD + 'longitude' + Colors.NOCOLOR,
    print longitude + '\n'
