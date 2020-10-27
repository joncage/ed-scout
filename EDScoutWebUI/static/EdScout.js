(function init() {

    function removeSystemFromNavList(systemId) {
        // Remove the system from the nav list
        let systemElement = document.getElementById(systemId);
        if (systemElement)
        {
            systemElement.remove();
        }

        // Remove any valuable bodies too.

        let bodiesToRemove = document.querySelectorAll("[data-associatedsystem='"+systemId+"']");
        let bodyElement;
        console.log(bodiesToRemove);
        for (bodyElement of bodiesToRemove)
        {
            bodyElement.remove();
        }
    }


    function setCurrentSystem(systemInfo) {
        console.log("Setting current");
        const systemId = systemInfo.SystemAddress;

        let currentSystem = getCurrentSystem();
        if (currentSystem && currentSystem === systemId.toString()){
            return; // Don't want to clear anything if we're not changing anything
        }

        removeSystemFromNavList(systemId);

        let locationElement = document.getElementById('location');
        clearCurrentLocation();
        locationElement.setAttribute('data-currentSystem', systemId);
    }

    function getCurrentSystem() {
        let locationElement = document.getElementById('location');
        if (locationElement.hasAttribute('data-currentSystem')) {
            return locationElement.getAttribute('data-currentSystem');
        }
        else {
            return null;
        }
    }

    function setTargetSystem(data) {
        console.log("Setting target system");
        let systemId = data.SystemAddress;

        // Record some data about this target so we can check it easily later
        let locationElement = document.getElementById('target-sys');
        locationElement.setAttribute('data-targetSystem', systemId.toString());
    }

    function startJumpTo(data) {
        if (data.JumpType !== "Hyperspace") {
            // Don't do anything if we're just entering supercruise
            console.log("Skipping jump");
            return
        }

        console.log("Starting jump");

        // Clear the current location as we're now jumping
        let locationElement = document.getElementById('location');

        let content = document.createElement('div');
        content.classList.add("col","text-center", "highlighted");
        content.innerText = ">> Hyperspace <<";

        let row = document.createElement('div');
        row.classList.add("row", "ml-1", "mr-1");
        row.appendChild(content);

        clearCurrentLocation();
        locationElement.appendChild(row);
    }

    function clearCurrentLocation() {
        document.getElementById('location').innerHTML = "";
        document.getElementById('high-value-scans').innerHTML = "";
        document.getElementById('low-value-scans').innerHTML = "";
    }

    function addScannedBody(payloadContent) {
        // { "timestamp":"2020-08-20T23:57:05Z", "event":"Scan", "ScanType":"Detailed", "BodyName":"Pro Eurl MO-H d10-11 2", "BodyID":27, "Parents":[ {"Star":0} ], "StarSystem":"Pro Eurl MO-H d10-11", "SystemAddress":388770122203, "DistanceFromArrivalLS":5502.835374, "TidalLock":false, "TerraformState":"", "PlanetClass":"Sudarsky class III gas giant", "Atmosphere":"", "AtmosphereComposition":[ { "Name":"Hydrogen", "Percent":74.636978 }, { "Name":"Helium", "Percent":25.363026 } ], "Volcanism":"", "MassEM":1115.081787, "Radius":76789080.000000, "SurfaceGravity":75.373241, "SurfaceTemperature":272.228607, "SurfacePressure":0.000000, "Landable":false, "SemiMajorAxis":1634133458137.512207, "Eccentricity":0.018997, "OrbitalInclination":-4.741432, "Periapsis":30.585864, "OrbitalPeriod":1122406125.068665, "RotationPeriod":113532.553386, "AxialTilt":-0.182964, "Rings":[ { "Name":"Pro Eurl MO-H d10-11 2 A Ring", "RingClass":"eRingClass_MetalRich", "MassMT":1.8852e+12, "InnerRad":1.1586e+08, "OuterRad":3.61e+08 } ], "ReserveLevel":"PristineResources", "WasDiscovered":false, "WasMapped":false }

        // If this already exists somewhere on the page, we should stop processing as we don't want to eliminate any work done by a detailed scan
        if (document.getElementById(idFromBodyName(payloadContent.BodyName)))
        {
            return;
        }

        const newBodyEntry = createDetailedBodyEntry(payloadContent);

        let container;
        if (isValuableSystem(payloadContent)){
            container = document.getElementById('high-value-scans');
        }
        else
        {
            container = document.getElementById('low-value-scans');
        }

        container.prepend(newBodyEntry);
    }

    function createIconElement(iconType, description='', elementType='i') {
        let iconElement = document.createElement(elementType)
        iconElement.classList.add("flaticon-"+iconType)
        if (description !== '') {
            iconElement.setAttribute("title", description)
        }
        return iconElement
    }

    function getBodyIcon(bodyName) {
        let bodyIcon = "";
        let lowerBodyName = bodyName.toLowerCase();
        if (lowerBodyName.includes("metal")) {
            bodyIcon = createIconElement("ingot", "Metal").outerHTML
        }
        else if (lowerBodyName.includes("icy") || lowerBodyName.includes("ice")) {
            bodyIcon = createIconElement("snowflake", "Icy").outerHTML
        }
        else if (lowerBodyName.includes("earth")) {
            bodyIcon = createIconElement("earth", "Earth-like").outerHTML
        }
        else if (lowerBodyName.includes("gas giant")) {
            bodyIcon = createIconElement("jupiter-1", "Gas giant").outerHTML
        }
        else if (lowerBodyName.includes("rock")) {
            bodyIcon = createIconElement("asteroid-3", "Rocky").outerHTML
        }
        else if (lowerBodyName.includes("water") || lowerBodyName.includes("ammonia world")) {
            bodyIcon = createIconElement("water-drops", "Water/Ammonia").outerHTML
        }
        else if (lowerBodyName.includes("belt")) {
            bodyIcon = createIconElement("asteroid-4", "Asteroid belt").outerHTML
        }
        //rocky
        //gas
        return bodyIcon;
    }

    function numberWithCommas(x) {
        return x.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
    }

    function createFlagElement(iconName, description, activeIndicator) {
        const flagElementType = 'b';
        let element = createIconElement(iconName, description, flagElementType);
        if (!activeIndicator) {
            element.classList.add("inactive")
            element.removeAttribute("title")
        }
        else {
            element.classList.add("active")
        }
        return element;
    }

    function isValuableSystem(payloadContent) {
        return payloadContent.MappedValue > 500000;
    }

    function getRingInfo(payloadContent) {
        let ringInfo = "";
        if (payloadContent.Rings) {

            let ringSeparator = document.createElement("span");
            ringSeparator.classList.add("ring-separator");
            ringSeparator.innerHTML = " ) ";

            for (let [index, ring] of payloadContent.Rings.entries()) {
                ringInfo += ringSeparator.outerHTML;

                let ringClass = ring.RingClass.replace('eRingClass_', '');
                let ringIcon = null;
                switch (ringClass) {
                    case 'MetalRich': {
                        ringIcon = createIconElement("gold-bars")
                        break;
                    }
                    case 'Metalic':
                    case 'Metallic': {
                        ringIcon = createIconElement("ingot")
                        break;
                    }
                    case 'Icy': {
                        ringIcon = createIconElement("snowflake")
                        break;
                    }
                    case 'Rocky': {
                        ringIcon = createIconElement("asteroid-3")
                        break;
                    }
                }
                ringInfo += ringIcon.outerHTML
            }

            ringInfo += ringSeparator.outerHTML;
        }

        let ringContainer = document.createElement("span");
        ringContainer.classList.add("ring");
        ringContainer.innerHTML = ringInfo;
        return ringContainer.outerHTML;
    }

    function createGravityIndicator(payloadContent) {

        let gravityIndicator = document.createElement("span")

        // Only bother highlighting if the planet is landable and the gravity is worrying enough
        const gravityWarningThresh = 1.0
        const gravityAlertThresh = 2.0
        let severityClass = null;
        let gravityText = null;
        if (payloadContent.Landable) {
            let surfaceGravity = payloadContent.SurfaceGravity/10.0; // Divided the values by 10 as they appear to be a factor of 10 too large for some reason (compared to the system map + EDSM).
            console.log("Surface gravity: " + surfaceGravity.toString())

            if (surfaceGravity >= gravityAlertThresh) {
                severityClass = "gravity-alert"
            }
            else if (surfaceGravity >= gravityWarningThresh) {
                severityClass = "gravity-warning"
            }
            else {
                severityClass = "gravity-good"
            }
            gravityText = surfaceGravity.toFixed(1)+""
        }
        else
        {
            gravityText = "X.X"; // Add some essentially blank text to pad things out as it's mono-spaced.
            severityClass = "gravity-hidden";
            gravityIndicator.classList.add("inactive")
        }
        gravityIndicator.classList.add("gravity-indicator", "rounded", "border-0", severityClass)

        let landable = createFlagElement('lander', 'Landable', payloadContent.Landable);
        landable.classList.add('landable');

        gravityIndicator.innerHTML = landable.outerHTML + " " +  gravityText


        return gravityIndicator.outerHTML
    }

    function createDetailedBodyEntry(payloadContent) {

        let discovered = payloadContent.WasDiscovered;
        let chartedStyle = discovered?"charted":"uncharted";
        let bodyId = idFromBodyName(payloadContent.BodyName);

        if (isValuableSystem(payloadContent)) {
            chartedStyle = "highlighted"
        }

        let spacer = document.createElement('div');
        spacer.classList.add("col-1", "system");

        let bodySymbol = "";
        if (payloadContent.PlanetClass) {
            bodySymbol = createIconElement('jupiter-3').outerHTML;
        }
        else if (payloadContent.StarType) {
            bodySymbol = createIconElement('star').outerHTML;
        }
        else {
            if (payloadContent.BodyClass.includes("Belt")) {
                bodySymbol = createIconElement('asteroid-4').outerHTML;
            }
        }
        let rings = getRingInfo(payloadContent);
        let bodyName = document.createElement('div');
        bodyName.classList.add("col-2", "system", chartedStyle, "text-left");
        let simpleBodyName =  payloadContent.BodyName.replace(payloadContent.StarSystem, "")
        bodyName.innerHTML = bodySymbol+" "+simpleBodyName;

        let bodyType = document.createElement('div');
        bodyType.classList.add("col", "pr-0", "mr-0", "system", chartedStyle);
        if (payloadContent.PlanetClass) {
            bodyType.innerHTML = getBodyIcon(payloadContent.PlanetClass)+" "+rings+" "+payloadContent.PlanetClass;
        }
        else if (payloadContent.StarType) {
            bodyType.innerHTML = createIconElement('star').outerHTML+" "+payloadContent.StarType;
        }
        else if (payloadContent.BodyClass) {
            bodyType.innerHTML = createIconElement('asteroid-4').outerHTML+" "+payloadContent.BodyClass;
        }

        let distance = document.createElement('div');
        // DistanceFromArrivalLS
        // numberWithCommas
        distance.classList.add("col-auto", "pl-2", "ml-0", "system", chartedStyle);
        distance.innerHTML = numberWithCommas(payloadContent.DistanceFromArrivalLS.toFixed(0)).toString();

        let extra_info = ""
        if (payloadContent.StarType) {
            payloadContent.Volcanism = false;
            payloadContent.TerraformState = "";
            payloadContent.Landable = false;
            payloadContent.WasMapped = true; // Not strictly true but you can't map stars
        }

        extra_info += createFlagElement('volcano', 'Volcanism', payloadContent.Volcanism).outerHTML;
        extra_info += createFlagElement('cooling-tower', 'Terraformable', payloadContent.TerraformState).outerHTML;
        extra_info += createFlagElement('flag-outline-on-a-pole-with-stars-around', 'Unmapped', !payloadContent.WasMapped).outerHTML;
        extra_info += createGravityIndicator(payloadContent)

        let bodyInfo = document.createElement('div');
        bodyInfo.classList.add("col-auto", "system", chartedStyle);
        bodyInfo.innerHTML = extra_info;

        let bodyValue = document.createElement('div');
        bodyValue.classList.add("col-2", "system", chartedStyle, "text-right");
        bodyValue.innerText = numberWithCommas(payloadContent.MappedValue);

        // De-select anything that's currently selected.
        let prevLatestScanElement = document.querySelector('.latest-scan');
        if (prevLatestScanElement) {
            prevLatestScanElement.classList.remove('latest-scan');
        }

        let row = document.createElement('div');
        row.classList.add("row", "ml-1", "mr-1", "latest-scan");
        row.innerHTML =
            spacer.outerHTML+
            bodyName.outerHTML+
            bodyType.outerHTML+
            distance.outerHTML+
            bodyInfo.outerHTML+
            bodyValue.outerHTML;
        row.setAttribute('data-associatedsystem', payloadContent.SystemAddress);
        row.id = bodyId;

        return row;
    }

    function createSystemEntry(systemInfo) {
        let row = document.createElement('div');
        row.classList.add("row", "ml-1", "mr-1");
        row.id = systemInfo.SystemAddress;
        let chartedSpecificStyle = systemInfo.charted?"charted":"uncharted";

        let systemName = document.createElement('div');
        systemName.classList.add("col", "system", chartedSpecificStyle);
        let starClass = "["+(systemInfo.StarClass?systemInfo.StarClass:"?")+"]";
        systemName.innerHTML = createIconElement("solar-system").outerHTML+" "+starClass+" "+systemInfo.StarSystem;

        let systemValue = document.createElement('div');
        systemValue.classList.add("col-2", "system", chartedSpecificStyle, "text-right");
        let mappedValue = systemInfo.charted?systemInfo.estimatedValueMapped:"?";
        systemValue.innerText = numberWithCommas(mappedValue);

        row.innerHTML = systemName.outerHTML+systemValue.outerHTML;

        return row;
    }



    function createBodyEntry(body, system_id) {

        let spacer = document.createElement('div');
        spacer.classList.add("col-1", "system");

        let bodyName = document.createElement('div');
        bodyName.classList.add("col", "system", "charted");
        bodyName.innerHTML = createIconElement('jupiter-3').outerHTML+" "+body.bodyName;

        let bodyValue = document.createElement('div');
        bodyValue.classList.add("col-2", "system", "charted", "text-right");
        bodyValue.innerText = numberWithCommas(body.valueMax);

        let row = document.createElement('div');
        row.classList.add("row", "ml-1", "mr-1");
        row.innerHTML = spacer.outerHTML+bodyName.outerHTML+bodyValue.outerHTML;
        row.setAttribute('data-associatedsystem', system_id);
        row.id = body.bodyId;

        return row;
    }

    function finishJump(data)
    {
        console.log("Finished jump");

        // Update the current system
        setCurrentSystem(data);
    }

    function hideCurrentTarget() {
        // <div id="target-sys" data-target-sys="" class="container statusInfo d-none">
        let nextTargetContainer = document.getElementById('target-sys');
        nextTargetContainer.classList.add("d-none");
    }

    function showCurrentTarget() {
        // <div id="target-sys" data-target-sys="" class="container statusInfo d-none">
        let nextTargetContainer = document.getElementById('target-sys');
        if (nextTargetContainer.classList.contains("d-none"))
        {
            nextTargetContainer.classList.remove("d-none");
        }
    }

    function addNewSystemToContainer(systemInfo, container) {

        let currentSystem = getCurrentSystem();
        let existingSystemEntry = document.getElementById(systemInfo.SystemAddress);
        if (existingSystemEntry) {
            return; // Do nothing if the element already exists to avoid a duplicate.
        }

        let systemEntry = createSystemEntry(systemInfo)
        container.appendChild(systemEntry);

        if (systemInfo.valuableBodies)
        {
            let body;
            for (body of systemInfo.valuableBodies) {

                let nameText = body.bodyName;
                const systemName = systemInfo['name'];
                body.bodyName = nameText.replace(systemName, "");
                body.bodyId = idFromBodyName(body.bodyName);

                console.log(body);
                container.appendChild(createBodyEntry(body, systemInfo.SystemAddress));
            }
        }
    }

    function idFromBodyName(bodyName) {
        return bodyName.replace(" ","-");
    }

    function finishScanningBody(data) {
        let existingBodyEntry = document.getElementById(idFromBodyName(data.BodyName));
        if (existingBodyEntry) {
            console.log("Updating existing body")

            for (child of existingBodyEntry.childNodes) {
                let styleChanged = false;
                // Clear any uncharted styles as this has now been mapped.
                if (child.classList.contains("uncharted")) {
                    child.classList.remove("uncharted");
                    styleChanged = true;
                }

                // Clear any high value styles
                if (child.classList.contains("highlighted")) {
                    child.classList.remove("highlighted");
                    styleChanged = true;
                }

                // Format it as a charted system now.
                if (styleChanged) {
                    child.classList.add("charted");
                }
            }

            // Clear the un-mapped flag
            let mappedIcon = existingBodyEntry.querySelector(".flaticon-flag-outline-on-a-pole-with-stars-around");
            mappedIcon.classList.remove("active")
            mappedIcon.classList.add("inactive")
            //mappedIcon.style.color = "#4CE0E1";

            // If it's in the valuable list, move it into the less valuable list
            document.getElementById('low-value-scans').prepend(existingBodyEntry)
        }
        else
        {
            console.log("Couldn't find: "+data.BodyName)
        }
    }



    function postData(payload) {
        console.log(payload);
        let payloadContent = payload.data;
        if (payloadContent.type === 'NewRoute') {
            console.log('Clearing');
            let navRouteContainer = document.getElementById('nav-route')
            navRouteContainer.innerHTML = '';
            // If we're about to plot a new route, it'll set the next target as the first item in the navroute.
            hideCurrentTarget();
        }
        else if (payloadContent.type === 'JournalEntry')
        {
            switch(payloadContent.event)
            {
                case "FSDTarget": { // When you set a new jump target in the galaxy map
                    setTargetSystem(payloadContent);
                    break;
                }
                case "Location": {
                    setCurrentSystem(payloadContent);
                    break;
                }
                case "StartJump": { // When 3..2..1 starts
                    startJumpTo(payloadContent);
                    break;
                }
                case "FSDJump": { // When you drop out of hyperspace
                    finishJump(payloadContent);
                    break;
                }
                case "Scan": { // When you identify a body in the FSS
                    addScannedBody(payloadContent);
                    break;
                }
                case "SAAScanComplete" : { // When you do a detailed scan
                    finishScanningBody(payloadContent);
                }
            }
        }
        else {
            console.log('Processing system report', payloadContent)

            if (payloadContent.type === 'System-NavRoute')
            {
                // If no current system set (or it matches the one that's already set because we just cleared it and we're waiting for the data to populate it), the first one we get should be current
                let currentSystem = getCurrentSystem();
                let container = null;
                let systemId = payloadContent.SystemAddress.toString();
                if ((currentSystem === null) || (currentSystem === "") || (currentSystem === systemId))
                {
                    console.log('Assigning new system to current-system list; ', currentSystem)
                    setCurrentSystem(payloadContent);
                    container = document.getElementById('location');
                }
                else
                {
                    console.log('Assigning new system to nav list; ', currentSystem)
                    let navRouteContainer = document.getElementById('nav-route')
                    container = navRouteContainer;
                }

                addNewSystemToContainer(payloadContent, container)
            }
            else
            {
                // This is going to be one of the other routines that wants a system report showing
                if (payloadContent.type === 'System-FSDTarget')
                {
                    // If this doesn't exist in the nav list, it's a unique target the commander has selected independently of the selected route
                    // As such, we need to update the system in the target area
                    // Make sure we clear the ID so it doesn't interfere with other checks (we can have systems in the target area that are also in the navlist

                    let container = document.getElementById('target-sys');
                    container.innerHTML = "";

                    if (document.getElementById(payloadContent.SystemAddress)) {
                        // This element exists already in the navlist so make sure the next-address is hidden to avoid a duplicate
                        hideCurrentTarget();
                    }
                    else
                    {
                        showCurrentTarget();
                        addNewSystemToContainer(payloadContent, container);
                    }
                }
                else if ((payloadContent.type === 'System-Location') || // Update the system recorded in 'current system'
                    (payloadContent.type === 'System-FSDJump')) // Happens at the end of the jump so update the current system.
                {
                    addNewSystemToContainer(payloadContent, document.getElementById('location'));
                }


            }
        }
    }

    let enableBackendConnections = true;

    function WrapWithEventType(type, entryContent) {
        let wrap = {'data': {'type': type}};
        wrap.data = $.extend(true, {}, wrap.data, entryContent);
        return wrap;
    }

    let tests = {};

    tests["just-startup"] = [
        // Simulate a normal startup
        WrapWithEventType("JournalEntry", {"timestamp":"2020-08-08T23:07:06Z", "event":"Location", "Docked":false, "StarSystem":"Sifeae EH-C c13-3", "SystemAddress":913385362290, 'StarPos': [2899.96875, 206.34375, 801.6875], "SystemAllegiance":"", "SystemEconomy":"$economy_None;", "SystemEconomy_Localised":"None", "SystemSecondEconomy":"$economy_None;", "SystemSecondEconomy_Localised":"None", "SystemGovernment":"$government_None;", "SystemGovernment_Localised":"None", "SystemSecurity":"$GAlAXY_MAP_INFO_state_anarchy;", "SystemSecurity_Localised":"Anarchy", "Population":0, "Body":"V447 Lacertae", "BodyID":0, "BodyType":"Star" }),
    ];

    tests["planets-and-systems-listed-after-nav-route-sent"] = [
        // Simulate a normal startup
        WrapWithEventType("JournalEntry", {"timestamp":"2020-08-08T23:07:06Z", "event":"Location", "Docked":false, "StarSystem":"Sifeae EH-C c13-3", "SystemAddress":913385362290, 'StarPos': [2899.96875, 206.34375, 801.6875], "SystemAllegiance":"", "SystemEconomy":"$economy_None;", "SystemEconomy_Localised":"None", "SystemSecondEconomy":"$economy_None;", "SystemSecondEconomy_Localised":"None", "SystemGovernment":"$government_None;", "SystemGovernment_Localised":"None", "SystemSecurity":"$GAlAXY_MAP_INFO_state_anarchy;", "SystemSecurity_Localised":"Anarchy", "Population":0, "Body":"V447 Lacertae", "BodyID":0, "BodyType":"Star" }),
        // Plot a nav route
        WrapWithEventType("NewRoute"),
        WrapWithEventType("JournalEntry", {"timestamp":"2020-08-08T23:07:12Z", "event":"FSDTarget", "Name":'Pro Eurl YJ-Q d5-18', "SystemAddress":629388954035, "StarClass":"F", "RemainingJumpsInRoute":1 }),
        WrapWithEventType("System-NavRoute", {'StarSystem': 'Sifeae EH-C c13-3', 'SystemAddress': 913385362290, 'StarPos': [2899.96875, 206.34375, 801.6875], 'StarClass': 'K', 'id': 55216390, 'id64': 913385362290, 'name': 'Sifeae EH-C c13-3', 'url': 'https://www.edsm.net/en/system/bodies/id/55216390/name/Sifeae+EH-C+c13-3', 'estimatedValue': 112130, 'estimatedValueMapped': 368117, 'valuableBodies': [{'bodyId': 226907740, 'bodyName': 'Sifeae EH-C c13-3 A 1', 'distance': 1250, 'valueMax': 365696}], 'charted': true}),
        WrapWithEventType("System-NavRoute", {'StarSystem': 'Pro Eurl YJ-Q d5-18', 'SystemAddress': 629388954035, 'StarPos': [2035.6875, 381.59375, 739.6875], 'StarClass': 'F', 'id': 55108083, 'id64': 629388954035, 'name': 'Pro Eurl YJ-Q d5-18', 'url': 'https://www.edsm.net/en/system/bodies/id/55108083/name/Pro+Eurl+YJ-Q+d5-18', 'estimatedValue': 39863, 'estimatedValueMapped': 127197, 'valuableBodies': [], 'charted': true}),
        WrapWithEventType("System-NavRoute", {'StarSystem': 'Pro Eurl DV-E c12-2', 'SystemAddress': 637098300266, 'StarPos': [2083.0, 374.71875, 748.09375], 'StarClass': 'K', 'charted': false})
    ];

    tests["planets-and-systems-removed-when-jump-finishes"] = [
        // Simulate a normal startup
        WrapWithEventType("JournalEntry", {"timestamp":"2020-08-08T23:07:06Z", "event":"Location", "Docked":false, "StarSystem":"Sifeae EH-C c13-3", "SystemAddress":913385362290, 'StarPos': [2899.96875, 206.34375, 801.6875], "SystemAllegiance":"", "SystemEconomy":"$economy_None;", "SystemEconomy_Localised":"None", "SystemSecondEconomy":"$economy_None;", "SystemSecondEconomy_Localised":"None", "SystemGovernment":"$government_None;", "SystemGovernment_Localised":"None", "SystemSecurity":"$GAlAXY_MAP_INFO_state_anarchy;", "SystemSecurity_Localised":"Anarchy", "Population":0, "Body":"V447 Lacertae", "BodyID":0, "BodyType":"Star" }),
        // Plot a nav route
        WrapWithEventType("NewRoute"),
        WrapWithEventType("JournalEntry", {"timestamp":"2020-08-08T23:07:12Z", "event":"FSDTarget", "Name":'Pro Eurl YJ-Q d5-18', "SystemAddress":629388954035, "StarClass":"F", "RemainingJumpsInRoute":1 }),
        WrapWithEventType("System-NavRoute", {'StarSystem': 'Sifeae EH-C c13-3', 'SystemAddress': 913385362290, 'StarPos': [2899.96875, 206.34375, 801.6875], 'StarClass': 'K', 'id': 55216390, 'id64': 913385362290, 'name': 'Sifeae EH-C c13-3', 'url': 'https://www.edsm.net/en/system/bodies/id/55216390/name/Sifeae+EH-C+c13-3', 'estimatedValue': 112130, 'estimatedValueMapped': 368117, 'valuableBodies': [{'bodyId': 226907740, 'bodyName': 'Sifeae EH-C c13-3 A 1', 'distance': 1250, 'valueMax': 365696},{'bodyId': 226907741, 'bodyName': 'Sifeae EH-C c13-3 A 2', 'distance': 120, 'valueMax': 36596}], 'charted': true}),
        WrapWithEventType("System-NavRoute", {'StarSystem': 'Pro Eurl YJ-Q d5-18', 'SystemAddress': 629388954035, 'StarPos': [2035.6875, 381.59375, 739.6875], 'StarClass': 'F', 'id': 55108083, 'id64': 629388954035, 'name': 'Pro Eurl YJ-Q d5-18', 'url': 'https://www.edsm.net/en/system/bodies/id/55108083/name/Pro+Eurl+YJ-Q+d5-18', 'estimatedValue': 39863, 'estimatedValueMapped': 127197, 'valuableBodies': [{'bodyId': 226907740, 'bodyName': 'Pro Eurl YJ-Q d5-18 A 1', 'distance': 1250, 'valueMax': 365696},{'bodyId': 226907741, 'bodyName': 'Pro Eurl YJ-Q d5-18 A 2', 'distance': 120, 'valueMax': 36596}], 'charted': true}),
        WrapWithEventType("System-NavRoute", {'StarSystem': 'Pro Eurl DV-E c12-2', 'SystemAddress': 637098300266, 'StarPos': [2083.0, 374.71875, 748.09375], 'StarClass': 'K', 'charted': false}),
        // Do the jump
        WrapWithEventType("JournalEntry", {"timestamp":"2020-08-08T23:08:14Z", "event":"StartJump", "JumpType":"Hyperspace", "StarSystem":"Pro Eurl YJ-Q d5-18", "SystemAddress":629388954035, "StarClass":"M" }),
        WrapWithEventType("JournalEntry", {"timestamp":"2020-08-08T23:07:12Z", "event":"FSDTarget", "Name":'Pro Eurl DV-E c12-2', "SystemAddress":637098300266, "StarClass":"F", "RemainingJumpsInRoute":1 }),
        WrapWithEventType("JournalEntry", {"timestamp":"2020-08-08T23:09:55Z", "event":"FSDJump", "StarSystem":"Pro Eurl YJ-Q d5-18", "SystemAddress":629388954035, "StarPos":[25.06250,13.53125,19.93750], "SystemAllegiance":"", "SystemEconomy":"$economy_None;", "SystemEconomy_Localised":"None", "SystemSecondEconomy":"$economy_None;", "SystemSecondEconomy_Localised":"None", "SystemGovernment":"$government_None;", "SystemGovernment_Localised":"None", "SystemSecurity":"$GAlAXY_MAP_INFO_state_anarchy;", "SystemSecurity_Localised":"Anarchy", "Population":0, "Body":"Core Sys Sector ON-T b3-5 A", "BodyID":2, "BodyType":"Star", "JumpDist":51.088, "FuelUsed":7.591439, "FuelLevel":24.408562 })
    ];

    tests["planets-and-systems-removed-when-jump-finishes-after-missed-startup"] = [
        // Plot a nav route
        WrapWithEventType("NewRoute"),
        WrapWithEventType("JournalEntry", {"timestamp":"2020-08-08T23:07:12Z", "event":"FSDTarget", "Name":'Pro Eurl YJ-Q d5-18', "SystemAddress":629388954035, "StarClass":"F", "RemainingJumpsInRoute":1 }),
        WrapWithEventType("System-NavRoute", {'StarSystem': 'Sifeae EH-C c13-3', 'SystemAddress': 913385362290, 'StarPos': [2899.96875, 206.34375, 801.6875], 'StarClass': 'K', 'id': 55216390, 'id64': 913385362290, 'name': 'Sifeae EH-C c13-3', 'url': 'https://www.edsm.net/en/system/bodies/id/55216390/name/Sifeae+EH-C+c13-3', 'estimatedValue': 112130, 'estimatedValueMapped': 368117, 'valuableBodies': [{'bodyId': 226907740, 'bodyName': 'Sifeae EH-C c13-3 A 1', 'distance': 1250, 'valueMax': 365696}], 'charted': true}),
        WrapWithEventType("System-NavRoute", {'StarSystem': 'Pro Eurl YJ-Q d5-18', 'SystemAddress': 629388954035, 'StarPos': [2035.6875, 381.59375, 739.6875], 'StarClass': 'F', 'id': 55108083, 'id64': 629388954035, 'name': 'Pro Eurl YJ-Q d5-18', 'url': 'https://www.edsm.net/en/system/bodies/id/55108083/name/Pro+Eurl+YJ-Q+d5-18', 'estimatedValue': 39863, 'estimatedValueMapped': 127197, 'valuableBodies': [], 'charted': true}),
        WrapWithEventType("System-NavRoute", {'StarSystem': 'Pro Eurl DV-E c12-2', 'SystemAddress': 637098300266, 'StarPos': [2083.0, 374.71875, 748.09375], 'StarClass': 'K', 'charted': false}),
        // Do the jump
        WrapWithEventType("JournalEntry", {"timestamp":"2020-08-08T23:08:14Z", "event":"StartJump", "JumpType":"Hyperspace", "StarSystem":"Pro Eurl YJ-Q d5-18", "SystemAddress":629388954035, "StarClass":"M" }),
        WrapWithEventType("JournalEntry", {"timestamp":"2020-08-08T23:07:12Z", "event":"FSDTarget", "Name":'Pro Eurl DV-E c12-2', "SystemAddress":637098300266, "StarClass":"F", "RemainingJumpsInRoute":1 }),
        WrapWithEventType("JournalEntry", {"timestamp":"2020-08-08T23:09:55Z", "event":"FSDJump", "StarSystem":"Pro Eurl YJ-Q d5-18", "SystemAddress":629388954035, "StarPos":[25.06250,13.53125,19.93750], "SystemAllegiance":"", "SystemEconomy":"$economy_None;", "SystemEconomy_Localised":"None", "SystemSecondEconomy":"$economy_None;", "SystemSecondEconomy_Localised":"None", "SystemGovernment":"$government_None;", "SystemGovernment_Localised":"None", "SystemSecurity":"$GAlAXY_MAP_INFO_state_anarchy;", "SystemSecurity_Localised":"Anarchy", "Population":0, "Body":"Core Sys Sector ON-T b3-5 A", "BodyID":2, "BodyType":"Star", "JumpDist":51.088, "FuelUsed":7.591439, "FuelLevel":24.408562 })
    ];

    tests["supercruise-not-cancelling-next-target"] = [
        // Plot a nav route
        WrapWithEventType("NewRoute"),
        WrapWithEventType("JournalEntry", {"timestamp":"2020-08-08T23:07:12Z", "event":"FSDTarget", "Name":'Pro Eurl YJ-Q d5-18', "SystemAddress":629388954035, "StarClass":"F", "RemainingJumpsInRoute":1 }),
        WrapWithEventType("System-NavRoute", {'StarSystem': 'Sifeae EH-C c13-3', 'SystemAddress': 913385362290, 'StarPos': [2899.96875, 206.34375, 801.6875], 'StarClass': 'K', 'id': 55216390, 'id64': 913385362290, 'name': 'Sifeae EH-C c13-3', 'url': 'https://www.edsm.net/en/system/bodies/id/55216390/name/Sifeae+EH-C+c13-3', 'estimatedValue': 112130, 'estimatedValueMapped': 368117, 'valuableBodies': [{'bodyId': 226907740, 'bodyName': 'Sifeae EH-C c13-3 A 1', 'distance': 1250, 'valueMax': 365696}], 'charted': true}),
        WrapWithEventType("System-NavRoute", {'StarSystem': 'Pro Eurl YJ-Q d5-18', 'SystemAddress': 629388954035, 'StarPos': [2035.6875, 381.59375, 739.6875], 'StarClass': 'F', 'id': 55108083, 'id64': 629388954035, 'name': 'Pro Eurl YJ-Q d5-18', 'url': 'https://www.edsm.net/en/system/bodies/id/55108083/name/Pro+Eurl+YJ-Q+d5-18', 'estimatedValue': 39863, 'estimatedValueMapped': 127197, 'valuableBodies': [], 'charted': true}),
        WrapWithEventType("System-NavRoute", {'StarSystem': 'Pro Eurl DV-E c12-2', 'SystemAddress': 637098300266, 'StarPos': [2083.0, 374.71875, 748.09375], 'StarClass': 'K', 'charted': false}),
        // Do the jump
        WrapWithEventType("JournalEntry", {"timestamp":"2020-08-08T23:08:14Z", "event":"StartJump", "JumpType":"Hyperspace", "StarSystem":"Pro Eurl YJ-Q d5-18", "SystemAddress":629388954035, "StarClass":"M" }),
        WrapWithEventType("JournalEntry", {"timestamp":"2020-08-08T23:07:12Z", "event":"FSDTarget", "Name":'Pro Eurl DV-E c12-2', "SystemAddress":637098300266, "StarClass":"F", "RemainingJumpsInRoute":1 }),
        WrapWithEventType("JournalEntry", {"timestamp":"2020-08-08T23:09:55Z", "event":"FSDJump", "StarSystem":"Pro Eurl YJ-Q d5-18", "SystemAddress":629388954035, "StarPos":[25.06250,13.53125,19.93750], "SystemAllegiance":"", "SystemEconomy":"$economy_None;", "SystemEconomy_Localised":"None", "SystemSecondEconomy":"$economy_None;", "SystemSecondEconomy_Localised":"None", "SystemGovernment":"$government_None;", "SystemGovernment_Localised":"None", "SystemSecurity":"$GAlAXY_MAP_INFO_state_anarchy;", "SystemSecurity_Localised":"Anarchy", "Population":0, "Body":"Core Sys Sector ON-T b3-5 A", "BodyID":2, "BodyType":"Star", "JumpDist":51.088, "FuelUsed":7.591439, "FuelLevel":24.408562 }),
        WrapWithEventType("JournalEntry", { "timestamp":"2020-08-16T23:01:10Z", "event":"StartJump", "JumpType":"Supercruise" })
    ];



    tests["scans"] = [
        // Plot a nav route
        WrapWithEventType("NewRoute"),
        WrapWithEventType("JournalEntry", {"timestamp":"2020-08-08T23:07:12Z", "event":"FSDTarget", "Name":'Pro Eurl YJ-Q d5-18', "SystemAddress":629388954035, "StarClass":"F", "RemainingJumpsInRoute":1 }),
        WrapWithEventType("System-NavRoute", {'StarSystem': 'Sifeae EH-C c13-3', 'SystemAddress': 913385362290, 'StarPos': [2899.96875, 206.34375, 801.6875], 'StarClass': 'K', 'id': 55216390, 'id64': 913385362290, 'name': 'Sifeae EH-C c13-3', 'url': 'https://www.edsm.net/en/system/bodies/id/55216390/name/Sifeae+EH-C+c13-3', 'estimatedValue': 112130, 'estimatedValueMapped': 368117, 'valuableBodies': [], 'charted': true}),
        WrapWithEventType("System-NavRoute", {'StarSystem': 'Pro Eurl YJ-Q d5-18', 'SystemAddress': 629388954035, 'StarPos': [2035.6875, 381.59375, 739.6875], 'StarClass': 'F', 'id': 55108083, 'id64': 629388954035, 'name': 'Pro Eurl YJ-Q d5-18', 'url': 'https://www.edsm.net/en/system/bodies/id/55108083/name/Pro+Eurl+YJ-Q+d5-18', 'estimatedValue': 39863, 'estimatedValueMapped': 127197, 'valuableBodies': [], 'charted': true}),
        WrapWithEventType("System-NavRoute", {'StarSystem': 'Pro Eurl DV-E c12-2', 'SystemAddress': 637098300266, 'StarPos': [2083.0, 374.71875, 748.09375], 'StarClass': 'K', 'charted': false}),
        // Show some scans


        WrapWithEventType("JournalEntry", { "timestamp":"2020-08-27T22:32:19Z", "event":"Scan", "MappedValue": 12345, "ScanType":"AutoScan", "BodyName":"Sifeae TP-F d11-27", "BodyID":0, "StarSystem":"Sifeae TP-F d11-27", "SystemAddress":938811132387, "DistanceFromArrivalLS":0.000000, "StarType":"F", "Subclass":5, "StellarMass":1.156250, "Radius":771655168.000000, "AbsoluteMagnitude":3.957947, "Age_MY":1876, "SurfaceTemperature":6705.000000, "Luminosity":"Vb", "RotationPeriod":510875.821241, "AxialTilt":0.000000, "WasDiscovered":false, "WasMapped":false }),
        WrapWithEventType("JournalEntry", { "timestamp":"2020-08-27T20:45:27Z", "event":"Scan", "MappedValue": 12345, "ScanType":"Detailed", "BodyName":"C 1", "BodyID":5, "Parents":[ {"Star":4}, {"Null":0} ], "StarSystem":"Pro Eurl YJ-Q d5-18", "SystemAddress":629388954035, "DistanceFromArrivalLS":3952.286837, "TidalLock":true, "TerraformState":"", "PlanetClass":"High metal content body", "Atmosphere":"", "AtmosphereType":"None", "Volcanism":"", "MassEM":0.002846, "Radius":933771.437500, "SurfaceGravity":1.300979, "SurfaceTemperature":300.952332, "SurfacePressure":0.000000, "Landable":true, "Materials":[ { "Name":"iron", "Percent":23.895164 }, { "Name":"nickel", "Percent":18.073303 }, { "Name":"sulphur", "Percent":16.917128 }, { "Name":"carbon", "Percent":14.225550 }, { "Name":"phosphorus", "Percent":9.107442 }, { "Name":"vanadium", "Percent":5.867821 }, { "Name":"germanium", "Percent":4.995381 }, { "Name":"selenium", "Percent":2.647673 }, { "Name":"cadmium", "Percent":1.855568 }, { "Name":"molybdenum", "Percent":1.560341 }, { "Name":"technetium", "Percent":0.854634 } ], "Composition":{ "Ice":0.000000, "Rock":0.669572, "Metal":0.330428 }, "SemiMajorAxis":15086603164.672852, "Eccentricity":0.001070, "OrbitalInclination":-0.039211, "Periapsis":254.825325, "OrbitalPeriod":1905546.903610, "RotationPeriod":1905547.346105, "AxialTilt":-0.037440, "WasDiscovered":true, "WasMapped":true }),
        WrapWithEventType("JournalEntry", { "timestamp":"2020-08-27T20:45:53Z", "event":"Scan", "MappedValue": 123, "ScanType":"Detailed", "BodyName":"C 6 a", "BodyID":11, "Parents":[ {"Planet":10}, {"Star":4}, {"Null":0} ], "StarSystem":"Pro Eurl YJ-Q d5-18", "SystemAddress":629388954035, "DistanceFromArrivalLS":4098.951070, "TidalLock":true, "TerraformState":"", "PlanetClass":"Rocky body", "Atmosphere":"", "AtmosphereType":"None", "Volcanism":"", "MassEM":0.000184, "Radius":396043.750000, "SurfaceGravity":0.466752, "SurfaceTemperature":174.171570, "SurfacePressure":0.000000, "Landable":true, "Materials":[ { "Name":"iron", "Percent":19.803368 }, { "Name":"sulphur", "Percent":17.687706 }, { "Name":"nickel", "Percent":14.978438 }, { "Name":"carbon", "Percent":14.873528 }, { "Name":"phosphorus", "Percent":9.522289 }, { "Name":"chromium", "Percent":8.906232 }, { "Name":"zinc", "Percent":5.381814 }, { "Name":"germanium", "Percent":5.222922 }, { "Name":"niobium", "Percent":1.353455 }, { "Name":"yttrium", "Percent":1.182832 }, { "Name":"tungsten", "Percent":1.087404 } ], "Composition":{ "Ice":0.000000, "Rock":0.859877, "Metal":0.140123 }, "SemiMajorAxis":36701788.902283, "Eccentricity":0.000000, "OrbitalInclination":41.570031, "Periapsis":124.557983, "OrbitalPeriod":755303.013325, "RotationPeriod":763516.619483, "AxialTilt":-0.465541, "WasDiscovered":false, "WasMapped":false }),
        WrapWithEventType("JournalEntry", { "timestamp":"2020-08-27T20:55:33Z", "event":"Scan", "MappedValue": 123, "ScanType":"Detailed", "BodyName":"A 10", "BodyID":13, "Parents":[ {"Star":1}, {"Null":0} ], "StarSystem":"Sifeae RP-F d11-17", "SystemAddress":629388954035, "DistanceFromArrivalLS":5817.589961, "TidalLock":false, "TerraformState":"", "PlanetClass":"Icy body", "Atmosphere":"", "AtmosphereType":"None", "Volcanism":"", "MassEM":0.007883, "Radius":1628941.000000, "SurfaceGravity":1.184134, "SurfaceTemperature":107.449127, "SurfacePressure":0.000000, "Landable":true, "Materials":[ { "Name":"sulphur", "Percent":22.256582 }, { "Name":"carbon", "Percent":18.715481 }, { "Name":"iron", "Percent":16.512304 }, { "Name":"nickel", "Percent":12.489215 }, { "Name":"phosphorus", "Percent":11.981973 }, { "Name":"manganese", "Percent":6.819413 }, { "Name":"zinc", "Percent":4.487426 }, { "Name":"germanium", "Percent":3.436711 }, { "Name":"cadmium", "Percent":1.282255 }, { "Name":"niobium", "Percent":1.128528 }, { "Name":"tellurium", "Percent":0.890115 } ], "Composition":{ "Ice":0.617624, "Rock":0.256447, "Metal":0.125929 }, "SemiMajorAxis":1740140855312.347412, "Eccentricity":0.011868, "OrbitalInclination":9.222010, "Periapsis":353.753215, "OrbitalPeriod":1001487076.282501, "RotationPeriod":98751.115662, "AxialTilt":-0.519995, "WasDiscovered":false, "WasMapped":false }),
        WrapWithEventType("JournalEntry", { "timestamp":"2020-08-27T21:37:27Z", "event":"Scan", "MappedValue": 123, "ScanType":"Detailed", "BodyName":"9", "BodyID":13, "Parents":[ {"Star":0} ], "StarSystem":"Sifeae RP-F d11-2", "SystemAddress":629388954035, "DistanceFromArrivalLS":3887.502778, "TidalLock":false, "TerraformState":"", "PlanetClass":"Rocky ice body", "Atmosphere":"thick nitrogen atmosphere", "AtmosphereType":"Nitrogen", "AtmosphereComposition":[ { "Name":"Nitrogen", "Percent":99.930611 }, { "Name":"Argon", "Percent":0.068962 } ], "Volcanism":"", "MassEM":0.241041, "Radius":4597476.000000, "SurfaceGravity":4.545296, "SurfaceTemperature":150.470886, "SurfacePressure":48670292.000000, "Landable":false, "Composition":{ "Ice":0.412583, "Rock":0.393262, "Metal":0.194155 }, "SemiMajorAxis":1061343133449.554443, "Eccentricity":0.111669, "OrbitalInclination":-144.826757, "Periapsis":67.346550, "OrbitalPeriod":509246402.978897, "RotationPeriod":130196.875286, "AxialTilt":-0.337840, "WasDiscovered":false, "WasMapped":false }),
        WrapWithEventType("JournalEntry", { "timestamp":"2020-08-27T22:25:32Z", "event":"Scan", "MappedValue": 123, "ScanType":"Detailed", "BodyName":"5", "BodyID":48, "Parents":[ {"Star":0} ], "StarSystem":"Sifeae SP-F d11-19", "SystemAddress":629388954035, "DistanceFromArrivalLS":4348.969920, "TidalLock":false, "TerraformState":"", "PlanetClass":"Icy body", "Atmosphere":"thick methane rich atmosphere", "AtmosphereType":"MethaneRich", "AtmosphereComposition":[ { "Name":"Ammonia", "Percent":33.219345 }, { "Name":"Methane", "Percent":33.219345 }, { "Name":"Nitrogen", "Percent":33.219345 } ], "Volcanism":"water geysers volcanism", "MassEM":10.707685, "Radius":15074568.000000, "SurfaceGravity":18.780851, "SurfaceTemperature":485.114349, "SurfacePressure":4425951232.000000, "Landable":false, "Composition":{ "Ice":0.683452, "Rock":0.212104, "Metal":0.104443 }, "SemiMajorAxis":1302154421806.335449, "Eccentricity":0.002421, "OrbitalInclination":-1.029121, "Periapsis":53.665619, "OrbitalPeriod":795468407.869339, "RotationPeriod":74868.725071, "AxialTilt":-0.023235, "Rings":[ { "Name":"Sifeae SP-F d11-19 5 A Ring", "RingClass":"eRingClass_Icy", "MassMT":8.6698e+05, "InnerRad":2.4873e+07, "OuterRad":8.0814e+07 } ], "ReserveLevel":"PristineResources", "WasDiscovered":false, "WasMapped":false }),

        WrapWithEventType("JournalEntry", { "timestamp":"2020-08-27T22:40:03Z", "event":"Scan", "MappedValue": 3123456, "ScanType":"Detailed", "BodyName":"4", "BodyID":4, "Parents":[ {"Star":0} ], "StarSystem":"Sifeae TP-F d11-27", "SystemAddress":629388954035, "DistanceFromArrivalLS":1202.383750, "TidalLock":false, "TerraformState":"Terraformable", "PlanetClass":"Water world", "Atmosphere":"nitrogen atmosphere", "AtmosphereType":"Nitrogen", "AtmosphereComposition":[ { "Name":"Nitrogen", "Percent":97.354683 }, { "Name":"Oxygen", "Percent":2.557643 }, { "Name":"Water", "Percent":0.063727 } ], "Volcanism":"major rocky magma volcanism", "MassEM":0.800711, "Radius":5696840.500000, "SurfaceGravity":9.833697, "SurfaceTemperature":249.786743, "SurfacePressure":387579.375000, "Landable":true, "Composition":{ "Ice":0.000000, "Rock":0.674676, "Metal":0.325323 }, "SemiMajorAxis":360511553287.506104, "Eccentricity":0.000180, "OrbitalInclination":-0.070908, "Periapsis":154.857116, "OrbitalPeriod":109780913.591385, "RotationPeriod":168794.241913, "AxialTilt":-0.165132, "WasDiscovered":false, "WasMapped":false }),

        WrapWithEventType("JournalEntry", { "timestamp":"2020-08-27T22:42:20Z", "event":"Scan", "MappedValue": 123, "ScanType":"Detailed", "BodyName":"7", "BodyID":12, "Parents":[ {"Star":0} ], "StarSystem":"Sifeae QU-F d11-7", "SystemAddress":629388954035, "DistanceFromArrivalLS":5808.033260, "TidalLock":false, "TerraformState":"", "PlanetClass":"Gas giant with ammonia based life", "Atmosphere":"", "AtmosphereComposition":[ { "Name":"Hydrogen", "Percent":74.353905 }, { "Name":"Helium", "Percent":25.625011 } ], "Volcanism":"", "MassEM":355.137878, "Radius":72255304.000000, "SurfaceGravity":27.112337, "SurfaceTemperature":132.713913, "SurfacePressure":0.000000, "Landable":false, "SemiMajorAxis":1737880468368.530273, "Eccentricity":0.014049, "OrbitalInclination":-0.175683, "Periapsis":319.387555, "OrbitalPeriod":1119854152.202606, "RotationPeriod":163062.787293, "AxialTilt":-0.328957, "Rings":[ { "Name":"Sifeae QU-F d11-7 4 A Ring", "RingClass":"eRingClass_Metallic", "MassMT":1.0005e+11, "InnerRad":1.1772e+08, "OuterRad":1.3081e+08 }, { "Name":"Sifeae QU-F d11-7 4 B Ring", "RingClass":"eRingClass_Icy", "MassMT":1.343e+12, "InnerRad":1.3091e+08, "OuterRad":2.4653e+08 } ], "ReserveLevel":"PristineResources", "WasDiscovered":false, "WasMapped":false }),
        WrapWithEventType("JournalEntry", { "timestamp":"2020-08-27T22:43:17Z", "event":"Scan", "MappedValue": 123, "ScanType":"Detailed", "BodyName":"2", "BodyID":3, "Parents":[ {"Null":2}, {"Star":0} ], "StarSystem":"Sifeae QU-F d11-7", "SystemAddress":629388954035, "DistanceFromArrivalLS":4160.962580, "TidalLock":false, "TerraformState":"", "PlanetClass":"Sudarsky class II gas giant", "Atmosphere":"", "AtmosphereComposition":[ { "Name":"Hydrogen", "Percent":74.369583 }, { "Name":"Helium", "Percent":25.630409 } ], "Rings":[ { "Name":"Wregoe NT-X c28-8 A Belt", "RingClass":"eRingClass_Rocky", "MassMT":4.987e+06, "InnerRad":9.0376e+08, "OuterRad":1.9639e+09 } ], "Volcanism":"", "MassEM":454.990814, "Radius":74923384.000000, "SurfaceGravity":32.305561, "SurfaceTemperature":165.127991, "SurfacePressure":0.000000, "Landable":false, "SemiMajorAxis":48908598.423004, "Eccentricity":0.044947, "OrbitalInclination":9.301607, "Periapsis":353.801388, "OrbitalPeriod":49028207.659721, "RotationPeriod":150021.407255, "AxialTilt":0.485325, "Rings":[ { "Name":"Sifeae QU-F d11-7 2 A Ring", "RingClass":"eRingClass_Rocky", "MassMT":2.1809e+11, "InnerRad":1.2237e+08, "OuterRad":1.5135e+08 }, { "Name":"Sifeae QU-F d11-7 2 B Ring", "RingClass":"eRingClass_Rocky", "MassMT":1.3414e+12, "InnerRad":1.5145e+08, "OuterRad":2.6776e+08 } ], "ReserveLevel":"PristineResources", "WasDiscovered":false, "WasMapped":false }),
        WrapWithEventType("JournalEntry", { "timestamp":"2020-08-27T23:02:14Z", "event":"Scan", "MappedValue": 123, "ScanType":"Detailed", "BodyName":"AB 1", "BodyID":14, "Parents":[ {"Null":13}, {"Null":0} ], "StarSystem":"Sifeae SP-F d11-16", "SystemAddress":629388954035, "DistanceFromArrivalLS":4020.598838, "TidalLock":false, "TerraformState":"", "PlanetClass":"Sudarsky class III gas giant", "Atmosphere":"", "AtmosphereComposition":[ { "Name":"Hydrogen", "Percent":71.664436 }, { "Name":"Helium", "Percent":28.335575 } ], "Volcanism":"", "MassEM":2197.937988, "Radius":70825648.000000, "SurfaceGravity":174.640029, "SurfaceTemperature":597.157349, "SurfacePressure":0.000000, "Landable":false, "SemiMajorAxis":139971697.330475, "Eccentricity":0.197751, "OrbitalInclination":7.265513, "Periapsis":98.411227, "OrbitalPeriod":35178327.560425, "RotationPeriod":17075.715066, "AxialTilt":2.175150, "Rings":[ { "Name":"Sifeae SP-F d11-16 AB 1 A Ring", "RingClass":"eRingClass_MetalRich", "MassMT":2.1331e+11, "InnerRad":1.1453e+08, "OuterRad":1.4961e+08 }, { "Name":"Sifeae SP-F d11-16 AB 1 B Ring", "RingClass":"eRingClass_Rocky", "MassMT":4.2019e+12, "InnerRad":1.4971e+08, "OuterRad":4.5263e+08 } ], "ReserveLevel":"PristineResources", "WasDiscovered":false, "WasMapped":false }),

        WrapWithEventType("JournalEntry", { "timestamp":"2020-08-27T20:58:37Z", "event":"Scan", "MappedValue": 1123456, "ScanType":"Detailed", "BodyName":"6", "BodyID":6, "Parents":[ {"Star":0} ], "StarSystem":"Sifeae RP-F d11-3", "SystemAddress":114143857123, "DistanceFromArrivalLS":3141.918552, "TidalLock":false, "TerraformState":"", "PlanetClass":"Ammonia world", "Atmosphere":"", "AtmosphereType":"AmmoniaOxygen", "AtmosphereComposition":[ { "Name":"CarbonDioxide", "Percent":84.502144 }, { "Name":"Nitrogen", "Percent":11.775880 }, { "Name":"Oxygen", "Percent":2.830044 } ], "Volcanism":"", "MassEM":0.296209, "Radius":4198024.500000, "SurfaceGravity":6.699115, "SurfaceTemperature":234.536438, "SurfacePressure":294524.968750, "Landable":false, "Composition":{ "Ice":0.000000, "Rock":0.673636, "Metal":0.326364 }, "SemiMajorAxis":942827576398.849487, "Eccentricity":0.001102, "OrbitalInclination":9.992684, "Periapsis":260.638759, "OrbitalPeriod":437092494.964600, "RotationPeriod":39129.182124, "AxialTilt":-0.224488, "WasDiscovered":false, "WasMapped":false }),

        WrapWithEventType("JournalEntry", { "timestamp":"2020-08-27T22:25:20Z", "event":"Scan", "MappedValue": 1, "ScanType":"AutoScan", "BodyName":"B 4", "BodyClass": "Belt Cluster", "BodyID":12, "Parents":[ {"Ring":8}, {"Star":0} ], "StarSystem":"Sifeae SP-F d11-19", "SystemAddress":663916448227, "DistanceFromArrivalLS":197.613961, "WasDiscovered":false, "WasMapped":false }),
        WrapWithEventType("JournalEntry", { "timestamp":"2020-07-28T23:34:03Z", "event":"Scan", "MappedValue": 3523456, "ScanType":"Detailed", "BodyName":"C 5", "BodyID":12, "Parents":[ {"Null":11}, {"Star":4}, {"Null":0} ], "StarSystem":"Pro Eurl RI-T d3-24", "SystemAddress":835463448995, "DistanceFromArrivalLS":29917.101719, "TidalLock":false, "TerraformState":"", "PlanetClass":"Earthlike body", "Atmosphere":"", "AtmosphereType":"EarthLike", "AtmosphereComposition":[ { "Name":"Nitrogen", "Percent":95.066788 }, { "Name":"Oxygen", "Percent":4.298672 }, { "Name":"Water", "Percent":0.609198 } ], "Volcanism":"major rocky magma volcanism", "MassEM":0.881002, "Radius":5857355.000000, "SurfaceGravity":10.234893, "SurfaceTemperature":303.686554, "SurfacePressure":386198.937500, "Landable":false, "Composition":{ "Ice":0.000000, "Rock":0.671427, "Metal":0.328573 }, "SemiMajorAxis":924326723.814011, "Eccentricity":0.138475, "OrbitalInclination":-8.776263, "Periapsis":254.857225, "OrbitalPeriod":23820475.339890, "RotationPeriod":98249.471153, "AxialTilt":-0.254686, "WasDiscovered":true, "WasMapped":false }),

        // badly spelt metallic in ring
        WrapWithEventType("JournalEntry", { "timestamp":"2020-10-13T21:34:30Z", "event":"Scan", "MappedValue": 1, "ScanType":"Detailed", "BodyName":"Sleguae AN-M c23-4 A 2", "BodyID":22, "Parents":[ {"Null":21}, {"Star":1}, {"Null":0} ], "StarSystem":"Sleguae AN-M c23-4", "SystemAddress":1178599166154, "DistanceFromArrivalLS":1614.812718, "TidalLock":false, "TerraformState":"", "PlanetClass":"Sudarsky class III gas giant", "Atmosphere":"", "AtmosphereComposition":[ { "Name":"Hydrogen", "Percent":73.104919 }, { "Name":"Helium", "Percent":26.895090 } ], "Volcanism":"", "MassEM":1664.134521, "Radius":74779944.000000, "SurfaceGravity":118.611691, "SurfaceTemperature":393.255524, "SurfacePressure":0.000000, "Landable":false, "SemiMajorAxis":794658607.244492, "Eccentricity":0.033201, "OrbitalInclination":-7.229987, "Periapsis":249.203960, "OrbitalPeriod":8435987.770557, "RotationPeriod":212952.984035, "AxialTilt":-0.975308, "Rings":[ { "Name":"Sleguae AN-M c23-4 A 2 A Ring", "RingClass":"eRingClass_Metalic", "MassMT":1.525e+11, "InnerRad":1.1955e+08, "OuterRad":1.3837e+08 }, { "Name":"Sleguae AN-M c23-4 A 2 B Ring", "RingClass":"eRingClass_MetalRich", "MassMT":4.7453e+12, "InnerRad":1.3847e+08, "OuterRad":4.1255e+08 } ], "ReserveLevel":"PristineResources", "WasDiscovered":false, "WasMapped":false }),
    ];



    tests["galaxy-map-doesnt-wipe-list"] = [
        // Simulate a normal startup
        WrapWithEventType("JournalEntry", {"timestamp":"2020-08-08T23:07:06Z", "event":"Location", "Docked":false, "StarSystem":"Sifeae EH-C c13-3", "SystemAddress":913385362290, 'StarPos': [2899.96875, 206.34375, 801.6875], "SystemAllegiance":"", "SystemEconomy":"$economy_None;", "SystemEconomy_Localised":"None", "SystemSecondEconomy":"$economy_None;", "SystemSecondEconomy_Localised":"None", "SystemGovernment":"$government_None;", "SystemGovernment_Localised":"None", "SystemSecurity":"$GAlAXY_MAP_INFO_state_anarchy;", "SystemSecurity_Localised":"Anarchy", "Population":0, "Body":"V447 Lacertae", "BodyID":0, "BodyType":"Star" }),
        // Simulate a few scans
        WrapWithEventType("JournalEntry", { "timestamp":"2020-08-27T22:25:20Z", "event":"Scan", "MappedValue": 1, "ScanType":"AutoScan", "BodyName":"B 4", "BodyClass": "Belt Cluster", "BodyID":12, "Parents":[ {"Ring":8}, {"Star":0} ], "StarSystem":"Sifeae SP-F d11-19", "SystemAddress":913385362290, "DistanceFromArrivalLS":197.613961, "WasDiscovered":false, "WasMapped":false }),
        // Plot a nav route
        WrapWithEventType("NewRoute"),
        WrapWithEventType("JournalEntry", {"timestamp":"2020-08-08T23:07:12Z", "event":"FSDTarget", "Name":'Pro Eurl YJ-Q d5-18', "SystemAddress":629388954035, "StarClass":"F", "RemainingJumpsInRoute":1 }),
        WrapWithEventType("System-NavRoute", {'StarSystem': 'Sifeae EH-C c13-3', 'SystemAddress': 913385362290, 'StarPos': [2899.96875, 206.34375, 801.6875], 'StarClass': 'K', 'id': 55216390, 'id64': 913385362290, 'name': 'Sifeae EH-C c13-3', 'url': 'https://www.edsm.net/en/system/bodies/id/55216390/name/Sifeae+EH-C+c13-3', 'estimatedValue': 112130, 'estimatedValueMapped': 368117, 'valuableBodies': [{'bodyId': 226907740, 'bodyName': 'Sifeae EH-C c13-3 A 1', 'distance': 1250, 'valueMax': 365696},{'bodyId': 226907741, 'bodyName': 'Sifeae EH-C c13-3 A 2', 'distance': 120, 'valueMax': 36596}], 'charted': true}),
        WrapWithEventType("System-NavRoute", {'StarSystem': 'Pro Eurl YJ-Q d5-18', 'SystemAddress': 629388954035, 'StarPos': [2035.6875, 381.59375, 739.6875], 'StarClass': 'F', 'id': 55108083, 'id64': 629388954035, 'name': 'Pro Eurl YJ-Q d5-18', 'url': 'https://www.edsm.net/en/system/bodies/id/55108083/name/Pro+Eurl+YJ-Q+d5-18', 'estimatedValue': 39863, 'estimatedValueMapped': 127197, 'valuableBodies': [{'bodyId': 226907740, 'bodyName': 'Pro Eurl YJ-Q d5-18 A 1', 'distance': 1250, 'valueMax': 365696},{'bodyId': 226907741, 'bodyName': 'Pro Eurl YJ-Q d5-18 A 2', 'distance': 120, 'valueMax': 36596}], 'charted': true}),
    ];

    tests["detailed-scan-drops-down-list"] = [
        // In a system.
        WrapWithEventType("JournalEntry", { "timestamp":"2020-09-04T22:19:02Z", "event":"FSDJump", "StarSystem":"Sifeae GF-R d4-115", "SystemAddress":3962585483691, "StarPos":[3517.00000,52.18750,680.09375], "SystemAllegiance":"", "SystemEconomy":"$economy_None;", "SystemEconomy_Localised":"None", "SystemSecondEconomy":"$economy_None;", "SystemSecondEconomy_Localised":"None", "SystemGovernment":"$government_None;", "SystemGovernment_Localised":"None", "SystemSecurity":"$GAlAXY_MAP_INFO_state_anarchy;", "SystemSecurity_Localised":"Anarchy", "Population":0, "Body":"Sifeae GF-R d4-115 A", "BodyID":1, "BodyType":"Star", "JumpDist":48.958, "FuelUsed":4.264605, "FuelLevel":27.735395 }),
        // Some scans
        WrapWithEventType("JournalEntry", { "timestamp":"2020-09-04T22:20:07Z", "event":"Scan", "MappedValue": 1000000, "ScanType":"Detailed", "BodyName":"Sifeae GF-R d4-115 A 1", "BodyID":5, "Parents":[ {"Star":1}, {"Null":0} ], "StarSystem":"Sifeae GF-R d4-115", "SystemAddress":3962585483691, "DistanceFromArrivalLS":1092.825009, "TidalLock":false, "TerraformState":"Terraformable", "PlanetClass":"High metal content body", "Atmosphere":"hot thick carbon dioxide atmosphere", "AtmosphereType":"CarbonDioxide", "AtmosphereComposition":[ { "Name":"CarbonDioxide", "Percent":95.848160 }, { "Name":"Nitrogen", "Percent":3.193112 }, { "Name":"SulphurDioxide", "Percent":0.958482 } ], "Volcanism":"major silicate vapour geysers volcanism", "MassEM":3.094303, "Radius":8427145.000000, "SurfaceGravity":17.366460, "SurfaceTemperature":956.388855, "SurfacePressure":44952200.000000, "Landable":false, "Composition":{ "Ice":0.000000, "Rock":0.669245, "Metal":0.330755 }, "SemiMajorAxis":326312464475.631714, "Eccentricity":0.004013, "OrbitalInclination":-0.188240, "Periapsis":187.106421, "OrbitalPeriod":79173184.037209, "RotationPeriod":168728.632391, "AxialTilt":0.334432, "WasDiscovered":true, "WasMapped":false }),
        WrapWithEventType("JournalEntry", { "timestamp":"2020-09-04T22:20:16Z", "event":"Scan", "MappedValue": 1, "ScanType":"Detailed", "BodyName":"Sifeae GF-R d4-115 A 7", "BodyID":14, "Parents":[ {"Null":12}, {"Star":1}, {"Null":0} ], "StarSystem":"Sifeae GF-R d4-115", "SystemAddress":3962585483691, "DistanceFromArrivalLS":3772.247374, "TidalLock":false, "TerraformState":"", "PlanetClass":"High metal content body", "Atmosphere":"thick methane rich atmosphere", "AtmosphereType":"MethaneRich", "AtmosphereComposition":[ { "Name":"Ammonia", "Percent":32.688076 }, { "Name":"Methane", "Percent":32.688076 }, { "Name":"Nitrogen", "Percent":32.688076 } ], "Volcanism":"minor silicate vapour geysers volcanism", "MassEM":1.378427, "Radius":6685303.500000, "SurfaceGravity":12.292803, "SurfaceTemperature":416.637970, "SurfacePressure":2200182.250000, "Landable":false, "Composition":{ "Ice":0.000000, "Rock":0.669251, "Metal":0.330749 }, "SemiMajorAxis":2948085606.098175, "Eccentricity":0.080099, "OrbitalInclination":-2.887471, "Periapsis":319.350979, "OrbitalPeriod":48950456.380844, "RotationPeriod":81034.086164, "AxialTilt":-0.196478, "WasDiscovered":true, "WasMapped":false }),
        WrapWithEventType("JournalEntry", { "timestamp":"2020-09-04T22:20:21Z", "event":"Scan", "MappedValue": 1, "ScanType":"Detailed", "BodyName":"Sifeae GF-R d4-115 A 6", "BodyID":13, "Parents":[ {"Null":12}, {"Star":1}, {"Null":0} ], "StarSystem":"Sifeae GF-R d4-115", "SystemAddress":3962585483691, "DistanceFromArrivalLS":3778.986417, "TidalLock":false, "TerraformState":"", "PlanetClass":"High metal content body", "Atmosphere":"thick methane rich atmosphere", "AtmosphereType":"MethaneRich", "AtmosphereComposition":[ { "Name":"Ammonia", "Percent":32.486629 }, { "Name":"Methane", "Percent":32.486629 }, { "Name":"Nitrogen", "Percent":32.486629 } ], "Volcanism":"metallic magma volcanism", "MassEM":2.528601, "Radius":7946843.500000, "SurfaceGravity":15.958809, "SurfaceTemperature":448.047302, "SurfacePressure":3692897.000000, "Landable":false, "Composition":{ "Ice":0.000000, "Rock":0.662390, "Metal":0.337610 }, "SemiMajorAxis":1607102572.917938, "Eccentricity":0.080099, "OrbitalInclination":-2.887471, "Periapsis":139.350985, "OrbitalPeriod":48950456.380844, "RotationPeriod":138931.744666, "AxialTilt":-0.758665, "WasDiscovered":true, "WasMapped":false }),
        // detailed surface map
        WrapWithEventType("JournalEntry", { "timestamp":"2020-09-04T22:23:40Z", "event":"SAAScanComplete", "BodyName":"Sifeae GF-R d4-115 A 1", "SystemAddress":3962585483691, "BodyID":5, "ProbesUsed":6, "EfficiencyTarget":7 }),
        WrapWithEventType("JournalEntry", { "timestamp":"2020-09-04T22:23:40Z", "event":"Scan", "MappedValue": 1000000, "ScanType":"Detailed", "BodyName":"Sifeae GF-R d4-115 A 1", "BodyID":5, "Parents":[ {"Star":1}, {"Null":0} ], "StarSystem":"Sifeae GF-R d4-115", "SystemAddress":3962585483691, "DistanceFromArrivalLS":1092.825012, "TidalLock":false, "TerraformState":"Terraformable", "PlanetClass":"High metal content body", "Atmosphere":"hot thick carbon dioxide atmosphere", "AtmosphereType":"CarbonDioxide", "AtmosphereComposition":[ { "Name":"CarbonDioxide", "Percent":95.848160 }, { "Name":"Nitrogen", "Percent":3.193112 }, { "Name":"SulphurDioxide", "Percent":0.958482 } ], "Volcanism":"major silicate vapour geysers volcanism", "MassEM":3.094303, "Radius":8427145.000000, "SurfaceGravity":17.366460, "SurfaceTemperature":956.388855, "SurfacePressure":44952200.000000, "Landable":false, "Composition":{ "Ice":0.000000, "Rock":0.669245, "Metal":0.330755 }, "SemiMajorAxis":326312464475.631714, "Eccentricity":0.004013, "OrbitalInclination":-0.188240, "Periapsis":187.106421, "OrbitalPeriod":79173184.037209, "RotationPeriod":168728.632391, "AxialTilt":0.334432, "WasDiscovered":true, "WasMapped":false }),
    ];

    function runTest(testId){
        let data;
        for (data of tests[testId])
        {
            postData(data);
        }
    }


    function addTest(testId) {
        let newButton = document.createElement('button')
        newButton.id = testId;
        newButton.innerText = testId;
        newButton.onclick = function() { runTest(testId); }

        document.body.appendChild(newButton);
        document.body.appendChild(document.createElement("br"))
    }


    function versionCheckReport(versionCheck) {
        console.log(versionCheck);

        if (versionCheck['new_release_detected']) {
            let versionInfoElement = document.getElementById('version-link-wrapper')
            let link = document.createElement('a')
            link.href = versionCheck['url']
            link.text = versionCheck['latest_version']
            link.target = '_blank'
            link.classList.add('alert-link')
            versionInfoElement.innerHTML = link.outerHTML

            let alertDiv = document.getElementById('new-version-alert-wrapper')
            alertDiv.hidden = false;
        }
    }

    function populateTests() {
        let testId;
        for (testId of Object.keys(tests))
        {
            addTest(testId);
        }

        enableBackendConnections = false;
    }

    document.addEventListener('DOMContentLoaded', function() {

        console.log('Launching backend connections')

        // Uncomment to debug without needing the backend
        //populateTests();

        if (enableBackendConnections) {
            let socket = io()
            socket.on('log', postData)
            socket.on('version', versionCheckReport)
        }
        else
        {
            console.log('Backend connections are disabled')
        }

        let url = 'http://'+window.location.hostname+':5001/GUI-is-still-open';
        fetch(url, { mode: 'no-cors'});
        setInterval(function(){ fetch(url, { mode: 'no-cors'});}, 5000);
    });

})()

