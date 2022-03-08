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
        vc_button.innerHTML = 'Stop VC <i class="fa fa-microphone-slash"></i>'
        vc_button.setAttribute('class', 'btn btn-warning')
    }else if (current == 'stop'){
        vc_button.setAttribute('data-current', 'start')
        vc_button.setAttribute('onclick', 'recognition.start();swap_vc(this.id)')
        vc_button.innerHTML = 'Start VC <i class="fa fa-microphone"></i>'
        vc_button.setAttribute('class', 'btn btn-success')
    } 
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
    if (!e.repeat){
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
    if (!e.repeat){
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
            jq_ajax('/process_movement', current_keys, defaulthandle);
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
    if (button.className == 'btn btn-success'){
        button.className = "btn btn-danger"
        button.setAttribute('onclick',"jq_ajax('/end-mission');stop_start_mission()")
        button.innerHTML = "End Mission"
    }else if (button.className == 'btn btn-danger'){
        button.className = "btn btn-success"
        button.setAttribute('onclick',"jq_ajax('/initiate-mission');stop_start_mission()")
        button.innerHTML = "Start Mission"
    }
    
}