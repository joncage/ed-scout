
# Uses calculations from here: https://forums.frontier.co.uk/threads/exploration-value-formulae.232000/
# https://github.com/EDSM-NET/Component/blob/master/Body/Value.php
# Ported from the EDSM code base.

star_types = {
    # Main sequence
    'O': 1,

    'B': 2,
    'B_BlueSuperGiant': 201,

    'A': 3,
    'A_BlueWhiteSuperGiant': 301,

    'F': 4,
    'F_WhiteSuperGiant': 401,

    'G': 5,
    'G_WhiteSuperGiant': 5001,

    'K': 6,
    'K_OrangeGiant': 601,

    'M': 7,
    'M_RedGiant': 701,
    'M_RedSuperGiant': 702,

    'L': 8,
    'T': 9,
    'Y': 10,

    # Proto stars
    'TTS': 11,
    'AeBe': 12,

    # Wolf-Rayet
    'W': 21,
    'WN': 22,
    'WNC': 23,
    'WC': 24,
    'WO': 25,

    # Carbon stars
    'CS': 31,
    'C': 32,
    'CN': 33,
    'CJ': 34,
    'CH': 35,
    'CHd': 36,

    'MS': 41,
    'S': 42,

    # White dwarfs
    'D': 51,
    'DA': 501,
    'DAB': 502,
    'DAO': 503,
    'DAZ': 504,
    'DAV': 505,
    'DB': 506,
    'DBZ': 507,
    'DBV': 508,
    'DO': 509,
    'DOV': 510,
    'DQ': 511,
    'DC': 512,
    'DCV': 513,
    'DX': 514,

    'N': 91,
    'H': 92,
    'SuperMassiveBlackHole': 93,

    'X': 94,

    'RoguePlanet': 111,
    'Nebula': 112,
    'StellarRemnantNebula': 113,
}

# Type mappings from EDSM\<Alias Repo>\Body\Planet\Type.php
body_types = {
    'Metal-rich body': 1,
    'Metal rich body': 1,
    'High metal content world': 2,
    'High metal content body': 2,
    'Rocky body': 11,
    'Rocky Ice world': 12,
    'Rocky ice body': 12,
    'Icy body': 21,
    'Earth-like world': 31,
    'Earthlike body': 31,
    'Water world': 41,
    'Water giant': 42,
    'Water giant with life': 43,
    'Ammonia world': 51,
    'Gas giant with water-based life': 61,
    'Gas giant with water based life': 61,
    'Gas giant with ammonia-based life': 62,
    'Gas giant with ammonia based life': 62,
    'Class I gas giant': 71,
    'Class II gas giant': 72,
    'Class III gas giant': 73,
    'Class IV gas giant': 74,
    'Class V gas giant': 75,
    'Sudarsky class I gas giant': 71,
    'Sudarsky class II gas giant': 72,
    'Sudarsky class III gas giant': 73,
    'Sudarsky class IV gas giant': 74,
    'Sudarsky class V gas giant': 75,
    'Helium-rich gas giant': 81,
    'Helium rich gas giant': 81,
    'Helium gas giant': 82,
}

terraform_states = {
    'Not terraformable': 0,
    'Candidate for terraforming': 1,
    'Terraformable': 1,
    'Terraformed': 2,
    'Terraforming': 3
}


def encode_body_type(body_info):
    if 'PlanetClass' not in body_info:
        return None  # Belt clusters for example do not have a planet class
    return body_types[body_info['PlanetClass']]


def encode_terraform_state(body_info):
    if 'TerraformState' not in body_info or len(body_info['TerraformState']) == 0:
        return None
    return terraform_states[body_info['TerraformState']]


def encode_star_type(body_info):
    return star_types[body_info['StarType']]


def appraise_body(body_info):

    main_type = None
    specific_type = None
    mass = None
    terraform_state = None
    if "StarType" in body_info:
        main_type = 'Star'
        specific_type = encode_star_type(body_info)
    else:
        # Planet
        main_type = 'Planet'
        specific_type = encode_body_type(body_info)

    if "MassEM" in body_info:
        mass = body_info['MassEM']
    else:
        mass = 0  # belts don't have a mass attribute

    terraform_state = encode_terraform_state(body_info)

    options = {
        'haveMapped': True,  # Always indicate we mapped it so we can tell the max worth
        'efficiencyBonus': True,
        'isFirstDiscoverer': not body_info['WasDiscovered'],
        'isFirstMapper': not body_info['WasMapped'],
    }

    return calculate_estimated_value(main_type, specific_type, mass, terraform_state, options)


def calculate_estimated_star_value(specific_type, mass):
    value = 1200

    # White Dwarf Star
    if specific_type in [51, 501, 502, 503, 504, 505, 506, 507, 508, 509, 510, 511, 512, 513, 514]:
        value = 14057

    # Neutron Star, Black Hole
    if specific_type in [91, 92]:
        value = 22628

    # Super-massive Black Hole
    if specific_type in [93]:
        # this is applying the same scaling to the 3.2 value as a normal black hole, not confirmed in game
        value = 33.5678

    return round(value + (mass * value / 66.25))


def calculate_planet_bonus(specific_type, terraform_state):
    bonus = 0

    if terraform_state is not None and terraform_state > 0:
        bonus = 93328

    # Metal-rich body
    if specific_type in [1]:
        if terraform_state is not None and terraform_state > 0:
            bonus = 65631

    # High metal content world / Class II gas giant
    if specific_type in [2, 72]:
        if terraform_state is not None and terraform_state > 0:
            bonus = 100677

    # Earth-like world / Water world
    if specific_type in [31, 41]:
        if terraform_state is not None and terraform_state > 0:
            bonus = 116295

        if specific_type == 31:  # Earth Like...
            bonus = 116295

    return bonus


def calculate_planet_value(specific_type):
    value = 300

    # Metal-rich body
    if specific_type in [1]:
        value = 21790

    # Ammonia world
    if specific_type in [51]:
        value = 96932

    # Class I gas giant
    if specific_type in [71]:
        value = 1656

    # High metal content world / Class II gas giant
    if specific_type in [2, 72]:
        value = 9654

    # Earth-like world / Water world
    if specific_type in [31, 41]:
        value = 64831

    return value


def calculate_estimated_planet_value(specific_type, mass, terraform_state, options):

    value = calculate_planet_value(specific_type)
    bonus = calculate_planet_bonus(specific_type, terraform_state)

    # CALCULATION
    q = 0.56591828
    value = value + bonus
    map_multiplier = 1.0

    if options['haveMapped']:
        map_multiplier = 3.3333333333

        if options['isFirstDiscoverer'] and options['isFirstMapper']:
            map_multiplier = 3.699622554

        elif not options['isFirstDiscoverer'] and options['isFirstMapper']:
            map_multiplier = 8.0956

        if options['efficiencyBonus']:
            map_multiplier *= 1.25

    value = max((value + (value * pow(mass, 0.2) * q)) * map_multiplier, 500)

    if options['isFirstDiscoverer']:
        value *= 2.6

    return round(value)


def calculate_estimated_value(main_type, specific_type, mass, terraform_state, options):

    if mass is None:
        mass = 1

    if main_type == 'Star' or main_type == 1:
        return calculate_estimated_star_value(specific_type, mass)

    if main_type == 'Planet' or main_type == 2:
        return calculate_estimated_planet_value(specific_type, mass, terraform_state, options)

    return 0
