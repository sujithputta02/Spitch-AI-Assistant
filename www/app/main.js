$(document).ready(function() {
	$('.text').textillate({
        loop: true,
        sync: true,
        in: {
            effect: "bounceIn",
        },
        out: {
            effect: "bounceOut",
        },

    });


    var siriWave = new SiriWave({
        container: document.getElementById("siri-container"),
        width: 800,
        height: 200,
        style: "ios9",
        amplitude: "1",
        speed: "0.30",
        autostart: true
      });

      $('.siri-message').textillate({
        loop: true,
        sync: true,
        in: {
            effect: "fadeInUp",
            sync: true,
        },
        out: {
            effect: "fadeOutUp",
            sync: true,
        },

    });

    // Voice Assistant Status
    var voiceAssistantActive = false;
    var recognition;
    var recognizing = false;

    // Check for browser speech recognition support
    window.SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition || null;
    if (window.SpeechRecognition) {
        recognition = new window.SpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = 'en-US';

        recognition.onstart = function() {
            recognizing = true;
            voiceAssistantActive = true;
            $("#MicBtn").prop('disabled', false);
            $("#MicBtn").html('<i class="bi bi-mic-mute"></i>');
            $("#MicBtn").attr('title', 'Stop Voice Assistant (Esc)');
            $("#MicBtn").removeClass('btn-loading').addClass('btn-active');
            $("#Oval").attr("hidden", true);
            $("#SiriWave").attr("hidden", false);
            showKeyboardHint();
        };

        recognition.onend = function() {
            recognizing = false;
            voiceAssistantActive = false;
            $("#MicBtn").prop('disabled', false);
            $("#MicBtn").html('<i class="bi bi-mic"></i>');
            $("#MicBtn").attr('title', 'Start Voice Assistant (Ctrl+Shift+M)');
            $("#MicBtn").removeClass('btn-loading btn-active');
            $("#Oval").attr("hidden", false);
            $("#SiriWave").attr("hidden", true);
            hideKeyboardHint();
        };

        recognition.onerror = function(event) {
            recognizing = false;
            voiceAssistantActive = false;
            $("#MicBtn").prop('disabled', false);
            $("#MicBtn").html('<i class="bi bi-mic"></i>');
            $("#MicBtn").removeClass('btn-loading btn-active');
            $("#Oval").attr("hidden", false);
            $("#SiriWave").attr("hidden", true);
            hideKeyboardHint();
            alert('Voice recognition error: ' + event.error);
        };

        recognition.onresult = function(event) {
            var transcript = event.results[0][0].transcript;
            console.log('Recognized:', transcript);
            // Show Siri wave animation for voice commands
            $("#Oval").attr("hidden", true);
            $("#SiriWave").attr("hidden", false);
            // Send recognized text to backend and speak/display response
            processTextCommandFetch(transcript)
                .then(response => {
                    if (response && response.response) {
                        $("#assistantResponse").text(response.response); // Display response
                        speakText(response.response); // Speak response
                    }
                    $("#Oval").attr("hidden", false);
                    $("#SiriWave").attr("hidden", true);
                })
                .catch(err => {
                    speakText('Sorry, there was an error processing your command.');
                    $("#Oval").attr("hidden", false);
                    $("#SiriWave").attr("hidden", true);
                });
        };
    }

    // Microphone button functionality (toggle voice assistant)
    $("#MicBtn").click(function() {
        if (!window.SpeechRecognition) {
            alert('Your browser does not support speech recognition.');
            return;
        }
        if (!voiceAssistantActive && !recognizing) {
            // Start browser-based voice recognition
            recognition.start();
        } else if (recognizing) {
            recognition.stop();
        }
    });

    function showKeyboardHint() {
        // Add keyboard shortcut hint
        if (!$("#keyboardHint").length) {
            $("body").append('<div id="keyboardHint" class="alert alert-info position-fixed" style="top: 20px; right: 20px; z-index: 1000; max-width: 300px;"><i class="bi bi-keyboard"></i> <strong>Keyboard Shortcuts:</strong><br><small>• Press <kbd>Esc</kbd> to stop voice assistant<br>• Press <kbd>Ctrl+Shift+M</kbd> to toggle</small></div>');
        }
        $("#keyboardHint").show();
    }

    function hideKeyboardHint() {
        $("#keyboardHint").hide();
    }

    // Text input functionality
    $("#chatbox").keypress(function(e) {
        if (e.which == 13) { // Enter key pressed
            var textCommand = $(this).val().trim();
            console.log("Text command submitted:", textCommand);
            if (textCommand) {
                $("#Oval").attr("hidden", true);
                $("#SiriWave").attr("hidden", false);
                processTextCommandFetch(textCommand)
                    .then(response => {
                        if (response && response.response) {
                            $("#assistantResponse").text(response.response);
                            speakText(response.response);
                        }
                        $("#Oval").attr("hidden", false);
                        $("#SiriWave").attr("hidden", true);
                    })
                    .catch(() => {
                        speakText('Sorry, there was an error processing your command.');
                        $("#Oval").attr("hidden", false);
                        $("#SiriWave").attr("hidden", true);
                    });
                $(this).val('');
            }
        }
    });

    // Send button for text input (if you want to add one)
    $("#ChatBtn").click(function() {
        var textCommand = $("#chatbox").val().trim();
        console.log("Text command submitted:", textCommand);
        if (textCommand) {
            $("#Oval").attr("hidden", true);
            $("#SiriWave").attr("hidden", false);
            processTextCommandFetch(textCommand)
                .then(response => {
                    if (response && response.response) {
                        $("#assistantResponse").text(response.response);
                        speakText(response.response);
                    }
                    $("#Oval").attr("hidden", false);
                    $("#SiriWave").attr("hidden", true);
                })
                .catch(() => {
                    speakText('Sorry, there was an error processing your command.');
                    $("#Oval").attr("hidden", false);
                    $("#SiriWave").attr("hidden", true);
                });
            $("#chatbox").val('');
        }
    });

    // Test button functionality
    $("#TestBtn").click(function() {
        console.log("Testing basic commands...");
        $(this).prop('disabled', true);
        $(this).html('<i class="bi bi-hourglass-split"></i> Testing...');
        
        testCommandFetch().then(result => {
            console.log("Test result:", result);
            $("#TestBtn").prop('disabled', false);
            $("#TestBtn").html('<i class="bi bi-play-circle"></i> Test Commands');
            
            if (result === "Test successful") {
                alert("✅ Basic command processing is working! Try voice or text commands now.");
            } else {
                alert("❌ Test failed. There might be an issue with the system.");
            }
        });
    });

    // Function to process text commands
    function processTextCommand(command) {
        console.log("Processing text command: " + command);
        // eel.DisplayMessage("Processing: " + command); // REMOVED to fix error
        // Call the Python function to process text commands
        eel.processTextCommand(command)()
            .then(function() {
                // After processing, reset UI to show hood (circle)
                $("#Oval").attr("hidden", false);
                $("#SiriWave").attr("hidden", true);
            })
            .catch(function(err) {
                console.error("Eel error:", err);
                $("#Oval").attr("hidden", false);
                $("#SiriWave").attr("hidden", true);
            });
    }

    // Wake Word Toggle
    $("#ToggleWakeWordBtn").click(function() {
        eel.toggle_wake_word()(function(result) {
            if (result.wake_word_enabled) {
                $("#ToggleWakeWordBtn").html('<i class="bi bi-mic"></i> Wake Word: ON');
                $("#ToggleWakeWordBtn").removeClass("btn-outline-secondary").addClass("btn-outline-info");
            } else {
                $("#ToggleWakeWordBtn").html('<i class="bi bi-mic-mute"></i> Wake Word: OFF');
                $("#ToggleWakeWordBtn").removeClass("btn-outline-info").addClass("btn-outline-secondary");
            }
        });
    });

    // Replace eel.takeCommand() with fetch
    function takeCommandFetch() {
        return fetch('/api/takeCommand', {method: 'POST'})
            .then(res => res.json())
            .then(data => data.result);
    }

    // Replace eel.processTextCommand(command)() with fetch
    function processTextCommandFetch(command) {
        return fetch('/api/processTextCommand', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({query: command})
        });
    }

    // Replace eel.test_command()(function(result) {...}) with fetch
    function testCommandFetch() {
        return fetch('/api/test_command')
            .then(res => res.json())
            .then(data => data.result);
    }

    // Replace eel.set_voice_language(lang_code) with fetch
    function setVoiceLanguageFetch(lang_code) {
        return fetch('/api/set_voice_language', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({lang_code: lang_code})
        });
    }

    // Helper: Speak text using browser TTS
    function speakText(text) {
        if ('speechSynthesis' in window) {
            var utterance = new SpeechSynthesisUtterance(text);
            utterance.lang = 'en-US';
            window.speechSynthesis.speak(utterance);
        }
    }

    // Minimal Voice Assistant UI logic
    const micBtn = document.getElementById('mic');
    const assistantResponseDiv = document.getElementById('assistantResponse');

    window.SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition || null;
    if (window.SpeechRecognition && micBtn) {
        recognition = new window.SpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = 'en-US';

        recognition.onstart = function() {
            recognizing = true;
            micBtn.textContent = '🛑';
            assistantResponseDiv.textContent = 'Listening...';
        };
        recognition.onend = function() {
            recognizing = false;
            micBtn.textContent = '🎤';
        };
        recognition.onerror = function(e) {
            assistantResponseDiv.textContent = 'Error: ' + e.error;
            micBtn.textContent = '🎤';
        };
        recognition.onresult = function(e) {
            const transcript = e.results[0][0].transcript;
            assistantResponseDiv.textContent = 'You said: ' + transcript;
            // Send to backend and speak response
            processTextCommandFetch(transcript)
                .then(response => {
                    if (response && response.response) {
                        assistantResponseDiv.textContent = response.response;
                        speakText(response.response);
                    }
                })
                .catch(() => {
                    assistantResponseDiv.textContent = 'Sorry, there was an error processing your command.';
                    speakText('Sorry, there was an error processing your command.');
                });
        };
        micBtn.onclick = function() {
            if (!recognizing) recognition.start();
            else recognition.stop();
        };
    } else if (micBtn) {
        assistantResponseDiv.textContent = 'Your browser does not support speech recognition.';
        micBtn.style.display = 'none';
    }
});