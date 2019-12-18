document.addEventListener('DOMContentLoaded', function (){
    render();
});

async function render() {
    let data = await readData('records.json');
    let common_data = await readData('records_common.json');
    let elements = finalizeJson(data);
    elements = joinArrays(elements, finalizeJson(common_data));
    console.log(elements);

    cy = cytoscape({
        container: document.getElementById('viz'),
        elements: elements,
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
                selector: 'edge[EntityType = "both"]',
                style: {
                    'line-color': '#602495',
                    'target-arrow-color': '#602495',
                }
            },
            {
                selector: 'edge[EntityType = "neither"]',
                style: {
                    'line-style': 'dashed',
                    'line-color': '#602495',
                    'target-arrow-color': '#602495',
                }
            },
            {
                selector: 'node[DataType ="Event"]',
                style: {
                    'label': 'data(Activity)'
                }
            },
            {
                selector: 'node[EntityType="Incident"]',
                style: {
                    'background-color': '#F47C7C',
                }
            },
            {
                selector: 'edge[EntityType = "Incident"]',
                style: {
                    'line-color': '#F47C7C',
                    'target-arrow-color': '#F47C7C',
                }
            },
            {
                selector: 'edge[EntityType = "Common"]',
                style: {
                    'line-color': '#f4dee2',
                    'target-arrow-color': '#f4dee2',
                }
            },
            {
                selector: 'node[EntityType="Configuration_Item"]',
                style: {
                    'background-color': '#80A1D7',
                }
            },
            {
                selector: 'edge[EntityType = "Configuration_Item"]',
                style: {
                    'line-color': '#80A1D7',
                    'target-arrow-color': '#80A1D7',
                }
            },
            {
                selector: 'node[EntityType="both"]',
                style: {
                    'background-color': '#602495',
                }
            }
        ],
        layout: {
            name: 'cola',
            rankDir: 'TB',
            nodeSep: 300,
            rankSep: 200,
            //maxSimulationTime: '6000',
            infinite: true,
            fit: false
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
                EntityType: 'Common',
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

function renameProperty(obj, oldName, newName) {
    if (obj.hasOwnProperty(oldName)) {
        obj[newName] = obj[oldName];
        delete obj[oldName];
    }
    return obj;
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
