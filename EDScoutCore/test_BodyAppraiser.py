
from .BodyAppraiser import calculateEstimatedValue

def test_calculateEstimatedValue():
    scan_data = {"timestamp":"2020-08-22T15:22:37Z",
                 "event":"Scan",
                 "ScanType":"Detailed",
                 "BodyName":"Pro Eurl TE-H d10-15 6",
                 "BodyID":8,
                 "Parents":[ {"Star":0} ],
                 "StarSystem":"Pro Eurl TE-H d10-15",
                 "SystemAddress":526259374555,
                 "DistanceFromArrivalLS":1127.160767,
                 "TidalLock":False,
                 "TerraformState":"Terraformable",
                 "PlanetClass":"High metal content body",
                 "Atmosphere":"carbon dioxide atmosphere",
                 "AtmosphereType":"CarbonDioxide",
                 "AtmosphereComposition":[ { "Name":"CarbonDioxide", "Percent":73.854675 }, { "Name":"SulphurDioxide", "Percent":26.145327 } ],
                 "Volcanism":"",
                 "MassEM":0.186790,
                 "Radius":3624502.000000,
                 "SurfaceGravity":5.667173,
                 "SurfaceTemperature":388.726654,
                 "SurfacePressure":37183.542969,
                 "Landable":False,
                 "Composition":{ "Ice":0.000000, "Rock":0.665171, "Metal":0.334829 },
                 "SemiMajorAxis":337803870439.529419,
                 "Eccentricity":0.001542,
                 "OrbitalInclination":0.091064,
                 "Periapsis":56.219471,
                 "OrbitalPeriod":81764177.083969,
                 "RotationPeriod":89616.127164,
                 "AxialTilt":1.271254,
                 "WasDiscovered":False,
                 "WasMapped":False }
    main_type = 'Planet' # ['Star'. 'Planet']
    specific_type = 1  # int()
    mass = scan_data["MassEM"]
    terraform_state = 1 # scan_data["TerraformState"]
    options = {
        'haveMapped': True,
        'isFirstDiscoverer': True,
        'isFirstMapper': True,
        'efficiencyBonus': True,
    }

    estimated_value = calculateEstimatedValue(main_type, specific_type, mass, terraform_state, options)

    assert 1490667 == estimated_value
