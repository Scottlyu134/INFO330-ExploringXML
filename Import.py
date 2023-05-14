import sqlite3
import sys
import xml.etree.ElementTree as ET

# Incoming Pokemon MUST be in this format
#
# <pokemon pokedex="" classification="" generation="">
#     <name>...</name>
#     <hp>...</name>
#     <type>...</type>
#     <type>...</type>
#     <attack>...</attack>
#     <defense>...</defense>
#     <speed>...</speed>
#     <sp_attack>...</sp_attack>
#     <sp_defense>...</sp_defense>
#     <height><m>...</m></height>
#     <weight><kg>...</kg></weight>
#     <abilities>
#         <ability />
#     </abilities>
# </pokemon>


# Read pokemon XML file name from command-line
# (Currently this code does nothing; your job is to fix that!)
if len(sys.argv) < 2:
    print("You must pass at least one XML file name containing Pokemon to insert")

for i, arg in enumerate(sys.argv):
    # Skip if this is the Python filename (argv[0])
    if i == 0:
        continue

    xml_tree = ET.parse(arg)
    xml_root = xml_tree.getroot()

    pokemon_details = dict()
    pokemon_types = []
    pokemon_abilities = []

    pokedex_num = xml_root.attrib.get("pokedexNumber")
    pokemon_class = xml_root.attrib.get("classification")
    pokemon_gen = xml_root.attrib.get("generation")

    def fetch_id(cursor, query, param):
        cursor.execute(query.format(param))
        return cursor.fetchone()[0]

    def fetch_and_append_data(child, tag_list, tag_name):
        for subchild in child:
            if subchild.tag == tag_name:
                tag_list.append(subchild.text)

    with sqlite3.connect("pokemon.sqlite") as connection:
        cur = connection.cursor()

        class_id_query = "select id from classification where text='{}'"
        class_id = fetch_id(cur, class_id_query, pokemon_class)

        for child in xml_root:
            tag, text = child.tag, child.text
            if tag == "type":
                pokemon_types.append(text)
            else:
                fetch_and_append_data(child, pokemon_abilities, "ability")
                if tag and tag != "abilities":
                    pokemon_details[tag] = text

        pokemon_query = 'select id from pokemon where pokedex_number={}'
        if not fetch_id(cur, pokemon_query, int(pokedex_num)):
            insert_query = (
                "insert into pokemon (pokedex_number,name,classification_id,generation,hp,attack,defense,speed,sp_attack,sp_defense,height_m,weight_kg) "
                "values ({},'{}',{},{},{},{},{},{},{},{},{},{})"
            )
            cur.execute(insert_query.format(
                int(pokedex_num), pokemon_details.get('name'), int(class_id), int(pokemon_gen),
                int(pokemon_details.get('hp')), int(pokemon_details.get('attack')), int(pokemon_details.get('defense')),
                int(pokemon_details.get('speed')), int(pokemon_details.get('sp_attack')),
                int(pokemon_details.get('sp_defense')), float(pokemon_details.get('height_m')),
                float(pokemon_details.get('weight_kg'))
            ))
            connection.commit()

            pokemon_id = fetch_id(cur, pokemon_query, int(pokedex_num))

            for ability in pokemon_abilities:
                ability_id_query = "select id from ability where name='{}'"
                ability_id = fetch_id(cur, ability_id_query, ability)

                insert_abilities_query = "insert into pokemon_abilities (pokemon_id,ability_id) values({}, {})"
                cur.execute(insert_abilities_query.format(pokemon_id, ability_id))

            connection.commit()

            for index, _type in enumerate(pokemon_types):
                type_id_query = "select id from type where name='{}'"
                type_id = fetch_id(cur, type_id_query, _type)

                insert_type_query = "insert into pokemon_type (pokemon_id,type_id,which) values({}, {}, {})"
                cur.execute(insert_type_query.format(pokemon_id, type_id, index + 1))

            connection.commit()


            
