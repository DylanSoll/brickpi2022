window.SpeechRecognition = window.SpeechRecognition
                || window.webkitSpeechRecognition;
const recognition = new SpeechRecognition();
recognition.interimResults = false;
recognition.continuous = true;
var synth = window.speechSynthesis;
const time = new Date
function defaulthandle(results){
    temp_var = results
}
var allow_sensors = false;
var allow_keypress = true
commands = {'turn':['left','right', 'degrees'],
            'face':{'north': 0,'east': 90, 'south':180, 'west':270},
            'shoot':'shoot',
            'forward': ['centimetre', 'metre'],
            'spin': ['seconds', 'times']}
compass_directions = {'north': parseInt(0),
                    'east': parseInt(90), 
                    'south':parseInt(180), 
                    'west':parseInt(270)}       
function swap_vc(id){
    const vc_button = document.getElementById(id)
    current = vc_button.getAttribute('data-current')
    if (current == 'start'){
        vc_button.setAttribute('data-current', 'stop')
        vc_button.setAttribute('onclick', 'recognition.stop(); swap_vc(this.id)')
        vc_button.innerHTML = 'Disable VC <i class="fa fa-microphone-slash"></i>'
        vc_button.setAttribute('class', 'btn btn-warning')
    }else if (current == 'stop'){
        vc_button.setAttribute('data-current', 'start')
        vc_button.setAttribute('onclick', 'recognition.start();swap_vc(this.id)')
        vc_button.innerHTML = 'Enable VC <i class="fa fa-microphone"></i>'
        vc_button.setAttribute('class', 'btn btn-success')
    } 
}

function reset_image_settings(){
    document.getElementById('upper_colour').value =  "#ffffff"
    document.getElementById('lower_colour').value =  "#000000"
    document.getElementById('h_victims').setAttribute('checked', '') 
    document.getElementById('u_victims').setAttribute('checked', '') 
    jq_ajax('/update-colour-mask/lower', document.getElementById('lower_colour').value)
    jq_ajax('/update-colour-mask/upper', document.getElementById('upper_colour').value)
}


function tts(speech){
    //window.synth.cancel()
    var utterThis = new SpeechSynthesisUtterance(speech);
    utterThis.lang = 'EN-au'; utterThis.volume = 1; 
    utterThis.pitch =.5; utterThis.rate = 1.35;
    window.synth.speak(utterThis);
}
function process_transcript(transcript, confidence){
    if (confidence < 0.5){
        tts("Can you please repeat that?");
    }else{
        if (transcript.toLowerCase() == "disable voice commands"){
            recognition.stop();
            tts('Disabling Voice Commands');
        }else{
            power = document.getElementById('power').value
            lower_transcript = transcript.toLowerCase();
            instructions = [];
            respons = ""
            if (lower_transcript.includes('shoot') || lower_transcript.includes('fire')) {
                instructions = ['fire', true];
                response = "Delivering Packing"
            }else if (lower_transcript.includes('stop')){
                instructions = ['stop', true];
                respone = 'Stopping'
            }else if (lower_transcript.includes('turn')){
                direction = 'left';
                if (lower_transcript.includes('left')){
                    direction = 'left';
                }else if (lower_transcript.includes('right')){
                    direction = 'right';
                }if (lower_transcript.includes('degrees')){
                    degrees =lower_transcript.match(/(\d+)/)[0];
                }else{
                    degrees = 0;
                    tts('No degrees were given');
                }
                response = "Turning "+ direction + " " + degrees + " degrees.";
                instructions = [direction, degrees, 'degrees', power];
            }else if (lower_transcript.includes('face')){
                if (lower_transcript.includes('degrees')){
                    target_direction =lower_transcript.match(/(\d+)/)[0];
                    if (isNaN(target_direction)){
                        target_direction = 0;
                    }
                }else{
                    transcript_array = lower_transcript.split(" ");
                    compass_degrees = Object.keys(compass_directions);
                    converted_degrees = 0;
                    divisor = 1;
                    for (var i =0; i < transcript_array.length; i++){
                        word = transcript_array[i];
                        if (compass_degrees.includes(word)){
                            converted_degrees += compass_directions[word];
                            divisor +=1;
                        }
                    }
                    target_direction = converted_degrees/(divisor-1);
                }
                instructions = ['face', target_direction, 'degrees', power];
                response = "Turning to face " + target_direction + " degrees";
            }else if (lower_transcript.includes('forward')){
                numeric = lower_transcript.match(/(\d+)/);
                if (numeric == null){
                    numeric = 0;
                }else{
                    numeric = numeric[0];
                }
                if (lower_transcript.includes('seconds')){
                    type = 'seconds';
                }else if (lower_transcript.includes('centimetre')){
                    type = 'centimetres';
                }else if(lower_transcript.includes('metre')){
                    type = 'metres';
                }else{
                    type = 'seconds';
                }
                instructions = ['forward', numeric, type, power];
                response = "Moving forward for " +numeric + type;
            }else if (lower_transcript.includes('backward') || lower_transcript.includes('reverse')){
                numeric =lower_transcript.match(/(\d+)/);
                if (numeric == null){
                    numeric = 0;
                }else{
                    numeric = numeric[0];
                }
                if (lower_transcript.includes('seconds')){
                    type = 'seconds';
                }else if (lower_transcript.includes('centimetre')){
                    type = 'centimetre';
                }else if(lower_transcript.includes('metre')){
                    type = 'metre';
                }else{
                    type = 'seconds';
                }
                instructions = ['backward',numeric, type, power];
                response = "Moving backward for " +numeric + type;
            }else if (lower_transcript.includes('play')){
                response = "Playing loaded song";
                instructions = ['play', true];
            }else{
                tts('Command not understood')
                instructions = 'null';
            }
            if (instructions != 'null'){
                jq_ajax('/process_voice_commands', instructions, defaulthandle);
                tts(response);
            }
            
            
        }
    }
}





current_keys = {'a': false,
            'w': false,
            's': false,
            'd': false,
            'space': false,
            'stop': false};

document.addEventListener('keydown', function(e){
    if ((!e.repeat) && (allow_keypress) && (robot_enabled)){
        time_pressed = time.getTime();
        message = "pressed at: " + time_pressed;
        valid_keys = ['w', 'a', 's', 'd', 'p'];
        firing_key = [' '];
        if(e.key === 'w'){
            current_keys['w'] = true;
        }else if (e.key === 'a'){
            current_keys['a'] = true;
        }else if(e.key === 's'){
            current_keys['s'] = true;
        }else if (e.key === 'd'){
            current_keys['d'] = true;
        }else if (e.key === 'p'){
            current_keys['stop'] = true;
        }
        if (valid_keys.includes(e.key)){
            jq_ajax('/process_movement/'+document.getElementById('power').value, current_keys, defaulthandle);
        }else if (firing_key.includes(e.key)){
            jq_ajax('/process_shooting', {}, defaulthandle);
        }
    }
    
 })
 document.addEventListener('keyup', function(e){
    if ((!e.repeat) && (allow_keypress)&& (robot_enabled)){
        time_released = time.getTime();
        message = "released at: " + time_released;
        valid_keys = ['w', 'a', 's', 'd', 'p'];
        if(e.key === 'w'){
            current_keys['w'] = false;
        }else if (e.key === 'a'){
            current_keys['a'] = false;
        }else if(e.key === 's'){
            current_keys['s'] = false;
        }else if (e.key === 'd'){
            current_keys['d'] = false;
        }else if (e.key === ' '){
            current_keys['space'] = false;
        }
        else if (e.key === 'p'){
            current_keys['stop'] = false;
        }
        if (valid_keys.includes(e.key)){
            jq_ajax('/process_movement/0', current_keys, defaulthandle);
        }
    }
 })

recognition.addEventListener('result', e => {
    const transcript = Array.from(e.results)
        .map(result => result[0])
        .map(result => result.transcript)
        //.join('')
    const confidence = Array.from(e.results)
        .map(result => result[0])
        .map(result => result.confidence)
        //.join('')
    temp_transcript = String(transcript.pop()).trim();
    temp_confidence = String(confidence.pop()).trim();
    process_transcript(temp_transcript, temp_confidence);
    recognition.stop()
    recognition.start()
});

function stop_start_mission(){
    const button = document.getElementById('missions-button');
    const modal_button = document.getElementById('missions-modal-button');
    if (button.hasAttribute('hidden')){
        button.removeAttribute('hidden')
        modal_button.setAttribute('hidden', true)
    }else if (modal_button.hasAttribute('hidden')){
        modal_button.removeAttribute('hidden')
        button.setAttribute('hidden', true)
    }
    
}

function suspend_mission(interval){
    clearInterval(interval);
    allow_keypress = false;
    allow_sensors = false;
}

function resume_mission(){
    interval = setInterval(function(){jq_ajax('/sensors', {}, defaulthandle)},2000)
    allow_keypress = true;
    allow_sensors = true;
    return interval
}






const commands_help = {'help':'Display commands', 'forward': 'Move forward x centimeters or seconds', 
  'back': 'Move back x centimeters or seconds', 'left': 'Turn left x degrees or seconds', 'right': 'Turn right x degrees or seconds',
  'fire': 'Deliver medical package', 'stop': 'Stops all movement'};
function toggle_chatbox(buttonid, chatboxid){
    var button = document.getElementById(buttonid);
    var chatbox = document.getElementById(chatboxid);
    if (button.hasAttribute('hidden')){
      button.removeAttribute('hidden')
      chatbox.setAttribute('hidden', true)
    }else{
      chatbox.removeAttribute('hidden')
      button.setAttribute('hidden', true)
    }
    return
  }
  function add_response(response){
    var target = document.getElementById('sent_messages')
    var temp_div = document.createElement('div')
    temp_div.innerHTML = response
    temp_div.className = "command-response-text"
    target.appendChild(temp_div)
    return
  }

  function send_command(inputid){
    var input_element = document.getElementById(inputid)
    var message = input_element.value.toLowerCase()
    console.log(message)
    if (message.includes('help')){
      commands_list = Object.keys(commands_help)
      
      for (var i = 0; i < commands_list.length; i++){
        response = "<u data-toggle='tooltip' data-placement='top' title="+commands_list[i]+">" + commands_list[i] + "</u> : " +commands_help[commands_list[i]]
        add_response(response);
      }
    }else if (message.includes('say')){
      phrase = message.splice('say').slice(1);
      phrase = phrase.join(say);
      jq_ajax('/say-phrase', phrase, add_response);
    }else if (message.includes('shoot')){
      jq_ajax('/process_shooting');
      add_response('Firing')
    }else if (message.includes('kill')){
      jq_ajax('/robotshutdown');
      add_response('Shut down everything')
    }
    input_element.value = ""
  }
  function enlarge_console(){
    var console_el = document.getElementById('message_box');
    var trigger = document.getElementById('resize_console');
    var text_area = document.getElementById('textbox_area');
    var terminal_counter = document.getElementById('terminal-counter');
    trigger.setAttribute('onclick',"shrink_console()");
    trigger.className = "fa fa-compress fa-2x pointer";
    console_el.className = "message-box cs-lg";
    text_area.className = "textbox-area cs-lg";
    terminal_counter.removeAttribute('hidden');

  }
  function shrink_console(){
    var console_el = document.getElementById('message_box');
    var trigger = document.getElementById('resize_console');
    var text_area = document.getElementById('textbox_area');
    var terminal_counter = document.getElementById('terminal-counter');

    trigger.setAttribute('onclick',"enlarge_console()");
    trigger.className = "fa fa-expand fa-2x pointer";
    console_el.className = "message-box cs-sm";
    text_area.className = "textbox-area cs-sm";
    terminal_counter.setAttribute('hidden', true);
  }