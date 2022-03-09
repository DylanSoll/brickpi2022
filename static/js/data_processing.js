function shorten_time(epoch_time){
    time = String(new Date(epoch_time*1000)).split(' ').slice(0,5).join(" ")
    return time
}

function create_checkbox(id, text){
    var form_check = document.createElement('div');
    form_check.className = 'form-check';   
    var input_element = document.createElement('input');
    input_element.className = "form-check-input";
    input_element.type = 'checkbox';
    input_element.value = "";
    input_element.id = id;
    var input_label = document.createElement('label');
    input_label.className = "form-check-label";
    input_label.setAttribute('for', id);
    input_label.innerHTML = text
    form_check.appendChild(input_element);
    form_check.appendChild(input_label);
    return form_check
}

function fill_basic_table(table_id, datasets, fields){
    table = document.getElementById(table_id)
    table.innerHTML = ""
    for (var row = 0; row < datasets.length; row++){
        const row_obj = datasets[row];
        const new_row = document.createElement('tr');
        new_row.setAttribute('data-hidden-by', JSON.stringify({}));
        for (var field_num = 0; field_num < fields.length; field_num++){
            var field = fields[field_num]
            if (field.includes('time')) {
                data = shorten_time(row_obj[field])
            }else if (field == 'select'){
                data = create_checkbox('select_all_'+table_id, '')
            }else{
                data = row_obj[field]
            }
            new_td = document.createElement('td');
            if (typeof(data) == "object"){
                new_td.appendChild(data)
            }else{
                new_td.innerHTML = data;
            }
            
            data_label = 'data-'+field
            string_obj = new_row.getAttribute('data-hidden-by')
            temp_obj = JSON.parse(string_obj) 
            temp_obj[field] = false;
            new_row.setAttribute(data_label, data)
            new_row.setAttribute('data-hidden-by', JSON.stringify(temp_obj))
            new_row.appendChild(new_td);
        }

        table.appendChild(new_row)
    }
    return
}

function create_table_shell(parentid, columns, bodyid, datasets, fields){
    parent = document.getElementById(parentid);
    var table = document.createElement('table');
    var thead = document.createElement('thead');
    var header_row = document.createElement('tr');
    var filter_row = document.createElement('tr');
    column_ids = Object.keys(columns);
    for (var i = 0; i < column_ids.length; i++){
        current_column = column_ids[i];
        column_name = columns[current_column];
        var temp_th = document.createElement('th');
        temp_th.setAttribute('scope', 'col');
        temp_th.innerHTML = column_name;// + ' <i class="fa fa-arrow-up"></i>';
        header_row.appendChild(temp_th);

        //
        var filter_th = document.createElement('th');
        filter_th.setAttribute('scope', 'col');
        if (current_column == 'select'){
            filter_th.appendChild(create_checkbox('select_all_'+parentid, 'Select '))

        }else{
            var filter_input = document.createElement('input');
            filter_input.type = 'text';
            filter_input.placeholder = "Filter...";
            filter_input.setAttribute('data-search', current_column);
            filter_input.setAttribute('oninput', "search_table(this,"+ "'" +bodyid+"')");
            filter_th.appendChild(filter_input);
        }
        filter_row.appendChild(filter_th);
    }
    thead.appendChild(header_row);
    thead.appendChild(filter_row);
    table.appendChild(thead);
    var tbody = document.createElement('tbody');
    tbody.id = bodyid;
    table.appendChild(tbody)
    parent.appendChild(table)
    fill_basic_table(bodyid, datasets, fields)
    return parent
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
            }
            else{
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


function lineGraph(user_title, locationid, row_array, column_obj,legend_pos = 'bottom',  curve = 'none'){

    google.charts.load('current', {'packages':['corechart']});
          google.charts.setOnLoadCallback(drawchart); 
          function drawchart(){
            y_axis_name = String(user_title).split(' vs')[0]
          
            var data = new google.visualization.DataTable();
            columns = Object.keys(column_obj)
            for (var i = 0; i < columns.length; i++){
              data.addColumn(column_obj[columns[i]], columns[i])
            }
    
          data.addRows(row_array);
            
            var options = {
                title: user_title,
                curveType: curve,
                legend: { position: legend_pos },
                selectionMode: 'multiple',
                tooltip: {trigger: 'selection'},
                aggregationTarget: 'category',
                /*hAxis: {
                    title: 'Time',
                    direction: 1,
                    minTextSpacing: 1,
                    showTextEvery: 1
                  },
                vAxis: {
                    title: y_axis_name,
                    direction: 1,
                    minTextSpacing: 1,
                    showTextEvery: 1
                  }*/
                };
    
            var chart = new google.visualization.LineChart(document.getElementById(locationid));
    
            chart.draw(data, options);}
          }

google.charts.load('current', {'packages':['gauge']});
google.charts.setOnLoadCallback(drawChart);
      
function drawGuage() {
var data = google.visualization.arrayToDataTable([
    ['Label', 'Value'],
    ['Battery', 80],
]);

var options = {
    width: 400, height: 120,
    redFrom: 0, redTo: 20,
    yellowFrom:20, yellowTo: 60,
    greenFrom: 60, greenTo:100,
    minorTicks: 5
};

var chart = new google.visualization.Gauge(document.getElementById('battery_graph'));

chart.draw(data, options);

setInterval(function() {
    data.setValue(0, 1, 40 + Math.round(60 * Math.random()));
    chart.draw(data, options);
}, 1300);
}
function drawGuage(target, info, colour_banding, size, minor_ticks = 5) {
    google.charts.load('current', {'packages':['gauge']});
    google.charts.setOnLoadCallback(drawchart());
    function drawchart(){
        var data = new google.visualization.DataTable();
        data.addColumn('string', 'Label');
        data.addColumn('number', 'Value');
        data.addRow([
          ['Battery', 80]
        ]);
        
    
        var options = {
            width: size['width'], height: size['height'],
            redFrom: colour_banding['redFrom'], redTo: colour_banding['redTo'],
            yellowFrom:colour_banding['yellowFrom'], yellowTo: colour_banding['yellowTo'],
            greenFrom: colour_banding['greenFrom'], greenTo:colour_banding['greenTo'],
            minorTicks: minor_ticks
        };
        
        var chart = new google.visualization.Gauge(document.getElementById(target));
        console.log(chart)
        chart.draw(data, options);
    }
        
}
    


function populate_specific_mission(details){
    const breakdown = details['breakdown'][0];
    const sensors = details['sensor_data'];
    const movement = details['movement_data'];
    //const custom_table = details['custom-tables'];
    //const custom_graph = details['custom-graph'];
    //const breakdown_parent = document.getElementById('mission_breakdown');
    //const mission_sensor_log = document.getElementById('mission_sensor_log');
    var start_time = shorten_time(breakdown['time_init'])
    var finish_time = shorten_time(breakdown['time_final'])
    const summary = "A mission starting on "+ start_time + " and went to " + finish_time + ", lasting " + breakdown['duration']
    +" seconds. A total of " + breakdown['victims'] + " people were saved. The operator " + breakdown['name']
        + " left \"" + breakdown['notes'] + "\" as a comment on the mission.";
    document.getElementById('mission_summary').innerHTML = summary;
    sensor_fields = ['sensor_data_id', 'acceleration', 'orientation', 'direction', 'distance', 'thermal', 'colour', 'victim', 'time']
    movement_fields = ['movementid', 'type', 'time_init', 'time_final', 'duration','magnitude', 'command_type']
    sensor_columns = {'sensor_data_id': 'Record ID', 'acceleration': 'Acceleration (m/s/s)', 'orientation':'Orientation (°)', 
    'direction':'Direction', 'distance':'Distance (cm)', 'thermal':'Thermal (°C)', 
    'colour':'Colour', 'victim':'Victim', 'time':'Time'}
    movement_columns = {'movementid': 'Movement ID', 'type': 'Type', 'time_init':'Start Time', 
    'time_final':'End Time', 'duration': 'Duration (s)','magnitude':'Magnitude', 'command_type': 'Method'}
    if (document.getElementById('sensors_table_body') == null){
        create_table_shell('mission_sensor_table', sensor_columns,'sensors_table_body', sensors, sensor_fields);
        create_table_shell('mission_movement_table', movement_columns,'movements_table_body', movement, movement_fields);
    }
    else{
        fill_basic_table('sensors_table_body', sensors, sensor_fields);
        fill_basic_table('movements_table_body', movement, movement_fields);
    }
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

function create_graphs(values){
    mission_graphs = {'mission_acceleration_graph':document.getElementById('mission_acceleration_graph'),
    'mission_orientation_graph':document.getElementById('mission_orientation_graph'),
    'mission_thermal_graph':document.getElementById('mission_thermal_graph')}
    mission_graph_keys = Object.keys(mission_graphs)
    for (var i = 0; i < mission_graph_keys.length; i++){
        target = String(String(mission_graph_keys[i]).split('mission_')[1]).split('_graph')[0]
        all_vals = []
        for (var result = 0; result < values.length; result++){
            val_obj = values[result]
            row_val = [shorten_time(val_obj['time']), val_obj[target]]
            all_vals.push(row_val)
        }
        title = target  + " vs Time"
        columns = {'time': 'string', target: 'number'}
        lineGraph(title, String(mission_graph_keys[i]), all_vals, columns)
    }
}

function search_table(search, tableid){
    table = document.getElementById(tableid)
    text = search.value
    type = search.getAttribute('data-search')
    rows = table.getElementsByTagName('tr')
    for (var row_num = 0; row_num < rows.length; row_num++){
        row = rows[row_num]
        target_data = 'data-'+type
        if (row.hasAttribute(target_data)){
            data = row.getAttribute(target_data)
            hidden_by = JSON.parse(row.getAttribute('data-hidden-by'))
            hidden_by_keys = Object.keys(hidden_by);
            if (hidden_by_keys.includes(type)){
                if (data.includes(text)){
                    hidden_by[type] = false
                }else{
                    hidden_by[type] = true 
                }
            }
            hidden_by_values = Object.values(hidden_by)
            row.setAttribute('data-hidden-by', JSON.stringify(hidden_by))
            if (hidden_by_values.includes(true)){
                row.setAttribute('hidden', true)
            }else{
                row.removeAttribute('hidden')
            }
        }
    }
}



function create_mission_carosel(missions){
    var parent = document.getElementById('carousel-inner');
    var indicator = document.getElementById('carousel-indicators')
    for (var i = 0; i < missions.length; i++){
        var carousel_indicator = document.createElement('button');
        carousel_indicator.type = "button";
        carousel_indicator.setAttribute('data-bs-target', '#carouselExampleCaptions');
        carousel_indicator.setAttribute('data-bs-slide-to', i);
        carousel_indicator.setAttribute('aria-label', 'Slide ' + String(i+1));
        var current_mission = missions[i];
        var container = document.createElement('div');
        if (i == 0){
            container.className = 'carousel-item active';
            carousel_indicator.className = 'Active'
            carousel_indicator.setAttribute('aria-current', true);
        }else{
            container.className = 'carousel-item';
        }
        var mission_item = document.createElement('div');
        mission_item.className = 'mission_item';
        var carousel_content = document.createElement('div');
        var title = document.createElement('h3')
        title.innerHTML = 'Mission #'+ current_mission['missionid']
        var name = document.createElement('h5');
        name.innerHTML = current_mission['name'];
        var notes = document.createElement('p');
        notes.innerHTML = current_mission['notes'];
        carousel_content.appendChild(title);
        carousel_content.appendChild(name);
        carousel_content.appendChild(notes);
        mission_item.appendChild(carousel_content);
        container.appendChild(mission_item);
        parent.append(container);
        indicator.appendChild(carousel_indicator)

    }
    var generic_button =  document.createElement('button');
    generic_button.type = 'button';
    generic_button.setAttribute('data-bs-target', '#carouselExampleCaptions');
    next_button = generic_button;
    prev_button = generic_button;
    prev_button.className = "carousel-control-prev";
    prev_button.setAttribute('data-bs-slide',"prev");
    prev_span = document.createElement('span');
    prev_span_label = document.createElement('span');
    prev_span.className = "carousel-control-prev-icon";
    prev_span.setAttribute('aria-hidden',"true");
    prev_span_label.className = 'visually-hidden';
    prev_span_label.innerHTML = "Previous";
    prev_button.appendChild(prev_span)
    prev_button.appendChild(prev_span_label)


    next_button.className = "carousel-control-next";
    next_button.setAttribute('data-bs-slide',"next");
    next_span = document.createElement('span');
    next_span_label = document.createElement('span');
    next_span.className = "carousel-control-next-icon";
    next_span.setAttribute('aria-hidden',"true");
    next_span_label.className = 'visually-hidden';
    next_span_label.innerHTML = "Next";
    next_button.appendChild(next_span)
    next_button.appendChild(next_span_label)
    document.getElementById('carouselExampleCaptions').appendChild(prev_button)
    document.getElementById('carouselExampleCaptions').appendChild(next_button)
    
}

function create_table(details){
    columns = details['columns']
    table_id = details['table_id']
    body_id = details['body_id']
    fields = details['fields']
    data = details['datasets']
    create_table_shell(table_id, columns, body_id, data, fields);
    return
}