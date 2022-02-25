function shorten_time(epoch_time){
    time = String(new Date(epoch_time*1000)).split(' ').slice(0,5).join(" ")
    return time
}

function fill_basic_table(table_id, datasets, fields){
    table = document.getElementById(table_id)
    for (var row = 0; row < datasets.length; row++){
        const row_obj = datasets[row];
        const new_row = document.createElement('tr');
        new_row.className = 'table';
        for (var field_num = 0; field_num < fields.length; field_num++){
            var field = fields[field_num]
            if (field.includes('time')) {
                data = shorten_time(row_obj[field])
            }else{
                data = row_obj[field]
            }
            new_td = document.createElement('td');
            new_td.innerHTML = data;
            new_row.appendChild(new_td);
        }

        table.appendChild(new_row)
        console.log(table)
    }
    return
}


function populate_main_table(results){
    table = document.getElementById('missions_table_body');
    for (var row = 0; row < results.length; row++){
        const row_obj = results[row];
        const new_row = document.createElement('tr');
        new_row.className = 'table';
        new_row.setAttribute('data-mission-id', row_obj['missionid']);
        new_row.setAttribute('onclick', "populate_mission_table(this.getAttribute('data-mission-id'))")
        fields = ['missionid', 'name','time_init', 'time_final', 'duration','victims','notes'];
        for (var field_num = 0; field_num < fields.length; field_num++){
            var field = fields[field_num]
            if (field == 'time_init' || field == 'time_final') {
                data = shorten_time(row_obj[field])
            }else{
                data = row_obj[field]
            }
            new_td = document.createElement('td');
            new_td.innerHTML = data;
            new_row.appendChild(new_td);
        }
        table.appendChild(new_row)
    }
    return
}
function populate_specific_mission(details){
    const breakdown = details['breakdown'][0];
    const sensors = details['sensor_data'];
    const movement = details['movement_data'];
    //const custom_table = details['custom-tables'];
    //const custom_graph = details['custom-graph'];
    //const breakdown_parent = document.getElementById('mission_breakdown');
    const mission_sensor_log = document.getElementById('mission_sensor_log');
    var start_time = shorten_time(breakdown['time_init'])
    var finish_time = shorten_time(breakdown['time_final'])
    const summary = "A mission starting on "+ start_time + " and went to " + finish_time + ", lasting " + breakdown['duration']
    +" seconds. A total of " + breakdown['victims'] + " people were saved. The operator " + breakdown['name']
     + " left \"" + breakdown['notes'] + "\" as a comment on the mission.";
    document.getElementById('mission_summary').innerHTML = summary;
    sensor_fields = ['sensor_data_id', 'acceleration', 'orientation', 'direction', 'distance', 'thermal', 'colour', 'victim', 'time']
    movement_fields = ['movementid', 'type', 'time_init', 'time_final', 'duration','magnitude', 'command_type']
    fill_basic_table('sensors_table_body', sensors, sensor_fields)
    fill_basic_table('movements_table_body', movement,movement_fields)
    return
}
function populate_mission_table(mission_id){
    const mission_cont = document.getElementById('mission_history_container');
    const details_cont = document.getElementById('mission_history');
    const mission_number = document.getElementById('mission_number');
    mission_number.innerHTML = "Mission #"+mission_id;
    mission_cont.setAttribute('hidden', true);
    details_cont.removeAttribute('hidden');

    jq_ajax('/mission-data', mission_id, populate_specific_mission);
    return
}
function return_to_missions(){
    const mission_cont = document.getElementById('mission_history_container');
    const details_cont = document.getElementById('mission_history');
    details_cont.setAttribute('hidden', true);
    mission_cont.removeAttribute('hidden');
    return
}

