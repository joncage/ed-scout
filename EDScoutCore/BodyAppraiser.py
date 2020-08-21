
# Uses calculations from here: https://forums.frontier.co.uk/threads/exploration-value-formulae.232000/
# https://github.com/EDSM-NET/Component/blob/master/Body/Value.php




def appraise_star(star_info):
    # (k + (m * k / 66.25))
    return 0

def appraise_body(body_info):



    return "???"

def calculateEstimatedValue(mainType, type, mass, terraformState, options):

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

    if mainType == 'Star' or mainType == 1:
        value = 1200

        # White Dwarf Star
        if type in (51, 501, 502, 503, 504, 505, 506, 507, 508, 509, 510, 511, 512, 513, 514):
            value = 14057

        # Neutron Star, Black Hole
        if type in (91, 92):
            value = 22628

        # Supermassive Black Hole
        if type in (93):
            # this is applying the same scaling to the 3.2 value as a normal black hole, not confirmed in game
            value = 33.5678

        return round(value + (mass * value / 66.25))


    if mainType == 'Planet' or mainType == 2:
        value = 300

        if terraformState is not None and terraformState > 0:
            bonus = 93328

        # Metal-rich body
        if type in (1):
            value = 21790
            bonus = 0

            if terraformState is not None and terraformState > 0:
                bonus = 65631

        # Ammonia world
        if type in (51):
            value = 96932
            bonus = 0

        # Class I gas giant
        if type in (71):
            value = 1656
            bonus = 0

        # High metal content world / Class II gas giant
        if type in (2, 72):
            value = 9654
            bonus = 0

            if terraformState is not None and terraformState > 0:
                bonus = 100677

        # Earth-like world / Water world
        if type in (31, 41):
            value = 64831
            bonus = 0

            if terraformState is not None and terraformState > 0:
                bonus = 116295

            if type == 31: # Earth Like...
                bonus = 116295



        # CALCULATION
        q              = 0.56591828
        value          = value + bonus
        mapMultiplier  = 1

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