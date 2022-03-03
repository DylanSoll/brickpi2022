const allowedCharacters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890-_.'


function hideOrShow(toHideID, toShowID){
    const toHide = document.getElementById(toHideID);
    const toShow = document.getElementById(toShowID);
    toHide.setAttribute('hidden', true);
    toShow.removeAttribute('hidden');
}



function validateRegister(parentID, navTabToSwap){
    const parent = document.getElementById(parentID);
    const inputArray = parent.getElementsByTagName('input');
    const navTabsParent = document.getElementById(navTabToSwap);
    const navTabs = navTabsParent.getElementsByTagName('a')
    var showModal = true
    var targetObj = {validEmail : false,
        matchEmail: false,
        uniqueEmail: false,
        noSpacesUsername : false,
        usernameLongEnough: false,
        uniqueUsername: false,
        passwordComplexEnough: false,
        matchPassword: false
    }
    
    //match emails

    if (inputArray[0].value === inputArray[1].value){
        targetObj.matchEmail = true;
    }

    //is email valid
    if (inputArray[0].value.length > 0){
        emailValue = inputArray[0].value;
        if (emailValue.includes('@')){
            var emailArray = emailValue.split('@');
            if (emailArray.length === 2){
                if (emailArray[0].length > 0 && emailArray[1].length > 0){
                    targetObj.validEmail = true;
                }
            }
        }
    }
    emailIsValid = document.getElementById('email')
    if (emailIsValid.getAttribute('data-unique-email') == 'true'){
        targetObj.uniqueEmail = true;
    }

    //username
    username = inputArray[2].value;
    if (username.length > 3){
        targetObj.usernameLongEnough = true;
    }
    if (!username.includes(' ')){
        targetObj.noSpacesUsername = true;
    }
    usernameIsValid = document.getElementById('username')
    if (usernameIsValid.getAttribute('data-unique-username') == 'true'){
        targetObj.uniqueUsername = true;
    }


    //match passwords

    if (inputArray[3].value === inputArray[4].value){
        targetObj.matchPassword = true;
    }


    //complex password
    if (inputArray[3].className == "form-control" || inputArray[3].className == "form-control is-invalid"){
        targetObj.passwordComplexEnough = false;
    }
    else{
        targetObj.passwordComplexEnough = true;
    }



    const targetkeys = Object.keys(targetObj);
    for (i = 0; i < targetkeys.length; i++){
        const target = document.getElementById(targetkeys[i]);
        
        if (targetObj[targetkeys[i]] === true){
            target.className = "fa fa-check";
            target.setAttribute('style', "color: green");
        }else{
            showModal = false;
            target.className = "fa fa-times";
            target.setAttribute('style', "color: red");
        }
    }
    
    if (showModal){
        hideOrShow(navTabs[1].id, navTabs[0].id);
    }else{
        hideOrShow(navTabs[0].id, navTabs[1].id);
    }
    
}


function validateAllDetails(button){
    validity = [validateNumber('phoneNumber'), validateNumber('phoneNumber'),
    validateName('fullName'),validateName('fullName'), 
    validatePassword(document.getElementById('password')), matchValues('password', 'confirmPassword'),
    validateEmail(document.getElementById('email')),matchValues('email', 'confirmEmail')];
    console.log(validity)
    if (validity.includes(false)){
        button.setAttribute('type', 'button')
    }else{
        button.setAttribute('type', 'submit')
    }
}

function validatePassword(passwordElement){
    var longEnough= false; 
    var containsUpperCase = false; var containsLowerCase = false;
    var containsNumber = false; var containsSpecial = false;
    const passwordValue = passwordElement.value;
    if (passwordValue.length >= 8){
        longEnough=true;
    }
    for (let letterNum in passwordValue){
        var letter = passwordValue[letterNum]
        if (isNaN(letter) === false) {
            containsNumber = true;
        }
        else{
            if (letter.charCodeAt() >= 97 &&letter.charCodeAt() <= 122){
                containsLowerCase = true;
            }
            
            else if (letter.charCodeAt() >= 65 &&letter.charCodeAt() <= 90){
                containsUpperCase = true;
            }
            else{
                containsSpecial = true;
            }
        }
    }
    
    const listOf = [('lowerCharParaID:'+String(containsLowerCase)), ('upperCharParaID:' + String(containsUpperCase)), 
    ('numberCharParaID:' + String(containsNumber)), ('specialCharParaID:'+String(containsSpecial)), 
    ('longEnoughPasswordID:'+String(longEnough))];
    var valid = true;
    for (var i = 0; i < listOf.length; i++) {
        passwordPart = String(listOf[i]).split(':');
        var error_message = document.getElementById(passwordPart[0]);
        if (passwordPart[1] == 'false'){
            error_message.className = 'fa fa-close';
            error_message.setAttribute('style','color:red');
            valid = false;
        }else{
            error_message.className = 'fa fa-check';
            error_message.setAttribute('style','color:green');
            
        }
        if (!valid){
            passwordElement.className = "form-control is-invalid";
        }
        else{
            passwordElement.className = "form-control is-valid";
        }
    }
    return valid
    
}


function matchValues(firstVal, confirmValID){
    const toConfirm = document.getElementById(firstVal).value;
    const confirm = document.getElementById(confirmValID);
    const confirmValue = confirm.value;
    var valid = false;
    if (toConfirm == confirmValue){
        confirm.className = "form-control is-valid";
        valid = true;
    }
    else{
        confirm.className = "form-control is-invalid";
        valid = false;
    }
    return valid
}
function valid_email_res(result){
    if (result != false){
        email.className = "form-control is-invalid";
        email.setAttribute('data-unique-email','false');
        valid = false
    }else{
        email.className = "form-control is-valid";
        email.setAttribute('data-unique-email','true');
        valid = true
    }
    return valid
}
function validateEmail(email){
    const emailValue = email.value;
    var valid = false;
    if (emailValue.length > 0){
        if (emailValue.includes('@')){
            var emailArray = emailValue.split('@');
            if (emailArray.length === 2){
                if (emailArray[0].length > 0 && emailArray[1].length > 0){
                    valid = true;
                }
            }
        }
        if (valid){
            $.ajax({
                type: "POST",
                url: '/uniqueEmail',
                data: JSON.stringify(emailValue),
                contentType: "application/json",
                dataType: 'json',
                success: function(result) {
                    if (result != false){
                        email.className = "form-control is-invalid";
                        email.setAttribute('data-unique-email','false');
                        valid = false
                    }else{
                        email.className = "form-control is-valid";
                        email.setAttribute('data-unique-email','true');
                        valid = true
                    }
                    
                  } 
                
            });
        }
        else{
            email.className = "form-control is-invalid"
        }
    }
    return valid
}


function validateName(nameID){
    const name = document.getElementById(nameID);
    const nameValue = name.value;
    var valid = false;
    if (nameValue.includes(' ')){
        var nameArray = nameValue.split(' ')
        if (nameArray[0].length > 0 && nameArray[1].length > 0){
            name.className = "form-control is-valid"
            valid = true;
        }

    }else{
        name.className = "form-control is-invalid"
        valid = false;
    }
    return valid
}


function validateNumber(numberID){
    const number = document.getElementById(numberID);
    var numberValue = number.value.replaceAll(' ','');
    var valid = true;
    if (numberValue.length !== 10){
        valid = false;
    }else{
        for (var i = 0; i < numberValue.length; i++){
            if(isNaN(parseInt(numberValue[i]))){
                valid = false;
            }
        }
    }
    if (valid){
        number.className = "form-control is-valid";
    }
    else{
        number.className = "form-control is-invalid";
    }
    return valid
}
