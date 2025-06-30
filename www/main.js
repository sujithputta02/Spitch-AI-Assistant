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

    // Keyboard shortcuts
    $(document).keydown(function(e) {
        // Ctrl+Shift+M to toggle voice assistant
        if (e.ctrlKey && e.shiftKey && e.keyCode === 77) { // M key
            e.preventDefault();
            $("#MicBtn").click();
        }
        // Escape key to stop voice assistant
        if (e.keyCode === 27 && voiceAssistantActive) { // Escape key
            e.preventDefault();
            $("#MicBtn").click();
        }
    });

    // Microphone button functionality (toggle voice assistant)
    $("#MicBtn").click(function() {
        if (!voiceAssistantActive) {
            // Start voice assistant
            console.log("Starting voice assistant...");
            $(this).prop('disabled', true);
            $(this).html('<i class="bi bi-hourglass-split"></i>');
            $(this).addClass('btn-loading');
            
            eel.start_continuous_listening()(function(result) {
                console.log("Voice assistant result:", result);
                if (result.status === "started") {
                    voiceAssistantActive = true;
                    $("#MicBtn").prop('disabled', false);
                    $("#MicBtn").html('<i class="bi bi-mic-mute"></i>');
                    $("#MicBtn").attr('title', 'Stop Voice Assistant (Esc)');
                    $("#MicBtn").removeClass('btn-loading').addClass('btn-active');
                    
                    // Show Siri wave animation
                    $("#Oval").attr("hidden", true);
                    $("#SiriWave").attr("hidden", false);
                    eel.playClickSound();
                    
                    // Show keyboard shortcut hint
                    showKeyboardHint();
                } else {
                    $("#MicBtn").prop('disabled', false);
                    $("#MicBtn").html('<i class="bi bi-mic"></i>');
                    $("#MicBtn").removeClass('btn-loading');
                    alert("Error: " + result.message);
                }
            });
        } else {
            // Stop voice assistant
            console.log("Stopping voice assistant...");
            $(this).prop('disabled', true);
            $(this).html('<i class="bi bi-hourglass-split"></i>');
            $(this).addClass('btn-loading');
            
            eel.stop_continuous_listening()(function(result) {
                console.log("Stop result:", result);
                voiceAssistantActive = false;
                $("#MicBtn").prop('disabled', false);
                $("#MicBtn").html('<i class="bi bi-mic"></i>');
                $("#MicBtn").attr('title', 'Start Voice Assistant (Ctrl+Shift+M)');
                $("#MicBtn").removeClass('btn-loading btn-active');
                $("#listeningStatus").hide();
                
                // Hide Siri wave animation
                $("#Oval").attr("hidden", false);
                $("#SiriWave").attr("hidden", true);
                
                // Hide keyboard hint
                hideKeyboardHint();
            });
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

    // Check initial listening status
    eel.get_listening_status()(function(result) {
        if (result.listening) {
            voiceAssistantActive = true;
            $("#MicBtn").html('<i class="bi bi-mic-mute"></i>');
            $("#MicBtn").attr('title', 'Stop Voice Assistant (Esc)');
            $("#MicBtn").addClass('btn-active');
            $("#Oval").attr("hidden", true);
            $("#SiriWave").attr("hidden", false);
            $("#listeningStatus").hide(); // Explicitly hide status bar on init
            showKeyboardHint();
        }
    });

    // Text input functionality
    $("#chatbox").keypress(function(e) {
        if (e.which == 13) { // Enter key pressed
            var textCommand = $(this).val().trim();
            console.log("Text command submitted:", textCommand);
            if (textCommand) {
                // Show Siri wave animation for text commands
                $("#Oval").attr("hidden", true);
                $("#SiriWave").attr("hidden", false);
                processTextCommand(textCommand);
                $(this).val(''); // Clear the input field
            }
        }
    });

    // Send button for text input (if you want to add one)
    $("#ChatBtn").click(function() {
        var textCommand = $("#chatbox").val().trim();
        console.log("Text command submitted:", textCommand);
        if (textCommand) {
            // Show Siri wave animation for text commands
            $("#Oval").attr("hidden", true);
            $("#SiriWave").attr("hidden", false);
            processTextCommand(textCommand);
            $("#chatbox").val(''); // Clear the input field
        }
    });

    // Test button functionality
    $("#TestBtn").click(function() {
        console.log("Testing basic commands...");
        $(this).prop('disabled', true);
        $(this).html('<i class="bi bi-hourglass-split"></i> Testing...');
        
        eel.test_command()(function(result) {
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

    eel.expose(force_stop_listening_ui);
    function force_stop_listening_ui() {
        console.log("Forcing UI stop from Python.");
        voiceAssistantActive = false;
        $("#MicBtn").prop('disabled', false);
        $("#MicBtn").html('<i class="bi bi-mic"></i>');
        $("#MicBtn").attr('title', 'Start Voice Assistant (Ctrl+Shift+M)');
        $("#MicBtn").removeClass('btn-loading btn-active');
        
        // Hide wave and show circle
        $("#Oval").attr("hidden", false);
        $("#SiriWave").attr("hidden", true);
        $("#listeningStatus").hide();
        
        // Hide keyboard hint
        hideKeyboardHint();
    }
});