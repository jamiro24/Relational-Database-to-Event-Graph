document.addEventListener('DOMContentLoaded', function (){
    render();
});

async function render() {
    let incident_events = await readData('incident_events.json', 'event', 'incident');
    let ci_events = await readData('configuration_item_events.json', 'event', 'configuration_item');
    let incident_df = await readData('incident_df.json', 'df');
    let ci_df = await readData('configuration_item_df.json', 'df');

    let events = joinArrays(incident_events, ci_events);
    let dfs = joinArrays(incident_df, ci_df);

    events = events.sort(eventSorter(events, dfs));

    // set 'both' nodes
    for (let i=0; i < events.length; i++) {
        let event = events[i].data;
        if (incident_events.find(e => e.data.id === event.id) && ci_events.find(e => e.data.id === event.id)) {
            event.group = 'both';
        }
    }

    // delete duplicate dfs edge
    for (let i=0; i < dfs.length; i++) {
        if (dfs[i].data.source === 553) {
            dfs.splice(i, 1);
            break;
        }
    }

    // set/add edges that form the DF graph for all events
    for (let i=0; i < events.length - 1; i++) {
        let targetId = events[i].data.id;
        let sourceId = events[i + 1].data.id;

        if (sourceId !== targetId) {

            let existing = dfs.find(ele => ele.data.source === sourceId && ele.data.target === targetId);

            if (existing) {
                let is_incident_df = incident_df.find(ele => ele.data.source === sourceId && ele.data.target === targetId);
                let is_ci_df = ci_df.find(ele => ele.data.source === sourceId && ele.data.target === targetId);

                if (is_incident_df && is_ci_df) {
                    existing.data.group = 'both';
                }

            } else {
                console.log("what");
                dfs.push(
                    {
                        data: {
                            source: sourceId,
                            target: targetId,
                            type: 'df',
                            group: 'neither'
                        }
                    }
                )
            }
        }
    }

    // color entity exclusive edges
    for (let i=0; i < dfs.length; i++) {
        let element = dfs[i].data;

        if (element.group === "") {
            if (incident_events.find(e => e.data.id === element.source) && incident_events.find(e => e.data.id === element.target)) {
                group = "incident"
            }
            if (ci_events.find(e => e.data.id === element.source) && ci_events.find(e => e.data.id === element.target)) {
                group = "configuration_item"
            }
            element.group = group;
        }
    }

    let eles = joinArrays(events, dfs);

    let cy = cytoscape({
        container: document.getElementById('viz'),
        elements: eles,
        style: [
            {
                selector: 'node',
                style: {
                    'text-valign': 'center',
                    'text-outline-width': '1px',
                    'text-outline-color': '#FFFFFF',
                }
            },
            {
                selector: 'edge',
                style: {
                    'width': 5,
                    'curve-style': 'bezier',
                    'target-arrow-shape': 'triangle',
                    'line-color': '#88ef41',
                    'target-arrow-color': '#88ef41',
                }
            },
            {
                selector: 'edge[group = "both"]',
                style: {
                    'line-color': '#602495',
                    'target-arrow-color': '#602495',
                }
            },
            {
                selector: 'edge[group = "neither"]',
                style: {
                    'line-style': 'dashed',
                    'line-color': '#602495',
                    'target-arrow-color': '#602495',
                }
            },
            {
                selector: 'node[type ="event"]',
                style: {
                    'label': 'data(activity)'
                }
            },
            {
                selector: 'node[group="incident"]',
                style: {
                    'background-color': '#F47C7C',
                }
            },
            {
                selector: 'edge[group = "incident"]',
                style: {
                    'line-color': '#F47C7C',
                    'target-arrow-color': '#F47C7C',
                }
            },
            {
                selector: 'node[group="configuration_item"]',
                style: {
                    'background-color': '#80A1D7',
                }
            },
            {
                selector: 'edge[group = "configuration_item"]',
                style: {
                    'line-color': '#80A1D7',
                    'target-arrow-color': '#80A1D7',
                }
            },
            {
                selector: 'node[group="both"]',
                style: {
                    'background-color': '#602495',
                }
            }
        ],
        layout: {

            name: 'cola',
            maxSimulationTime: '6000'
        }
    });
}

function joinArrays(...array) {
    let result = [];
    for (let e in array) {
        result = result.concat(array[e])
    }
    return result;
}

async function readData(filename, type="", group ="") {
    let json = await readJSON(filename);
    return toCytoscape(json, type, group)
}

function toCytoscape(array, type="", group="") {
    return array.map(function(e) {
        let transformed = {
            data: e
        };
        transformed.data.type = type;
        transformed.data.group = group;
        return transformed
    })
}

async function readJSON(filename) {
    try {
        const response = await fetch('/data/' + filename);
        return await response.json();
    } catch (error) {
        console.error(error)
    }
}

function eventSorter(events, dfs) {
    return (a, b) => {
        let aTime = a.data.time;
        let bTime = b.data.time;
        let aId = a.data.id;
        let bId = b.data.id;

        if (aTime > bTime) return -1;
        if (bTime > aTime) return 1;

        let aToB = dfs.find( ele => ele.data.source === aId && ele.data.target === bId);
        let bToA = dfs.find( ele => ele.data.source === bId && ele.data.target === aId);

        if (aToB) {
            return 1;
        }

        if (bToA) {
            return -1;
        }

        return 0;
    }
}
