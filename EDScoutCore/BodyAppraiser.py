
# Uses calculations from here: https://forums.frontier.co.uk/threads/exploration-value-formulae.232000/
# https://github.com/EDSM-NET/Component/blob/master/Body/Value.php


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
     'H': 93,

     'X': 94, # Exotic?? // Check in game

    'RoguePlanet': 111, # Check in game
    'Nebula': 112, # Check in game
    'StellarRemnantNebula': 113, # Check in game
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


def encode_terraform_state(terraform_state):
    return terraform_states[terraform_state]


def encode_star_type(body_info):
    return star_types[body_info['StarType']]

def appraise_body(body_info):

    # main_type = StarType | PlanetClass
    main_type = None
    specific_type = None
    mass = None
    terraform_state = None
    if "StarType" in body_info:
        #print(f"Star: {body_info['BodyName']}")
        main_type = 'Star'
        specific_type = encode_star_type(body_info)
    else:
        # Planet
        #print(f"Planet: {body_info['BodyName']}")
        main_type = 'Planet'
        specific_type = encode_body_type(body_info)

    if "MassEM" in body_info:
        mass = body_info['MassEM']
    else:
        mass = 0  # belts don't have a mass attribute

    terraform_state = None
    if 'TerraformState' in body_info and len(body_info['TerraformState']) > 0:
        terraform_state = encode_terraform_state(body_info['TerraformState'])

    options = {
        'haveMapped': True,  # Always indicate we mapped it so we can tell the max worth
        'efficiencyBonus': True,
        'isFirstDiscoverer': not body_info['WasDiscovered'],
        'isFirstMapper': not body_info['WasMapped'],
    }



    #     'isFirstDiscoverer'     => false,
    #     'isFirstMapper'         => false,
    #
    #     'haveMapped'            => false,
    #     'efficiencyBonus'       => false,
    #
    #     'systemBodies'          => tuple(),
    #     'isPrimaryStar'         => false,

    return calculateEstimatedValue(main_type, specific_type, mass, terraform_state, options)


def calculateEstimatedValue(main_type, specific_type, mass, terraform_state, options):

    # Merge default options
    # options = tuple_merge(tuple(
    #     'dateScanned'           => null,
    #
    #     'isFirstDiscoverer'     => false,
    #     'isFirstMapper'         => false,
    #
    #     'haveMapped'            => false,
    #     'efficiencyBonus'       => false,
    #
    #     'systemBodies'          => tuple(),
    #     'isPrimaryStar'         => false,
    # ), options)


    value  = 0
    bonus  = 0

    if mass is None:
        mass = 1

    if main_type == 'Star' or main_type == 1:
        value = 1200

        # White Dwarf Star
        if specific_type in [51, 501, 502, 503, 504, 505, 506, 507, 508, 509, 510, 511, 512, 513, 514]:
            value = 14057

        # Neutron Star, Black Hole
        if specific_type in [91, 92]:
            value = 22628

        # Supermassive Black Hole
        if specific_type in [93]:
            # this is applying the same scaling to the 3.2 value as a normal black hole, not confirmed in game
            value = 33.5678

        return round(value + (mass * value / 66.25))

    if main_type == 'Planet' or main_type == 2:
        value = 300

        if terraform_state is not None and terraform_state > 0:
            bonus = 93328

        # Metal-rich body
        if specific_type in [1]:
            value = 21790
            bonus = 0

            if terraform_state is not None and terraform_state > 0:
                bonus = 65631

        # Ammonia world
        if specific_type in [51]:
            value = 96932
            bonus = 0

        # Class I gas giant
        if specific_type in [71]:
            value = 1656
            bonus = 0

        # High metal content world / Class II gas giant
        if specific_type in [2, 72]:
            value = 9654
            bonus = 0

            if terraform_state is not None and terraform_state > 0:
                bonus = 100677

        # Earth-like world / Water world
        if specific_type in [31, 41]:
            value = 64831
            bonus = 0

            if terraform_state is not None and terraform_state > 0:
                bonus = 116295

            if specific_type == 31:  # Earth Like...
                bonus = 116295

        # CALCULATION
        q = 0.56591828
        value = value + bonus
        mapMultiplier = 1.0

        if options['haveMapped']:
            mapMultiplier = 3.3333333333

            if options['isFirstDiscoverer'] and options['isFirstMapper']:
                mapMultiplier = 3.699622554

            elif not options['isFirstDiscoverer'] and options['isFirstMapper']:
                mapMultiplier = 8.0956

            if options['efficiencyBonus']:
                mapMultiplier *= 1.25

        value = max((value + (value * pow(mass, 0.2) * q)) * mapMultiplier, 500)

        if options['isFirstDiscoverer']:
            value *= 2.6

        return round(value)

    return 0


# Notes:

#     static public function calculateEstimatedValue($mainType, $type, $mass, $terraformState, $options)
#     {
#         // Merge default options
#         $options = array_merge(array(
#             'dateScanned'           => null,
#
#             'isFirstDiscoverer'     => false,
#             'isFirstMapper'         => false,
#
#             'haveMapped'            => false,
#             'efficiencyBonus'       => false,
#
#             'systemBodies'          => array(),
#             'isPrimaryStar'         => false,
#         ), $options);
#
#
#         if(!is_null($options['dateScanned']))
#         {
#             if(strtotime($options['dateScanned']) < strtotime('2017-04-11 12:00:00'))
#             {
#                 return static::calculateEstimatedValueFrom22(
#                     $mainType,
#                     $type,
#                     $terraformState
#                 );
#             }
#
#             if(strtotime($options['dateScanned']) < strtotime('2018-12-11 12:00:00'))
#             {
#                 return static::calculateEstimatedValueFrom32(
#                     $mainType,
#                     $type,
#                     $mass,
#                     $terraformState
#                 );
#             }
#         }
#
#         $value  = 0;
#         $bonus  = 0;
#
#         if(is_null($mass))
#         {
#             $mass = 1;
#         }
#
#         if($mainType == 'Star' || $mainType == 1)
#         {
#             $value = 1200;
#
#             // White Dwarf Star
#             if(in_array($type, array(51, 501, 502, 503, 504, 505, 506, 507, 508, 509, 510, 511, 512, 513, 514)))
#             {
#                 $value = 14057;
#             }
#
#             // Neutron Star, Black Hole
#             if(in_array($type, array(91, 92)))
#             {
#                 $value = 22628;
#             }
#
#             // Supermassive Black Hole
#             if(in_array($type, array(93)))
#             {
#                 // this is applying the same scaling to the 3.2 value as a normal black hole, not confirmed in game
#                 $value = 33.5678;
#             }
#
#             return round($value + ($mass * $value / 66.25));
#         }
#
#         if($mainType == 'Planet' || $mainType == 2)
#         {
#             $value = 300;
#
#             if(!is_null($terraformState) && $terraformState > 0)
#             {
#                 $bonus = 93328;
#             }
#
#             // Metal-rich body
#             if(in_array($type, array(1)))
#             {
#                 $value = 21790;
#                 $bonus = 0;
#
#                 if(!is_null($terraformState) && $terraformState > 0)
#                 {
#                     $bonus = 65631;
#                 }
#             }
#
#             // Ammonia world
#             if(in_array($type, array(51)))
#             {
#                 $value = 96932;
#                 $bonus = 0;
#             }
#
#             // Class I gas giant
#             if(in_array($type, array(71)))
#             {
#                 $value = 1656;
#                 $bonus = 0;
#             }
#
#             // High metal content world / Class II gas giant
#             if(in_array($type, array(2, 72)))
#             {
#                 $value = 9654;
#                 $bonus = 0;
#
#                 if(!is_null($terraformState) && $terraformState > 0)
#                 {
#                     $bonus = 100677;
#                 }
#             }
#
#             // Earth-like world / Water world
#             if(in_array($type, array(31, 41)))
#             {
#                 $value = 64831;
#                 $bonus = 0;
#
#                 if(!is_null($terraformState) && $terraformState > 0)
#                 {
#                     $bonus = 116295;
#                 }
#                 if($type == 31) // Earth Like...
#                 {
#                     $bonus = 116295;
#                 }
#             }
#
#             // CALCULATION
#             $q              = 0.56591828;
#             $value          = $value + $bonus;
#             $mapMultiplier  = 1;
#
#             if($options['haveMapped'] === true)
#             {
#                 $mapMultiplier = 3.3333333333;
#
#                 if($options['isFirstDiscoverer'] === true && $options['isFirstMapper'] === true)
#                 {
#                     $mapMultiplier = 3.699622554;
#                 }
#                 elseif($options['isFirstDiscoverer'] === false && $options['isFirstMapper'] === true)
#                 {
#                     $mapMultiplier = 8.0956;
#                 }
#
#                 if($options['efficiencyBonus'] === true)
#                 {
#                     $mapMultiplier *= 1.25;
#                 }
#             }
#
#             $value = max(($value + ($value * pow($mass, 0.2) * $q)) * $mapMultiplier, 500);
#
#             if($options['isFirstDiscoverer'] === true)
#             {
#                 $value *= 2.6;
#             }
#
#             return round($value);
#         }