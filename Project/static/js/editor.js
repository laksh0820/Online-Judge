// Retrive Elements
const run_btn = document.querySelector('.editor__run');
const reset_btn = document.querySelector('.editor__reset');
const input_btn = document.querySelector('#input_tab');
const output_btn = document.querySelector('#output_tab');
const input_textarea = document.querySelector('#input_textarea');
const output_textarea = document.querySelector('#output_textarea');

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
run_btn.addEventListener('click',async () => {
    // Get input from the code editor
    const userCode = codeEditor.getValue();
    const encoded_code = btoa(userCode);
    const stdin = input_textarea.value;
    const encoded_std = btoa(stdin);

    // Send this code to API to parse it. How exactly to do this?

    // 1. Just use judge0 -> not very impressive, doesn't require any backend work
    // 2. Create an API, use Python in backend for shell scripting, compile and send data back to the front end.

    const settings = {
        async: true,
        crossDomain: true,
        url: 'https://judge0-ce.p.rapidapi.com/submissions?base64_encoded=true&wait=true&fields=*',
        method: 'POST',
        headers: {
            'content-type': 'application/json',
            'Content-Type': 'application/json',
            'X-RapidAPI-Key': '29a58e30d8msh81af7566051cd6ep196b88jsne041a8d0a091',
            'X-RapidAPI-Host': 'judge0-ce.p.rapidapi.com'
        },
        processData: true,
        data: '{\r\n    "language_id": 50,\r\n    "source_code": "' + encoded_code + '",\r\n    "stdin": "' + encoded_std + '"\r\n}'
    };
    
    $.ajax(settings).done(function (response) {
        console.log(response);
        let stdout = response["stdout"];
        let compile_output = response["compile_output"];

        if(stdout!=null){
            output_textarea.value = b64DecodeUnicode(stdout);
        }
        else{
            if(compile_output!=null){
                output_textarea.value = b64DecodeUnicode(compile_output);
            }
            else output_textarea.value = "";
        }
    });
});

// Reset Button

reset_btn.addEventListener('click',()=>{
    codeEditor.setValue(defaultCode);
});

// Input button
input_btn.addEventListener('click',()=>{
    output_btn.classList.remove("highlight_btn");
    input_btn.classList.add("highlight_btn");
    output_textarea.classList.add("hidden");
    input_textarea.classList.remove("hidden");
});

// Output button
output_btn.addEventListener('click',()=>{
    input_btn.classList.remove("highlight_btn");
    output_btn.classList.add("highlight_btn");
    input_textarea.classList.add("hidden");
    output_textarea.classList.remove("hidden");
});
