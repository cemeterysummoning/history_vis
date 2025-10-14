import sqlite3
import sys
import json

def process_name(name):
    new = name
    if '.www' in name:
        new = new[4:]

    replace_dict = {
        'googleusercontent': '.googleusercontent.com',
        'obsidian': '.obsidian.md', 
        'discover': '.discover.com', 
        'sofi': '.sofi.com',
        'citi': '.citi.com',
        'freeconvert': '.freeconvert.com',
        'discord': '.discord.com'
    }

    for k, v in replace_dict.items():
        if k in new:
            new = v
    
    return new

def process_main(path):

    places = {}
    conn = sqlite3.connect(path)
    cur = conn.cursor()
    cur.execute('select id, from_visit, place_id, visit_type from moz_historyvisits order by visit_date desc limit 1000')
    row = cur.fetchall()

    for r in row:
        cur.execute(f'select rev_host from moz_places where id={r[2]}')
        name = process_name(cur.fetchall()[0][0][::-1])

        if name not in places:
            places[name] = {
                'sources': {},
                'visit_types': {
                    'click': 0,
                    'type': 0,
                    'otherwise': 0
                }
            }

        if r[3] == 1:
            places[name]['visit_types']['click'] += 1
        elif r[3] == 2:
            places[name]['visit_types']['type'] += 1
        else:
            places[name]['visit_types']['otherwise'] += 1

        cur.execute(f'select place_id from moz_historyvisits where id={r[1]}')
        data = cur.fetchall()
        for s in data:
            cur.execute(f'select rev_host from moz_places where id={s[0]}')
            source_name = process_name(cur.fetchall()[0][0][::-1])

            if source_name not in places[name]['sources']:
                places[name]['sources'][source_name] = 1
            else:
                places[name]['sources'][source_name] += 1

    conn.close()

    return places

if __name__ == "__main__":
    name = sys.argv[1]
    path = sys.argv[2]
    places = process_main(path)

    with open(f"{name}.json", 'w') as f:
        json.dump(places, f)
