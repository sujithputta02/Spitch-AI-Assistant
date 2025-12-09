// Create a simple DisplayMessage function for compatibility
function DisplayMessage(message) {
    console.log("[DisplayMessage]", message);
    // You can add UI updates here if needed
}

$(document).ready(function () {
    console.log("🚀 jQuery document ready fired");
    console.log("📝 Chatbox element found:", $("#chatbox").length > 0);
    console.log("🔘 ChatBtn element found:", $("#ChatBtn").length > 0);
    console.log("🎤 MicBtn element found:", $("#MicBtn").length > 0);

    // Prevent Bootstrap from auto-initializing offcanvas on ChatBtn
    $("#ChatBtn").removeAttr('data-bs-toggle data-bs-target aria-controls');

    // Remove any Bootstrap event listeners that might be attached
    $("#ChatBtn").off('click.bs.offcanvas');

    // Override Bootstrap offcanvas initialization to prevent errors
    if (typeof bootstrap !== 'undefined' && bootstrap.Offcanvas) {
        const originalOffcanvas = bootstrap.Offcanvas;
        bootstrap.Offcanvas = function (element, config) {
            // Check if element exists and has required structure
            if (!element || !element.parentNode) {
                console.warn("Prevented Bootstrap Offcanvas initialization on invalid element");
                return {
                    show: function () { },
                    hide: function () { },
                    toggle: function () { },
                    dispose: function () { }
                };
            }
            return new originalOffcanvas(element, config);
        };
        // Copy static methods
        Object.setPrototypeOf(bootstrap.Offcanvas, originalOffcanvas);
        Object.assign(bootstrap.Offcanvas, originalOffcanvas);
    }

    // Additional safeguard: prevent any Bootstrap component initialization on ChatBtn
    $(document).off('click.bs.offcanvas.data-api', '#ChatBtn');

    // Ensure ChatBtn is completely clean of Bootstrap attributes
    setTimeout(function () {
        $("#ChatBtn").removeAttr('data-bs-toggle data-bs-target aria-controls data-bs-whatever');
        console.log("ChatBtn cleaned of Bootstrap attributes");
    }, 100);

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


    // Initialize SiriWave only if container exists
    var siriWave = null;
    var siriContainer = document.getElementById("siri-container");
    if (siriContainer) {
        try {
            siriWave = new SiriWave({
                container: siriContainer,
                width: 800,
                height: 200,
                style: "ios9",
                amplitude: "1",
                speed: "0.30",
                autostart: true
            });
            console.log("SiriWave initialized successfully");
        } catch (error) {
            console.error("Error initializing SiriWave:", error);
        }
    } else {
        console.log("siri-container not found, skipping SiriWave initialization");
    }

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
    $(document).keydown(function (e) {
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

    // Add a modal for voice command confirmation
    $('body').append(`
      <div id="voiceConfirmModal" class="modal" tabindex="-1" style="display:none;position:fixed;z-index:2000;left:0;top:0;width:100vw;height:100vh;background:rgba(0,0,0,0.4);align-items:center;justify-content:center;">
        <div style="background:#232b3a;padding:24px 18px;border-radius:12px;max-width:90vw;width:400px;box-shadow:0 4px 32px #0008;">
          <h5 style="color:#fff;">Confirm or Edit Command</h5>
          <input id="voiceConfirmInput" type="text" style="width:100%;margin:12px 0 18px 0;padding:10px 12px;border-radius:8px;border:none;font-size:1.1rem;" />
          <div style="display:flex;gap:12px;justify-content:flex-end;">
            <button id="voiceConfirmCancel" class="btn btn-secondary btn-sm">Cancel</button>
            <button id="voiceConfirmOk" class="btn btn-primary btn-sm">OK</button>
          </div>
        </div>
      </div>
    `);

    // Helper to show the confirmation modal
    function showVoiceConfirmModal(recognizedText, onConfirm) {
        $('#voiceConfirmInput').val(recognizedText);
        $('#voiceConfirmModal').fadeIn(120);
        $('#voiceConfirmInput').focus();
        $('#voiceConfirmOk').off('click').on('click', function () {
            const confirmed = $('#voiceConfirmInput').val().trim();
            $('#voiceConfirmModal').fadeOut(120);
            if (confirmed) onConfirm(confirmed);
        });
        $('#voiceConfirmCancel').off('click').on('click', function () {
            $('#voiceConfirmModal').fadeOut(120);
        });
    }

    // Microphone button functionality (toggle voice assistant)
    $("#MicBtn").off('click').on('click', function () {
        if (!voiceAssistantActive) {
            // Start voice assistant
            console.log("Starting voice assistant...");
            $(this).prop('disabled', true);
            $(this).html('<i class="bi bi-hourglass-split"></i>');
            $(this).addClass('btn-loading');

            // Set flag
            voiceAssistantActive = true;

            // Call Python to start listening
            eel.start_continuous_listening()(function (response) {
                console.log("Start response:", response);
                $("#MicBtn").prop('disabled', false);
                $("#MicBtn").html('<i class="bi bi-mic-fill" style="color: #ff4444;"></i>'); // Active state
                $("#MicBtn").attr('title', 'Stop Voice Assistant (Esc)');
                $("#MicBtn").removeClass('btn-loading');
                $("#MicBtn").addClass('btn-active');

                // Show listening status
                $("#listeningStatus").show();
                $("#listeningStatus").removeClass("alert-info").addClass("alert-success");
                $("#listeningStatus").html('<i class="bi bi-mic-fill"></i> <strong>Voice Assistant Active</strong><br><small>Say "stop" to stop me</small>');

                // Show Siri wave animation
                $("#Oval").attr("hidden", true);
                $("#SiriWave").attr("hidden", false);

                // Hide any previous response
                $("#siriResponse").hide();

                // Show keyboard hint
                showKeyboardHint();
            });
            return;
        } else {
            // Stop voice assistant
            console.log("Voice assistant stop requested");
            voiceAssistantActive = false;

            // Call Python to stop listening
            eel.stop_continuous_listening()(function (response) {
                console.log("Stop response:", response);

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
    console.log("Voice assistant status check...");

    // Text input functionality - Enhanced Enter key handler
    console.log("⌨️ Setting up text input handler...");
    $("#chatbox").off('keypress').on('keypress', function (e) {
        if (e.which == 13) { // Enter key pressed
            e.preventDefault(); // Prevent default form submission
            var textCommand = $(this).val().trim();
            console.log("⏎ Enter key pressed - Command:", textCommand);

            if (textCommand) {
                console.log("🎯 Processing command via Enter key:", textCommand);
                processTextCommand(textCommand);
                $(this).val(''); // Clear the input field
            } else {
                console.log("⚠️ Empty command, showing hint");
                // Briefly highlight the input to show it's active
                $(this).css('border', '2px solid #ffc107');
                setTimeout(() => {
                    $(this).css('border', '');
                }, 1000);
            }
            return false; // Prevent any further event handling
        }
    });

    // Also handle keydown for better responsiveness
    $("#chatbox").off('keydown').on('keydown', function (e) {
        if (e.which == 13) { // Enter key
            e.preventDefault();
            return false;
        }
    });

    // Chat button (arrow) click handler - Enhanced with visual feedback
    $("#ChatBtn").off().on('click', function (e) {
        e.preventDefault(); // Prevent any default behavior
        e.stopPropagation(); // Stop event bubbling
        e.stopImmediatePropagation(); // Stop all other handlers

        var textCommand = $("#chatbox").val().trim();
        console.log("🔘 Chat button (arrow) clicked - Command:", textCommand);

        if (textCommand) {
            console.log("🎯 Processing command via button:", textCommand);

            // Visual feedback - button press animation
            $(this).addClass('btn-pressed');
            setTimeout(() => {
                $(this).removeClass('btn-pressed');
            }, 150);

            processTextCommand(textCommand);
            $("#chatbox").val(''); // Clear the input field
        } else {
            console.log("⚠️ Empty command, showing hint");
            // Visual feedback for empty command
            $(this).addClass('btn-warning-flash');
            $("#chatbox").css('border', '2px solid #ffc107');
            setTimeout(() => {
                $(this).removeClass('btn-warning-flash');
                $("#chatbox").css('border', '');
                $("#chatbox").focus();
            }, 1000);
        }
        return false; // Prevent any further event handling
    });

    // Additional protection: Remove ChatBtn from Bootstrap's automatic component detection
    $("#ChatBtn").addClass('no-bootstrap-init');

    // Add custom styles for button feedback
    $('<style>').text(`
        .btn-pressed {
            transform: scale(0.95) !important;
            transition: transform 0.1s ease !important;
        }
        .btn-warning-flash {
            animation: warningFlash 0.5s ease-in-out !important;
        }
        @keyframes warningFlash {
            0%, 100% { background-color: transparent; }
            50% { background-color: rgba(255, 193, 7, 0.3); }
        }
        #outputArea {
            animation: slideInUp 0.3s ease-out;
        }
        @keyframes slideInUp {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        .glow-on-hover:hover {
            box-shadow: 0 0 10px rgba(0, 123, 255, 0.5) !important;
        }
        #siriResponse {
            animation: responseSlideIn 0.5s ease-out;
        }
        @keyframes responseSlideIn {
            from {
                opacity: 0;
                transform: translateY(30px) scale(0.95);
            }
            to {
                opacity: 1;
                transform: translateY(0) scale(1);
            }
        }
        .response-card {
            backdrop-filter: blur(10px);
            transition: all 0.3s ease;
        }
        .response-card:hover {
            box-shadow: 0 6px 25px rgba(74, 144, 226, 0.4) !important;
            transform: translateY(-2px);
        }
        .processing-dots {
            display: flex;
            justify-content: center;
            gap: 8px;
        }
        .processing-dots .dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background-color: #4a90e2;
            animation: dotPulse 1.4s infinite ease-in-out;
        }
        .processing-dots .dot:nth-child(1) { animation-delay: -0.32s; }
        .processing-dots .dot:nth-child(2) { animation-delay: -0.16s; }
        .processing-dots .dot:nth-child(3) { animation-delay: 0s; }
        @keyframes dotPulse {
            0%, 80%, 100% {
                transform: scale(0.8);
                opacity: 0.5;
            }
            40% {
                transform: scale(1.2);
                opacity: 1;
            }
        }
    `).appendTo('head');

    // Global error handler for Bootstrap offcanvas errors
    window.addEventListener('error', function (e) {
        if (e.message && e.message.includes('parentNode')) {
            console.warn('Bootstrap offcanvas error caught and handled:', e.message);
            e.preventDefault(); // Prevent the error from showing in console
            return true;
        }
    });

    // Test button functionality
    $("#TestBtn").click(function () {
        console.log("Testing basic commands...");
        $(this).prop('disabled', true);
        $(this).html('<i class="bi bi-hourglass-split"></i> Testing...');

        eel.test_command()(function (result) {
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

    // Add response display area within SiriWave section if it doesn't exist
    if (!$("#siriResponse").length) {
        $("#SiriWave .container .row .col-md-12 > div").append(`
            <div id="siriResponse" class="mt-4" style="display:none;">
                <div class="response-card" style="background: rgba(35, 43, 58, 0.95); border: 1px solid #4a90e2; border-radius: 15px; padding: 20px; margin-top: 30px; box-shadow: 0 4px 20px rgba(74, 144, 226, 0.3);">
                    <div class="response-header text-center mb-3">
                        <i class="bi bi-chat-dots text-primary" style="font-size: 1.5rem;"></i>
                        <h6 class="text-light mt-2 mb-0">Spitch Response</h6>
                    </div>
                    <div id="responseText" class="text-light text-center" style="font-size: 1.2rem; line-height: 1.6; min-height: 60px;"></div>
                    <div class="text-center mt-3">
                        <button id="continueChat" class="btn btn-outline-primary btn-sm">
                            <i class="bi bi-arrow-left-circle"></i> Continue Chat
                        </button>
                    </div>
                </div>
            </div>
        `);

        // Continue chat handler
        $("#continueChat").click(function () {
            // Hide SiriWave and response, show main interface
            $("#SiriWave").attr("hidden", true);
            $("#Oval").attr("hidden", false);
            $("#chatbox").focus();
        });
    }

    // Image Upload Logic
    let currentImageBase64 = null;

    $("#AttachBtn").click(function () {
        $("#imageInput").click();
    });

    $("#imageInput").change(function (e) {
        const file = e.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function (e) {
                currentImageBase64 = e.target.result; // Base64 string
                $("#imagePreview").attr("src", currentImageBase64);
                $("#imagePreviewContainer").fadeIn();
                $("#chatbox").focus();
            };
            reader.readAsDataURL(file);
        }
    });

    $("#removeImageBtn").click(function () {
        currentImageBase64 = null;
        $("#imageInput").val(""); // Reset input
        $("#imagePreview").attr("src", "");
        $("#imagePreviewContainer").hide();
    });

    // Function to process text commands (with optional image)
    function processTextCommand(command) {
        console.log("🚀 processTextCommand called with: " + command);
        console.log("📸 Image attached:", currentImageBase64 ? "Yes" : "No");

        // Show loading state
        $("#chatbox").attr("placeholder", "🤖 Processing your command...");
        $("#chatbox").prop("disabled", true);

        // Hide preview immediately to clean up UI
        if (currentImageBase64) {
            $("#imagePreviewContainer").hide();
        }

        // Show Siri wave animation immediately
        $("#Oval").attr("hidden", true);
        $("#SiriWave").attr("hidden", false);

        // Hide any previous response
        $("#siriResponse").hide();

        // Add processing indicator within SiriWave
        if (!$("#processingIndicator").length) {
            $("#SiriWave .container .row .col-md-12 > div").append(`
                <div id="processingIndicator" class="text-center mt-4" style="display:none;">
                    <div class="processing-animation">
                        <div class="spinner-border text-primary" role="status" style="width: 2.5rem; height: 2.5rem;">
                            <span class="visually-hidden">Loading...</span>
                        </div>
                        <p class="text-light mt-3" style="font-size: 1.1rem;">Processing...</p>
                    </div>
                </div>
            `);
        }
        $("#processingIndicator").show();

        // Use Eel for Flask/Eel app
        console.log("📡 Making eel request to processTextCommand");

        // Pass image data if available
        const imageData = currentImageBase64;

        eel.processTextCommand(command, imageData)(function (response) {
            console.log("✅ Command processed successfully:", response);

            // Cleanup image state after sending
            currentImageBase64 = null;
            $("#imageInput").val("");

            // Reset input state
            $("#chatbox").attr("placeholder", "Type your command here and press Enter...");
            $("#chatbox").prop("disabled", false);

            // Hide processing indicator
            $("#processingIndicator").hide();

            // Display the response within SiriWave section
            if (response && response.trim()) {
                $("#responseText").html(response.replace(/\n/g, '<br>'));
                $("#siriResponse").fadeIn(400);
            } else {
                // Show a generic success message if no response
                $("#responseText").html("Command executed successfully!");
                $("#siriResponse").fadeIn(400);
            }

            // Return focus to input after a short delay
            setTimeout(function () {
                $("#chatbox").focus();
            }, 1000);

            console.log("🎉 Command processing complete");
        });
    }

    // Wake Word Toggle
    $("#ToggleWakeWordBtn").click(function () {
        eel.toggle_wake_word()(function (response) {
            console.log("Wake word toggle:", response);
        });
    });

    // Force stop listening UI function - called from Python
    eel.expose(force_stop_listening_ui);
    function force_stop_listening_ui() {
        console.log("Force stop UI called from Python");
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

    // PWA Install Button Logic
    let deferredPrompt = null;
    window.addEventListener('beforeinstallprompt', (e) => {
        e.preventDefault();
        deferredPrompt = e;
        $('#installAppBtn').show();
    });
    $('#installAppBtn').on('click', function () {
        if (deferredPrompt) {
            deferredPrompt.prompt();
            deferredPrompt.userChoice.then((choiceResult) => {
                if (choiceResult.outcome === 'accepted') {
                    $('#installInstructions').hide();
                } else {
                    $('#installInstructions').text('You can always install Spitch later from your browser menu.').show();
                }
                deferredPrompt = null;
                $('#installAppBtn').hide();
            });
        } else {
            $('#installInstructions').html('To install Spitch as a desktop app, use your browser\'s menu: <br><b>Chrome/Edge:</b> ... > Install Spitch<br><b>Firefox:</b> Use the "Add to desktop" option.').show();
        }
    });
    // Hide instructions on click outside
    $(document).on('click', function (e) {
        if (!$(e.target).closest('#installAppBtn, #installInstructions').length) {
            $('#installInstructions').hide();
        }
    });
});

// Language Support
let supportedLanguages = {};
let currentLanguage = 'en-US';

// Load supported languages on page load
// Load supported languages on page load
function loadSupportedLanguages() {
    console.log("Loading languages via Eel...");
    eel.get_supported_languages()(function (languages) {
        if (!languages) {
            console.error("No languages received from backend");
            return;
        }
        supportedLanguages = languages;
        populateLanguageMenu();

        // Get current language
        eel.get_current_language()(function (lang) {
            console.log("Current language received:", lang);
            currentLanguage = lang || 'en-US';
            updateLanguageDisplay();
        });
    });
}

// Populate language dropdown menu
function populateLanguageMenu() {
    const languageMenu = $('#languageMenu');
    languageMenu.empty();

    Object.keys(supportedLanguages).forEach(langCode => {
        const language = supportedLanguages[langCode];
        const menuItem = $(`
                <li>
                    <a class="dropdown-item language-option" href="#" data-lang="${langCode}">
                        ${language.name}
                    </a>
                </li>
            `);
        languageMenu.append(menuItem);
    });

    // Add click handlers
    $('.language-option').click(function (e) {
        e.preventDefault();
        const selectedLang = $(this).data('lang');
        changeLanguage(selectedLang);
    });
}

// Change language
// Change language
function changeLanguage(langCode) {
    console.log('Changing language to:', langCode);

    eel.set_voice_language(langCode)(function (success) {
        if (success) {
            currentLanguage = langCode;
            updateLanguageDisplay();

            // Show success message
            const langName = supportedLanguages[langCode].name;
            console.log(`✅ Language changed to ${langName}`);

            // Update placeholder text based on language
            updatePlaceholderText(langCode);
        } else {
            alert('❌ Failed to change language');
        }
    });
}

// Update language display
function updateLanguageDisplay() {
    if (supportedLanguages[currentLanguage]) {
        $('#currentLanguage').text(supportedLanguages[currentLanguage].name);
    }
}

// Update placeholder text based on language
function updatePlaceholderText(langCode) {
    const placeholders = {
        'en-US': "Type your command here and press Enter... (e.g., 'what time is it', 'open notepad', 'tell me a joke')",
        'te-IN': "మీ కమాండ్ ఇక్కడ టైప్ చేసి Enter నొక్కండి... (ఉదా: 'సమయం ఎంత', 'నోట్‌ప్యాడ్ తెరవండి', 'జోక్ చెప్పండి')",
        'kn-IN': "ನಿಮ್ಮ ಆಜ್ಞೆಯನ್ನು ಇಲ್ಲಿ ಟೈಪ್ ಮಾಡಿ ಮತ್ತು Enter ಒತ್ತಿರಿ... (ಉದಾ: 'ಸಮಯ ಎಷ್ಟು', 'ನೋಟ್‌ಪ್ಯಾಡ್ ತೆರೆಯಿರಿ', 'ಜೋಕ್ ಹೇಳಿ')",
        'ml-IN': "നിങ്ങളുടെ കമാൻഡ് ഇവിടെ ടൈപ്പ് ചെയ്ത് Enter അമർത്തുക... (ഉദാ: 'സമയം എത്ര', 'നോട്ട്പാഡ് തുറക്കുക', 'തമാശ പറയുക')",
        'hi-IN': "अपना कमांड यहाँ टाइप करें और Enter दबाएं... (जैसे: 'समय क्या है', 'नोटपैड खोलें', 'जोक सुनाएं')"
    };

    const placeholder = placeholders[langCode] || placeholders['en-US'];
    $('#chatbox').attr('placeholder', placeholder);
}

// Initialize language support and Settings when page loads
$(document).ready(function () {
    loadSupportedLanguages();

    // --- Settings Modal Logic ---

    // Open Settings
    $("#SettingsBtn").click(function () {
        var myModal = new bootstrap.Modal(document.getElementById('settingsModal'));
        myModal.show();
        loadSettingsData();
    });

    // Load Settings Data
    function loadSettingsData() {
        console.log("Loading settings data...");

        // 1. Get Voices
        eel.get_voice_options()(function (voices) {
            const select = $("#voiceSelect");
            select.empty();
            voices.forEach(v => {
                select.append(new Option(v.name, v.id));
            });

            // 2. Get User Settings to set current state
            eel.get_all_settings()(function (settings) {
                console.log("Current settings:", settings);

                // Set Voice
                if (settings.voice_id) {
                    $("#voiceSelect").val(settings.voice_id);
                }

                // Set Rate
                if (settings.voice_rate) {
                    $("#rateRange").val(settings.voice_rate);
                    $("#rateValue").text(settings.voice_rate);
                }

                // Set Location
                if (settings.user_location) {
                    $("#locationInput").val(settings.user_location);
                }
            });
        });
    }

    // Rate Slider Update
    $("#rateRange").on('input', function () {
        $("#rateValue").text($(this).val());
    });

    // Save Settings
    $("#saveSettingsBtn").click(function () {
        const settings = {
            'voice_id': $("#voiceSelect").val(),
            'voice_rate': $("#rateRange").val(),
            'user_location': $("#locationInput").val()
        };

        console.log("Saving settings:", settings);
        $(this).html('<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Saving...');

        eel.save_all_settings(settings)(function (success) {
            if (success) {
                // Show success feedback
                $("#saveSettingsBtn").html('<i class="bi bi-check-circle"></i> Saved!');
                $("#saveSettingsBtn").removeClass("btn-primary").addClass("btn-success");

                setTimeout(() => {
                    // Reset button and close
                    $("#saveSettingsBtn").html('Save Changes');
                    $("#saveSettingsBtn").removeClass("btn-success").addClass("btn-primary");
                    var myModalEl = document.getElementById('settingsModal');
                    var modal = bootstrap.Modal.getInstance(myModalEl);
                    modal.hide();

                    // Optional: Speak test
                    eel.processTextCommand("Settings updated successfully.")(function () { });
                }, 1000);
            } else {
                alert("Failed to save settings.");
                $("#saveSettingsBtn").html('Save Changes');
            }
        });
    });
});