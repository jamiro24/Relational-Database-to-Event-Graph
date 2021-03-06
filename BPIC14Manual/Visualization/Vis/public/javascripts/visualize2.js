document.addEventListener('DOMContentLoaded', function (){
    render();
});

async function render() {
    let data = await readData('records.json');
    let elements = finalizeJson(data);
    let splitEles = splitElements(elements);
    elements = joinArrays(elements, calculateGlobalDF(splitEles));
    removeEmptyCommons(elements);
    let cy = cytoscape({
        container: document.getElementById('viz'),
        elements: elements,
        style: await readJSON('cytoscape_style.json'),
        layout: {
            name: 'cola',
            fit: false,
            maxSimulationTime: 60000,
        },
        wheelSensitivity: 0.3
    });
    cy.elements().qtip({
        content: function(){return dataToDiv(this.data()) },
        position: {
            my: 'top center',
            at: 'bottom center'
        },
        style: {
            classes: 'qtip-bootstrap',
            tip: {
                width: 15,
                height: 8
            }
        }
    });

    function dataToDiv(data) {
        let res = '';

        for (let key in data) {
            if (data.hasOwnProperty(key)) {
                res += "<div><b>" + key + ":</b> " + data[key] + "</div>"
            }
        }
        return res
    }
}
