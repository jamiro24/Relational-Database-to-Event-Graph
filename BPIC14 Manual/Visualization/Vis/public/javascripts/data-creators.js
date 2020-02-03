function createCommon(id, mod= '') {
    if (mod !== '')
        mod = mod + '-';
    return {
        data: {
            id: mod + id,
            DataType: 'Common'
        }
    };
}

function createEC(id, sourceId, targetId, mod= '') {
    if (mod !== '')
        mod = mod + '-';
    return {
        data: {
            id: mod + id,
            source: sourceId,
            target: targetId,
            DataType: 'EC',
        }
    }
}

function createEvent(id, activity, start, end, mod = '', type = 'Mixed') {
    if (mod !== '')
        mod = mod + '-';
    return {
        data: {
            id: mod + id,
            Activity: activity,
            DataType: 'Event',
            EntityType: type,
            Start: start,
            End: end,
        }
    }
}

function createDF(id, sourceId, targetId, mod = '', type = 'Mixed') {
    if (mod !== '')
        mod = mod + '-';

    return {
        data: {
            id: mod + id,
            source: sourceId,
            target: targetId,
            DataType: 'Event',
            EntityType: type
        }
    }
}