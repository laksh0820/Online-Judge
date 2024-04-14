// Importing modules
const fs = require('fs');

// Retrive Elements
const run_btn = document.querySelector('#editor__run');
const reset_btn = document.querySelector('#editor__reset');
const input_btn = document.querySelector('#input_tab');
const output_btn = document.querySelector('#output_tab');
const submit_btn = document.querySelector('#submit_tab')
const input_textarea = document.querySelector('#input_textarea');
const output_textarea = document.querySelector('#output_textarea');
const file_upload = document.querySelector('#fileToUpload');
const file_load = document.querySelector('#file_load');
const file_submit = document.querySelector('#fileUpload')

// decoder function

function b64DecodeUnicode(str) {
    // Going backwards: from bytestream, to percent-encoding, to original string.
    return decodeURIComponent(atob(str).split('').map(function(c) {
        return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
    }).join(''));
}

// Setup Ace
let codeEditor = ace.edit("editorCode");

let defaultCode = '#include <stdio.h>\n\nint main() {\n\n    //Enter your code\n\n    return 0;\n}';

let editorLib = {
    init(){
        // Configure Ace

        // Theme
        codeEditor.setTheme("ace/theme/monokai");

        // Set langugage
        codeEditor.session.setMode("ace/mode/c_cpp");

        // Set options
        codeEditor.setOptions({
            fontSize: '14pt',
            enableBasicAutocompletion: true,
            enableLiveAutocompletion: true,
        })

        // Set default code
        codeEditor.setValue(defaultCode);
    }
}

editorLib.init();


// Events

// Run button
run_btn.addEventListener('click',()=>{
    output_btn_func();
    const userCode = codeEditor.getValue();
    const stdin = input_textarea.value;
    const dict_value = {userCode,stdin};

    // Set value to empty upon click
    output_textarea.value = "";

   $.ajax({
        url:"/onlineIDE",
        type:"POST",
        contentType:"application/json",
        data:JSON.stringify(dict_value),
        success:function(response)
        {
            console.log(response);
            let stdout = response["stdout"];
            let compile_output = response["compile_output"];

            if(stdout!=""){
                output_textarea.value = stdout;   
            }
            else{
                if(compile_output!=""){
                    output_textarea.value = compile_output;
                }
                else output_textarea.value = "";
            }
        }
   });
});

// Reset Button
reset_btn.addEventListener('click',()=>{
    codeEditor.setValue(defaultCode);
    if (file_upload != null) {file_upload.value=null;};
    if (file_submit != null) {file_submit.value=null;};
});

// Input button
input_btn.addEventListener('click',()=>{
    output_btn.classList.remove("highlight_btn");
    output_textarea.classList.add("hidden");
    input_btn.classList.add("highlight_btn");
    input_textarea.classList.remove("hidden");
});

// Output button
output_btn.addEventListener('click',output_btn_func)
function output_btn_func(){
    input_btn.classList.remove("highlight_btn");
    input_textarea.classList.add("hidden");
    output_btn.classList.add("highlight_btn");
    output_textarea.classList.remove("hidden");
};


// Submit button
if (submit_btn != null){
    const code = {data:codeEditor.getValue()};
    submit_btn.addEventListener('click',()=>{
        code.data = codeEditor.getValue();
        if (file_submit.files.length != 0){
            const file_reader = new FileReader();
            file_reader.addEventListener("load",()=>{
                code.data = file_reader.result;
            });
            file_reader.readAsText(file_submit.files[0]);
            setTimeout(helper_func , 500);
        }else {
            helper_func();
        };
    });
    function helper_func (){
        const problem_id = document.getElementById('problem_id').getAttribute('myid');
        const dict_value = {userCode:code.data,problem_id};
        $.ajax({
                url:"/problem/1",
                type:"POST",
                contentType:"application/json",
                data:JSON.stringify(dict_value),
                success:function(response)
                {
                    window.location.href = response.redirect
                }
        });
    };
}


// File Upload To Editor Submit Button
if (file_load != null){
    file_load.addEventListener('click',()=>{
        const file_reader = new FileReader();
        file_reader.addEventListener("load",()=>{
            const code_file = file_reader.result;
            codeEditor.setValue(code_file);
        });
        file_reader.readAsText(file_upload.files[0]);
    });
}

