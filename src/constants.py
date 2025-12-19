import pygame

# Screen Dimensions
SCREEN_WIDTH = 1100  # Wider for sidebar
SCREEN_HEIGHT = 850  # Taller for sidebar content (Increased from 720)
MAP_WIDTH = 800      # Playable area width
MAP_HEIGHT = 850     # Playable area height
GRID_SIZE = 40
FPS = 60

# Colors (Cyberpunk / Matrix Theme)
BLACK = (10, 10, 12)
WHITE = (240, 240, 240)
NEON_GREEN = (57, 255, 20)
NEON_RED = (255, 49, 49)
NEON_BLUE = (10, 239, 255)
NEON_PURPLE = (188, 19, 254)
NEON_YELLOW = (255, 240, 31)
NEON_PINK = (255, 20, 147)
DARK_GRID = (20, 40, 20)
PATH_COLOR = (0, 50, 50)
UI_BG = (15, 15, 20)

# Game Settings
STARTING_MONEY = 450
STARTING_LIVES = 20

# Damage Multipliers (Tower vs Enemy Type)
DAMAGE_MULTIPLIERS = {
    "FIREWALL": {
        "DDOS": 2.0,       # Effective filtering
        "MALWARE": 1.2,
        "PHISHING": 0.5,   # Bypasses filter
        "SOCIAL_ENG": 0.5
    },
    "ANTIVIRUS": {
        "MALWARE": 2.0,    # Signature match
        "RANSOMWARE": 1.5,
        "DDOS": 0.5        # Not file-based
    },
    "IDS": {
        "PHISHING": 2.0,   # Anomaly detection
        "SOCIAL_ENG": 2.0,
        "ZEUS": 1.5
    },
    "HONEYPOT": {
        "RANSOMWARE": 2.0, # Slows them significantly
        "ZEUS": 1.5,
        "DDOS": 0.5        # Overwhelmed by volume
    }
}

# Towers
TOWER_TYPES = {
    "FIREWALL": {
        "name": "Firewall",
        "cost": 100,
        "range": 120,
        "damage": 10,
        "rate": 500, # Frames per shot (lower is faster)
        "color": NEON_BLUE,
        "description": "Packet Filter. Strong vs DDoS/Malware."
    },
    "ANTIVIRUS": {
        "name": "Antivirus",
        "cost": 250,
        "range": 150,
        "damage": 15,
        "rate": 350,
        "color": NEON_GREEN,
        "description": "File Scanner. Strong vs Malware/Ransom."
    },
    "IDS": {
        "name": "IDS", # Intrusion Detection System
        "cost": 400,
        "range": 250,
        "damage": 5,
        "rate": 50, # Very fast fire rate
        "color": NEON_PURPLE,
        "description": "Anomaly Detect. Strong vs Phishing/Social."
    },
    "HONEYPOT": {
        "name": "Honeypot",
        "cost": 300,
        "range": 150,
        "damage": 0, # Does no damage directly
        "rate": 0,
        "slow_factor": 0.5, # Slows enemies by 50%
        "color": NEON_PINK,
        "description": "Traps Attackers. Strong vs Ransom/Zeus."
    }
}

# Enemies
ENEMY_TYPES = {
    "MALWARE": {
        "name": "Malware",
        "speed": 2,
        "health": 30,
        "reward": 10,
        "color": NEON_RED,
        "radius": 10
    },
    "PHISHING": {
        "name": "Phishing",
        "speed": 3.5,
        "health": 15,
        "reward": 15,
        "color": NEON_YELLOW,
        "radius": 8
    },
    "DDOS": {
        "name": "DDoS",
        "speed": 1.5,
        "health": 80,
        "reward": 25,
        "color": NEON_PURPLE,
        "radius": 15
    },
    "RANSOMWARE": {
        "name": "Ransomware",
        "speed": 1.0,
        "health": 300, # Very tanky
        "reward": 50,
        "color": NEON_RED,
        "radius": 20
    },
    "SOCIAL_ENG": {
        "name": "Social Eng.",
        "speed": 3,
        "health": 60,
        "reward": 25,
        "color": WHITE, # Represents 'innocent' looking traffic
        "radius": 14
    },
    "ZEUS": { # BOSS
        "name": "ZEUS Botnet",
        "speed": 0.5,
        "health": 3000,
        "reward": 1000,
        "color": (255, 0, 0),
        "radius": 40
    },
    "SQL_INJECTION": { # Mini-Boss
        "name": "SQL Injection",
        "speed": 2.5,
        "health": 600,
        "reward": 150,
        "color": (255, 165, 0), # Orange
        "radius": 18
    },
    "APT": { # Mega Boss
        "name": "A.P.T.", # Advanced Persistent Threat
        "speed": 0.3,
        "health": 10000,
        "reward": 5000,
        "color": (100, 0, 100), # Dark Purple
        "radius": 50
    }
}

# Perk / Roguelike System
PERK_TYPES = {
    "OVERCLOCK": {
        "name": "Overclock",
        "desc": "All towers attack 15% faster.",
        "effect": "rate",
        "value": 0.85, # Multiplier (lower is faster)
        "rarity": "COMMON",
        "color": NEON_BLUE,
        "weight": 50
    },
    "HIGH_VOLTAGE": {
        "name": "High Voltage",
        "desc": "All towers deal 20% more damage.",
        "effect": "damage",
        "value": 1.2,
        "rarity": "RARE",
        "color": NEON_RED,
        "weight": 15
    },
    "LONG_RANGE": {
        "name": "Signal Boost",
        "desc": "All towers have +20% range.",
        "effect": "range",
        "value": 1.2,
        "rarity": "COMMON",
        "color": NEON_GREEN,
        "weight": 50
    },
    "BOUNTY_HUNTER": {
        "name": "Bug Bounty",
        "desc": "Earn 20% more money from kills.",
        "effect": "reward",
        "value": 1.2,
        "rarity": "UNCOMMON",
        "color": NEON_YELLOW,
        "weight": 30
    },
    "REINFORCED": {
        "name": "Hardened Kernel",
        "desc": "Restore 5 Lives & Increase Max Lives.",
        "effect": "lives",
        "value": 5,
        "rarity": "UNCOMMON",
        "color": NEON_PINK,
        "weight": 30
    },
    "BUDGET_CUTS": {
        "name": "Open Source",
        "desc": "Towers cost 15% less to build.",
        "effect": "cost",
        "value": 0.85,
        "rarity": "RARE",
        "color": WHITE,
        "weight": 15
    },
    "QUANTUM_CORE": {
        "name": "Quantum Core",
        "desc": "LEGENDARY: +50% Damage AND +20% Speed.",
        "effect": "hybrid_dmg_spd",
        "value": 1.5, # handled specially
        "rarity": "LEGENDARY",
        "color": (0, 255, 255), # Cyan
        "weight": 2
    },
    "TIME_WARP": {
        "name": "Time Dilation",
        "desc": "LEGENDARY: Enemies move 30% slower.",
        "effect": "enemy_slow",
        "value": 0.7,
        "rarity": "LEGENDARY",
        "color": (200, 100, 255), # Lavender
        "weight": 2
    }
}

# Loot / Data Drop System
LOOT_TYPES = {
    "CRYPTO": {
        "color": (255, 215, 0), # Gold
        "radius": 8,
        "chance": 0.15, # 15% chance
        "duration": 4.0, # Seconds
        "effect": "money",
        "value": 50
    },
    "PATCH": {
        "color": (0, 255, 100), # Green
        "radius": 10,
        "chance": 0.02, # 2% chance
        "duration": 5.0,
        "effect": "life",
        "value": 1
    },
    "DATA_STREAM": {
        "color": (0, 100, 255), # Blue
        "radius": 9,
        "chance": 0.05, # 5% chance
        "duration": 6.0,
        "effect": "buff_rate",
        "value": 0.5 # 50% faster fire rate
    }
}

# Codex / Educational Content
CODEX_CONTENT = {
    "DEFENSES": {
        "FIREWALL": {
            "title": "Firewall (Packet Filter)",
            "desc": "A network security device that monitors and filters incoming and outgoing network traffic based on an organization's previously established security policies.",
            "strength": "STRONG VS: DDoS (Flood attacks), Malware (Known signatures)",
            "weakness": "WEAK VS: Phishing (Social attacks), Encrypted traffic",
            "edu": "Did you know? The first firewalls were developed in the late 1980s. They act as a barrier between a trusted internal network and untrusted external networks (like the Internet)."
        },
        "ANTIVIRUS": {
            "title": "Antivirus Software",
            "desc": "A program or set of programs that are designed to prevent, search for, detect, and remove software viruses, and other malicious software like worms, trojans, adware, and more.",
            "strength": "STRONG VS: Malware, Ransomware (File-based threats)",
            "weakness": "WEAK VS: Network floods (DDoS), Zero-day exploits (Unknown threats)",
            "edu": "Modern antivirus software uses heuristics (behavioral analysis) in addition to signature matching to catch new, unknown viruses."
        },
        "IDS": {
            "title": "Intrusion Detection System",
            "desc": "A device or software application that monitors a network or systems for malicious activity or policy violations.",
            "strength": "STRONG VS: Phishing, Social Engineering, Botnet Command & Control",
            "weakness": "WEAK VS: High-volume encrypted traffic (can be blinded)",
            "edu": "IDS can be Network-based (NIDS) or Host-based (HIDS). Unlike a Firewall which blocks, an IDS primarily alerts admins to suspicious activity."
        },
        "HONEYPOT": {
            "title": "Honeypot",
            "desc": "A security mechanism that creates a virtual trap to lure attackers. An intentionally compromised computer system that allows attackers to exploit vulnerabilities.",
            "strength": "STRONG VS: Ransomware (Slows encryption), Automated Botnets (ZEUS)",
            "weakness": "WEAK VS: DDoS (Volume doesn't care about traps)",
            "edu": "Honeypots distract attackers from valuable assets and provide early warning of advanced attacks. They are also used to study attacker behavior."
        }
    },
    "THREATS": {
        "MALWARE": {
            "title": "Malware (Malicious Software)",
            "desc": "Intrusive software that is designed to damage and destroy computers and computer systems.",
            "counter": "BEST DEFENSE: Antivirus, Firewall",
            "edu": "Includes viruses, worms, Trojan horses, ransomware, spyware, adware, and scareware."
        },
        "PHISHING": {
            "title": "Phishing",
            "desc": "A social engineering attack often used to steal user data, including login credentials and credit card numbers.",
            "counter": "BEST DEFENSE: IDS (Anomaly detection), User Training",
            "edu": "Phishing emails often create a sense of urgency to trick users into clicking malicious links."
        },
        "DDOS": {
            "title": "DDoS (Distributed Denial-of-Service)",
            "desc": "A malicious attempt to disrupt the normal traffic of a targeted server, service or network by overwhelming the target or its surrounding infrastructure with a flood of Internet traffic.",
            "counter": "BEST DEFENSE: Firewall (Filtering), Traffic Scrubbing",
            "edu": "DDoS attacks utilize botnets—networks of infected computers remotely controlled by the attacker."
        },
        "RANSOMWARE": {
            "title": "Ransomware",
            "desc": "Malware that employs encryption to hold a victim's information at ransom. A user or organization's critical data is encrypted so that they cannot access files, databases, or applications.",
            "counter": "BEST DEFENSE: Honeypot (Delay), Antivirus, Backups",
            "edu": "WannaCry (2017) was a massive ransomware attack that affected over 200,000 computers across 150 countries."
        },
        "SOCIAL_ENG": {
            "title": "Social Engineering",
            "desc": "The art of manipulating people so they give up confidential information.",
            "counter": "BEST DEFENSE: IDS, Security Awareness Training",
            "edu": "Hackers use psychological manipulation to trick users into making security mistakes or giving away sensitive information."
        },
        "ZEUS": {
            "title": "ZEUS (Botnet)",
            "desc": "A Trojan horse malware package that runs on versions of Microsoft Windows. It is often used to steal financial information.",
            "counter": "BEST DEFENSE: IDS, Honeypot, Deep Packet Inspection",
            "edu": "Zeus creates a botnet—a network of corrupted machines that can be used to perform DDoS attacks or steal data."
        }
    }
}

# Levels Configuration
LEVELS = [
    {
        "name": "Level 1: Home Network",
        "story": [
            "INCOMING TRANSMISSION...",
            "Source: Localhost",
            "Message: 'User, your personal device is behaving erratically.'",
            "Diagnosis: Basic Malware and Phishing attempts detected.",
            "Mission: Deploy Firewalls and Antivirus to secure your home network.",
            "STATUS: DANGER"
        ],
        "waypoints": [
            (0, 300), (300, 300), (300, 100), (600, 100), (600, 500), (800, 500)
        ],
        "waves": [
            [("MALWARE", 5, 1000)],
            [("MALWARE", 10, 800)],
            [("PHISHING", 5, 1000), ("MALWARE", 5, 800)],
            [("PHISHING", 10, 800), ("MALWARE", 10, 600)]
        ],
        "starting_money": 450
    },
    {
        "name": "Level 2: Corporate Server",
        "story": [
            "ENCRYPTED CHANNEL ESTABLISHED.",
            "Source: SysAdmin",
            "Message: 'The attack has spread to the company servers.'",
            "Intel: Attackers are using Social Engineering and Ransomware.",
            "Mission: Use IDS for rapid filtering and Honeypots to trap them.",
            "STATUS: CRITICAL"
        ],
        "waypoints": [
            (0, 100), (700, 100), (700, 300), (100, 300), (100, 500), (800, 500)
        ],
        "waves": [
            [("SOCIAL_ENG", 5, 1200)],
            [("RANSOMWARE", 2, 2000), ("MALWARE", 10, 500)],
            [("SOCIAL_ENG", 8, 1000), ("PHISHING", 10, 500)],
            [("RANSOMWARE", 5, 2000), ("DDOS", 5, 1000)]
        ],
        "starting_money": 600
    },
    {
        "name": "Level 3: The Core",
        "story": [
            "ALERT! ALERT! ALERT!",
            "Source: THE CORE",
            "Message: 'ZERO-DAY EXPLOIT IMMINENT.'",
            "Intel: The ZEUS Botnet Master is approaching.",
            "Mission: DEFEAT ZEUS. SAVE THE INFRASTRUCTURE.",
            "STATUS: APOCALYPSE"
        ],
        "waypoints": [
            (0, 50), (100, 550), (200, 50), (300, 550), (400, 50), (500, 550), (600, 50), (700, 550), (800, 300)
        ],
        "waves": [
            [("DDOS", 10, 500)],
            [("RANSOMWARE", 5, 1500), ("SOCIAL_ENG", 10, 800)],
            [("DDOS", 20, 200)], # Zerg rush
            [("ZEUS", 1, 0)] # BOSS FIGHT
        ],
        "starting_money": 1000
    }
]

# Legacy constants for compatibility (if needed, but we will refactor to use LEVELS)
WAYPOINTS = LEVELS[0]["waypoints"] 
WAVES = LEVELS[0]["waves"]
