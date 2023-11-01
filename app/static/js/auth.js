$(document).ready(function() {
    
    function handleAccessToken(token, saveToSession=false) {
        console.log('token', token);
        if (token) {
            $('body').addClass('logged-in');

            $.ajaxSetup({
                headers: { 'Authorization': `Bearer ${token}` }
            });

            // save to browser session
            sessionStorage.setItem("access_token", token);
        }
    }

    // Check for an access token in the browser session
    handleAccessToken(sessionStorage.getItem("access_token"));

    $('#logout').click(function(evt) {
        // Lazy logout
        sessionStorage.removeItem("access_token");
        $('body').removeClass('logged-in');
    });

    // TODO: generalize these submit handlers
    $('#form-register').submit(function(evt) {
        const $form = $(this);

        evt.preventDefault();

        var postUrl = $form.attr("action");
        $form.find('button[type="submit"]').prop('disabled', true);

        // Serialize form data for the post request
        var data = $form.serializeObject();

        $.ajax({
            type: "POST",
            url: postUrl,
            dataType: "json",
            contentType: "application/json; charset=utf-8",
            data: JSON.stringify(data),
            success: function(response) {
                handleAccessToken(response.access_token, true);
            }
        }).fail(function(jqXHR, textStatus, errorThrown) {
            // Handle error during the request
            let message = jqXHR.responseJSON && jqXHR.responseJSON.detail;
            if (!message) {
                message = errorThrown;
            }
            showError('Registration Error', message);
        }).always(function() {
            $form.find('button[type="submit"]').prop('disabled', false);
            $('#modal-register').modal('hide');
        });
    });

    $('#form-login').submit(function(evt) {
        const $form = $(this);

        evt.preventDefault();

        var postUrl = $form.attr("action");
        $form.find('button[type="submit"]').prop('disabled', true);

        // Serialize form data for the post request
        var data = $form.serializeObject();

        $.ajax({
            type: "POST",
            url: postUrl,
            dataType: "json",
            contentType: "application/json; charset=utf-8",
            data: JSON.stringify(data),
            success: function(response) {
                handleAccessToken(response.access_token, true);
            }
        }).fail(function(jqXHR, textStatus, errorThrown) {
            // Handle error during the request
            let message = jqXHR.responseJSON && jqXHR.responseJSON.detail;
            if (!message) {
                message = errorThrown;
            }
            showError('Login Error', message);
        }).always(function() {
            $form.find('button[type="submit"]').prop('disabled', false);
        });
    });
});