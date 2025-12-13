#!/usr/bin/env python
import sys
from etl.extract import get_latest_films

print("Testing updated extract.py with real cast data from TV Maze API...\n")

films = get_latest_films(limit=4)

if films:
    print("SUCCESS: Extracted {} films\n".format(len(films)))
    
    # Count total unique actors
    total_actors = 0
    for film in films:
        actor_count = len(film['actors'])
        total_actors += actor_count
        print("Title: {}".format(film['title']))
        print("Rating: {}/10".format(film['rating']))
        print("Year: {}".format(film['year']))
        print("Actors ({}):".format(actor_count))
        for actor in film['actors']:
            print("  - {}".format(actor))
        print()
    
    print("SUMMARY: {} total actors across {} films".format(total_actors, len(films)))
else:
    print("ERROR: No films extracted")
    sys.exit(1)
