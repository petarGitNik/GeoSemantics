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

# If there is no input value for language, default to whatever dbpedia returns
language = '*'
if len(argv) == 5:
    language = argv[4]

def set_language_filters(language):
    if language == '*':
        return ['', '']
    filter_lang_label = "filter(lang(?label) = \'" + language + "\')\n"
    filter_lang_comment = "filter(lang(?comment) = \'" + language + "\')\n"
    return [filter_lang_label, filter_lang_comment]

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

filter_lang_label, filter_lang_comment = set_language_filters(language)

sparql.setQuery("""
    PREFIX geo: <http://www.w3.org/2003/01/geo/wgs84_pos#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

    SELECT DISTINCT
    ?name ?lat ?long (MIN(?label) AS ?label) (MIN(?comment) AS ?comment)
    WHERE {
        ?name  rdf:type   <http://dbpedia.org/class/yago/Company108058098>.
        ?name  geo:lat ?lat.
        ?name  geo:long ?long.

        filter(""" + filter_latitude + """ && """ + filter_longitude + """)
	    OPTIONAL {
        ?name rdfs:label ?label.
	    ?name rdfs:comment ?comment.

        """ + filter_lang_label + filter_lang_comment + """
        }
    } GROUP BY ?name ?lat ?long
    LIMIT 20
""")

sparql.setReturnFormat(JSON)
results = sparql.query().convert()

def get_value_of_key(dictionary, key, value):
    if dictionary.get(key, False):
        return unicode(dictionary[key][value])
    else:
        return Colors.BLUE + Colors.BOLD + 'No value found in dbpedia' + Colors.NOCOLOR

for result in results['results']['bindings']:
    name = unicode(result['name']['value'])

    label = get_value_of_key(result, 'label', 'value')
    comment = get_value_of_key(result, 'comment', 'value')

    latitude = str(result['lat']['value'])
    longitude = str(result['long']['value'])

    print '\n'
    print Colors.GREEN + Colors.BOLD + 'Name' + Colors.NOCOLOR, name
    print Colors.GREEN + Colors.BOLD + 'Label' + Colors.NOCOLOR, label
    print Colors.GREEN + Colors.BOLD + 'Comment' + Colors.NOCOLOR, comment
    print Colors.GREEN + Colors.BOLD + 'Latitude' + Colors.NOCOLOR, latitude
    print Colors.GREEN + Colors.BOLD + 'longitude' + Colors.NOCOLOR, longitude + '\n'
