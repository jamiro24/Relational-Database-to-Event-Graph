document.addEventListener('DOMContentLoaded', function (){
    render();
});

async function render() {
    let data = await readData('records.json');
    let common_data = await readData('records_common.json');
    let common_data2 = await readData('records_common2.json');

    let elements = joinArrays(finalizeJson(data), finalizeJson(common_data), finalizeJson(common_data2));
    let splitEles = splitElements(elements);
    elements = joinArrays(elements, calculateGlobalDF(splitEles));

    cy = cytoscape({
        container: document.getElementById('viz'),
        elements: elements,
        style: await readJSON('cytoscape_style.json'),
        layout: {
            name: 'cola',
            infinite: true,
            fit: false,
            boundingBox: undefined
        }
    });
}
