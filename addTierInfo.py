import sqlite3

# Database path
db_path = './pixlpets1.db'

# Connect to the database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Data to populate the 'moves' table
moves_data = [
    # FIRE
    ("Cataclysm", "Fire", "T5"), ("Overheat", "Fire", "T5"), ("Pyroclasm", "Fire", "T5"), ("Inferno", "Fire", "T5"),
    ("Explosion", "Fire", "T4"), ("Meteor", "Fire", "T4"), ("Lava Flow", "Fire", "T4"), ("Pyroblast", "Fire", "T4"),
    ("Ash Wave", "Fire", "T3"), ("Provoke", "Fire", "T3"), ("Fire Breath", "Fire", "T3"), ("Eruption", "Fire", "T3"),
    ("Dragons Rage", "Fire", "T2"), ("Flamewheel", "Fire", "T2"), ("Heat Up", "Fire", "T2"), ("Ignite", "Fire", "T2"),
    ("Combust", "Fire", "T1"), ("Scorch", "Fire", "T1"), ("Flame Whip", "Fire", "T1"), ("Fire Fang", "Fire", "T1"),
    # WATER
    ("Cryostasis", "Water", "T5"), ("Absolute Zero", "Water", "T5"), ("Tidal Wave", "Water", "T5"), ("Whirlpool", "Water", "T5"),
    ("Blizzard", "Water", "T4"), ("Glacier", "Water", "T4"), ("Snowstorm", "Water", "T4"), ("Crystallize", "Water", "T4"),
    ("Absorb", "Water", "T3"), ("Curechain", "Water", "T3"), ("Bubble Beam", "Water", "T3"), ("Torrent", "Water", "T3"),
    ("Bubble Shield", "Water", "T2"), ("Geyser", "Water", "T2"), ("Purify", "Water", "T2"), ("Ice Lance", "Water", "T2"),
    ("Blackice", "Water", "T1"), ("Waterlash", "Water", "T1"), ("Frostbite", "Water", "T1"), ("Cure", "Water", "T1"),
    # AIR
    ("Boltchain", "Air", "T5"), ("Cumulonimbus", "Air", "T5"), ("Volt Canon", "Air", "T5"),
    ("Clear Sky", "Air", "T4"), ("Lightning Slash", "Air", "T4"), ("Hurricane", "Air", "T4"),
    ("Agility", "Air", "T3"), ("Wind Blast", "Air", "T3"), ("Tesla Coil", "Air", "T3"),
    ("Aerial Aid", "Air", "T2"), ("Gale Force", "Air", "T2"), ("Rescue", "Air", "T2"),
    ("Air Rend", "Air", "T1"), ("Thunderpunch", "Air", "T1"), ("Elevate", "Air", "T1"),
    # EARTH
    ("Earthquake", "Earth", "T5"), ("Gaia Spirit", "Earth", "T5"), ("Fortress", "Earth", "T5"),
    ("Fissure", "Earth", "T4"), ("Pillar", "Earth", "T4"), ("Overgrowth", "Earth", "T4"),
    ("Aftershock", "Earth", "T3"), ("Collapse", "Earth", "T3"), ("Stone Breath", "Earth", "T3"),
    ("Bouldertoss", "Earth", "T2"), ("Dig", "Earth", "T2"), ("Lifespores", "Earth", "T2"),
    ("Boulderpunch", "Earth", "T1"), ("Rock Gun", "Earth", "T1"), ("Earth Rend", "Earth", "T1")
]

# Insert data into 'moves' table
cursor.executemany("INSERT INTO moves (name, element, tier) VALUES (?, ?, ?)", moves_data)

# Commit changes and close the connection
conn.commit()
conn.close()

"Moves table updated successfully with the new data."
