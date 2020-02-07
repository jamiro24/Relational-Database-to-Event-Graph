async function readJSON(filename) {
    try {
        const response = await fetch('/data/' + filename);
        return await response.json();
    } catch (error) {
        console.error(error)
    }
}

function renameProperty(obj, oldName, newName) {
    if (obj.hasOwnProperty(oldName)) {
        obj[newName] = obj[oldName];
        delete obj[oldName];
    }
    return obj;
}

function joinArrays(...array) {
    let result = [];
    for (let e in array) {
        result = result.concat(array[e])
    }
    return result;
}