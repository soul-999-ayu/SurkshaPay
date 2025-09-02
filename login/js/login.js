var login = document.getElementById("login");
var forgotEmail = document.getElementById("forgot");
var forgotOTP = document.getElementById("forgot2");
var forgotPass = document.getElementById("forgot3");

function toForgotPass(){
    login.style.display = "none";
    forgotEmail.style.display = "block";
}

function backToLogin(page){
    if(page=="p1"){
        forgotEmail.style.display = "none";
        login.style.display = "block";
    }
    else if(page=="p2"){
        forgotOTP.style.display = "none";
        login.style.display = "block";
    }
    else if(page=="p3"){
        forgotPass.style.display = "none";
        login.style.display = "block";
    }
}

function sendOTP(){
    forgotEmail.style.display = "none";
    forgotOTP.style.display = "block";
}

function changePass(){
    forgotOTP.style.display = "none";
    forgotPass.style.display = "block";
}