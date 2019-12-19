async function readData(filename) {
    let json = await readJSON(filename);
    return toCytoscape(json)
}

function toCytoscape(json) {
    let res = [];
    for (let i in json) {
        res.push(transformJsonEntity(json[i]))
    }
    return res
}

function transformJsonEntity(json) {
    let res = {};

    for (i in json) {
        switch(i) {
            case 'events':
                res.events = transformJsonEvents(json.events);
                break;
            case 'df':
                res.df = transformJsonDFs(json.df);
                break;
            case 'common':
                res.common = transformJsonCommon(json.common);
                break;
            case 'EC':
                res.ec = transformJsonECs(json.EC);
        }
    }
    return res;
}

function transformJsonCommon(json) {
    let obj = {
        data: {
            id: json.identity,
            DataType: 'Common',
            ...json.properties
        }
    };

    return [obj]
}

function transformJsonECs(json) {
    let res = [];
    for (let i in json) {
        let obj = {
            data: {
                DataType: 'EC',
                id: 'e-'+json[i].identity,
                source: json[i].start,
                target: json[i].end,
                ...json[i].properties
            }
        };

        res.push(obj);
    }
    return res
}

function transformJsonEvents(json) {
    let res = [];
    for (let i in json) {
        let obj = {
            data: {
                id: json[i].identity,
                DataType: 'Event',
                ...json[i].properties
            }
        };

        res.push(obj)
    }
    return res
}

function transformJsonDFs(json) {
    let res = [];
    for (let i in json) {
        let obj = {
            data: {
                DataType: "DF",
                id: 'e-'+json[i].identity,
                source: json[i].start,
                target: json[i].end,
                ...json[i].properties
            }
        };

        res.push(obj);
    }
    return res
}

function finalizeJson(json) {
    let res = [];
    for(let i in json) {
        for(let key in json[i]) {
            res = joinArrays(res, json[i][key]);
        }
    }
    return res;
}

function splitElements(elements) {
    let res = {};

    res.DF = elements.filter((e)=> {
        return e.data.DataType === "DF"
    });

    res.Event = elements.filter((e)=> {
        return e.data.DataType === "Event"
    });

    res.EC = elements.filter((e)=> {
        return e.data.DataType === "EC"
    });

    res.Common = elements.filter((e)=> {
        return e.data.DataType === "Common"
    });

    return res;
}

// Calculates the global DF structure and returns all elements that need to be added to graph in order to show it.
function calculateGlobalDF(splitElements) {
    console.log(splitElements);
    let sortedEvents = splitElements['Event'].sort(eventSorter(splitElements['Event'], splitElements['DF']));
    let getEvent = eventGetterFactory(splitElements['Event']);
    let getCommon = commonGetterFactory(splitElements['Common'], splitElements['EC']);
    let getEventsFromCommon = eventsFromCommonGetterFactory(splitElements['EC'], getEvent);
    let eventsSameCommon= eventsSameCommonFactory(getCommon, getEventsFromCommon);
    let getDF = dfGetterFactory(splitElements['DF']);
    let dfSourceSameCommon = dfSourceSameCommonFactory(getCommon, getDF, getEventsFromCommon);
    let dfTargetSameCommon = dfTargetSameCommonFactory(getCommon, getDF, getEventsFromCommon);
    let res = [];

    for (let i = 0; i < sortedEvents.length - 1; i++) {
        let source = sortedEvents[i];
        let target = sortedEvents[i+1];
        if (source.data.id === 1541) {
            console.log(target)
        }
        let df = getDF(source.data.id, target.data.id);

        // We only add a DF edge if the following hold:
        // There is no existing DF edge with the same source and target
        // The source and target are not connected to the same common node
        // There is no other node connected to the same common node as the target node to which the source node already has a DF edge
        // There is no other node connected to the same common node as the source node from which the target node already has a DF edge
        if (df == null &&
            !eventsSameCommon(source.data.id, target.data.id) &&
            !dfSourceSameCommon(source.data.id, target.data.id) &&
            !dfTargetSameCommon(source.data.id, target.data.id)
        ) {
            let sourceCommon = getCommon(source.data.id);
            let targetCommon = getCommon(target.data.id);

            // If the source does not have a common node yet, create one for it
            if (!sourceCommon) {
                sourceCommon = createCommon(source.data.id, 'c');
                res.push(sourceCommon);
                res.push(createEC(sourceCommon.data.id, source.data.id, sourceCommon.data.id, 'ecc'));
            }

            // If the target does not have a common node yet, create one for it
            if (!targetCommon) {
                targetCommon = createCommon(target.data.id, 'c');
                res.push(targetCommon);
                res.push(createEC(targetCommon.data.id, target.data.id, targetCommon.data.id, 'ecc'));
            }

            // Attach a new event node to the (possibly new) source common node
            let realSource = createEvent(source.data.id, source.data.Activity, source.data.Start, source.data.End, 'v');
            res.push(realSource);
            res.push(createEC(sourceCommon.data.id, realSource.data.id, sourceCommon.data.id, 'ec'));

            // Attach a new event node to the (possibly new) target common node
            let realTarget = createEvent(target.data.id, target.data.Activity, target.data.Start, target.data.End, 'v');
            res.push(realTarget);
            res.push(createEC(targetCommon.data.id, realTarget.data.id, targetCommon.data.id, 'ec'));

            // Connect the two new event nodes with a DF edge
            res.push(createDF(source.data.id, realSource.data.id, realTarget.data.id, 'vdf'));
        }
    }

    return res
}

function eventGetterFactory(events) {
    return (eventID) => {
        return events.find((e) => {return e.data.id === eventID; })
    }
}

function commonGetterFactory(common, ec) {
    return (eventID) => {
        let edge = ec.find((e) => { return e.data.source === eventID; });
        if (edge != null) {
            return common.find((e) => { return e.data.id === edge.data.target});
        }
        return undefined;
    }
}

function eventsSameCommonFactory(commonGetter, eventsFromCommonGetter) {
    return (a, b) => {
        let common = commonGetter(a);
        if (common) {
            let commonEvents = eventsFromCommonGetter(common.data.id);
            return !!commonEvents.find((e) => { return e.data.id === b });
        }
        return false
    }
}

function dfSourceSameCommonFactory(commonGetter, dfGetter, eventsFromCommonGetter) {
    return (a, b) => {
        let common = commonGetter(a);
        if (common) {
            let commonEvents = eventsFromCommonGetter(common.data.id);
            for (let i in commonEvents) {
                let df = dfGetter(commonEvents[i].data.id, b);
                if (df)
                    return true
            }
        }
        return false
    }
}

function dfTargetSameCommonFactory(commonGetter, dfGetter, eventsFromCommonGetter) {
    return (a, b) => {
        let common = commonGetter(b);
        if (common) {
            let commonEvents = eventsFromCommonGetter(common.data.id);
            for (let i in commonEvents) {
                let df = dfGetter(a, commonEvents[i].data.id);
                if (df)
                    return true
            }
        }
        return false
    }
}

function dfGetterFactory(df) {
    return (sourceID, targetID) => {
        return df.find((e) => {
            let source = e.data.source;
            let target = e.data.target;
            return source === sourceID && target === targetID })
    }

}

function eventsFromCommonGetterFactory(ec, eventGetter) {
    return (commonID) => {
        let ecs = ec.filter((e) => { return e.data.target === commonID });
        return ecs.map((e) => {return eventGetter(e.data.source) });
    }
}

function eventSorter(events, dfs) {
    return (a, b) => {
        let aTime = a.data['Start'];
        let bTime = b.data['Start'];
        let aId = a.data['id'];
        let bId = b.data['id'];

        if (aTime > bTime) return 1;
        if (bTime > aTime) return -1;

        let aToB = dfs.find( ele => ele.data.source === aId && ele.data.target === bId);
        let bToA = dfs.find( ele => ele.data.source === bId && ele.data.target === aId);

        if (aToB) {
            return -1;
        }

        if (bToA) {
            return 1;
        }

        return 0;
    }
}