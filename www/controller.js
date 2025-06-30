$(document).ready(function () {
    // Display Speak Message
    eel.expose(DisplayMessage)
    function DisplayMessage(message) {
        $(".siri-message li:first").text(message);
        $('.siri-message').textillate('start');

        // Also update the status if it's a listening message
        if (message.includes("Listening")) {
            $("#listeningStatus").show();
            $("#listeningStatus").removeClass("alert-info").addClass("alert-success");
            $("#listeningStatus").html('<i class="bi bi-mic-fill"></i> <strong>Voice Assistant Active</strong><br><small>Say "stop" to stop me</small>');
        }
    }

    // Display hood
    eel.expose(ShowHood)
    function ShowHood() {
        $("#Oval").attr("hidden", false);
        $("#SiriWave").attr("hidden", true);
    }
    
    // Update voice assistant status
    eel.expose(UpdateVoiceAssistantStatus)
    function UpdateVoiceAssistantStatus(isActive) {
        if (isActive) {
            $("#listeningStatus").show();
            $("#listeningStatus").removeClass("alert-info").addClass("alert-success");
            $("#listeningStatus").html('<i class="bi bi-mic-fill"></i> <strong>Voice Assistant Active</strong><br><small>Say "stop" to stop me</small>');
        } else {
            $("#listeningStatus").hide();
        }
    }
});