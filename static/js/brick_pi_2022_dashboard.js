window.SpeechRecognition = window.SpeechRecognition
                || window.webkitSpeechRecognition;
const recognition = new SpeechRecognition();
recognition.interimResults = false;
recognition.continuous = true;
var synth = window.speechSynthesis;
const time = new Date

commands = {'turn':['left','right', 'degrees'],
            'face':{'north': 0,'east': 90, 'south':180, 'west':270},
            'shoot':'shoot',
            'forward': ['centimetre', 'metre'],
            'spin': ['seconds', 'times']}
compass_directions = {'north': parseInt(0),
                    'east': parseInt(90), 
                    'south':parseInt(180), 
                    'west':parseInt(270)}       

function tts(speech){
    //window.synth.cancel()
    var utterThis = new SpeechSynthesisUtterance(speech);
    utterThis.lang = 'EN-au'; utterThis.volume = 1; 
    utterThis.pitch =.5; utterThis.rate = 1.35;
    window.synth.speak(utterThis);
    console.log(utterThis)
}
function process_transcript(transcript, confidence){
    if (confidence < 0.5){
        tts("Can you please repeat that?")
    }else{
        if (transcript.toLowerCase() == "disable voice commands"){
            recognition.stop()
        }else{
            lower_transcript = transcript.toLowerCase()
            if (lower_transcript.includes('shoot')) {
                tts('fire at will');
            }else if (lower_transcript.includes('stop')){
                tts('stopping');
            }else if (lower_transcript.includes('turn')){
                direction = 'left';
                if (lower_transcript.includes('left')){
                    direction = 'left';
                }else if (lower_transcript.includes('right')){
                    direction = 'right';
                }if (lower_transcript.includes('degrees')){
                    degrees =lower_transcript.match(/(\d+)/)[0]
                }
                turn_instructions = [direction, degrees]
                console.log(turn_instructions)
            }else if (lower_transcript.includes('face')){
                if (lower_transcript.includes('degrees')){
                    degrees =lower_transcript.match(/(\d+)/)[0]
                    console.log(degrees)
                }else{
                    transcript_array = lower_transcript.split(" ")
                    compass_degrees = Object.keys(compass_directions)
                    console.log(compass_directions)
                    converted_degrees = 0
                    divisor = 1
                    for (var i =0; i < transcript_array.length; i++){
                        word = transcript_array[i]
                        if (compass_degrees.includes(word)){
                            converted_degrees += compass_directions[word]
                            console.log(compass_directions[word])
                            divisor +=1
                        }
                    }
                    target_direction = converted_degrees/(divisor-1)
                }
            
            }else if (lower_transcript.includes('forward')){
                numeric =lower_transcript.match(/(\d+)/)[0]
                type = true
                if (lower_transcript.includes('seconds')){
                    type = 's'
                }else if (lower_transcript.includes('centimetre')){
                    type = 'cm'
                }else if(lower_transcript.includes('metre')){
                    type = 'm'
                }else{
                    type = true
                }
                forw_instuctions = [numeric, type]
            }else if (lower_transcript.includes('backward')){
                numeric =lower_transcript.match(/(\d+)/)[0]
                type = true
                if (lower_transcript.includes('seconds')){
                    type = 's'
                }else if (lower_transcript.includes('centimetre')){
                    type = 'cm'
                }else if(lower_transcript.includes('metre')){
                    type = 'm'
                }else{
                    type = true
                }
                back_instuctions = [numeric, type]
            }else if (lower_transcript.includes('you')){
                tts('Please kindly remove yourself from my posterior')
            }else{
                tts('Command not understood')
            }
            
            
            
        }
    }
}


recognition.addEventListener('result', e => {
    const transcript = Array.from(e.results)
        .map(result => result[0])
        .map(result => result.transcript)
        //.join('')
    const confidence = Array.from(e.results)
        .map(result => result[0])
        .map(result => result.confidence)
        //.join('')
    temp_transcript = String(transcript.pop()).trim()
    temp_confidence = String(confidence.pop()).trim()
    process_transcript(temp_transcript, temp_confidence)
    console.log(temp_transcript);
    console.log(temp_confidence);
});
current_keys = {'a': false,
            'w': false,
            's': false,
            'd': false,
            'space': false}
document.addEventListener('keydown', function(e){
    if (!e.repeat){
        time_pressed = time.getTime()
        message = "pressed at: " + time_pressed
        console.log(message)
        if(e.key === 'w'){
            current_keys['w'] = true
        }else if (e.key === 'a'){
            current_keys['a'] = true
        }else if(e.key === 's'){
            current_keys['s'] = true
        }else if (e.key === 'd'){
            current_keys['d'] = true
        }else if (e.keyCode === 32){
            current_keys['space'] = true
        }
        jq_ajax('/process_movement', current_keys, console.log)
    }
    
 })
 document.addEventListener('keyup', function(e){
    if (!e.repeat){
        time_released = time.getTime()
        message = "released at: " + time_released
        console.log(message)
        
        if(e.key === 'w'){
            current_keys['w'] = false
        }else if (e.key === 'a'){
            current_keys['a'] = false
        }else if(e.key === 's'){
            current_keys['s'] = false
        }else if (e.key === 'd'){
            current_keys['d'] = false
        }else if (e.keyCode === 32){
            current_keys['space'] = false
        }
        jq_ajax('/process_movement', current_keys, console.log)
    }
 })