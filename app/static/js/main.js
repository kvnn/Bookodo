let refreshLists;

// for serializing form data into JSON
$.fn.serializeObject = function() {
    var o = {};
    var a = this.serializeArray();
    $.each(a, function() {
        if (o[this.name]) {
            if (!o[this.name].push) {
                o[this.name] = [o[this.name]];
            }
            o[this.name].push(this.value || '');
        } else {
            o[this.name] = this.value || '';
        }
    });
    return o;
};

document.addEventListener('alpine:init', () => {
    Alpine.data('allBooks', () => ({
        books: [],
    }));
    Alpine.data('userLists', () => ({
        lists: [],
    }));
    Alpine.data('allLists', () => ({
        lists: [],
    }));
});

function showError(title, message) {
    console.error(title, message);
    $("#errorAlert .title").text(title);
    $("#errorAlert .message").text(message);
    $("#errorAlert").show();
}

$(document).ready(function() {
    // for serializing form data into JSON
    $.fn.serializeObject = function() {
        var o = {};
        var a = this.serializeArray();
        $.each(a, function() {
            if (o[this.name]) {
                if (!o[this.name].push) {
                    o[this.name] = [o[this.name]];
                }
                o[this.name].push(this.value || '');
            } else {
                o[this.name] = this.value || '';
            }
        });
        return o;
    };

    /*
    * ALERTS
    */
    $("#errorAlert .close").click(function(evt) {
        evt.preventDefault();
        $("#errorAlert").hide();
    });

    /*
    * BOOKS
    */
    $.get('/books', function(response) {
        let event = new CustomEvent("all-books-load", {
            detail: {
                books: response.books
            }
        });
        window.dispatchEvent(event);
        console.log('dispatched');
    }).catch(function(jqXHR, textStatus, errorThrown) {
        // Handle error during the request
        let message = jqXHR.responseJSON && jqXHR.responseJSON.detail;
        if (!message) {
            message = errorThrown;
        }
        showError('Error loading books', message);
    });

    $('#container-main').on('click', '.book-link', function(evt) {
        evt.preventDefault();
        // This is a Bootstrap modal button
        // Fill out the modal with the data from the button
        console.log($(this).data('modal-book-title'))
        $('#modal-book-id').data('id', $(this).data('modal-book-id'));
        $('#modal-book-title').text($(this).data('modal-book-title'));
        $('#modal-book-image_url').attr('src', $(this).data('modal-book-image_url'));
        $('#modal-book-isbn').text($(this).data('modal-book-isbn'));
        $('#modal-book-language').text($(this).data('modal-book-language'));
        $('#modal-book-pages').text($(this).data('modal-book-pages'));
        $('#modal-book-rating_average').text($(this).data('modal-book-rating_average'));
        $('#modal-book-rating_count').text($(this).data('modal-book-rating_count'));
        $('#modal-book-review_count').text($(this).data('modal-book-review_count'));

        $('#modal-book').modal('show');
    });

    /*
    * LISTS
    */
    refreshLists = function() {
        $.get('/lists', function(response) {
            let event = new CustomEvent("all-lists-load", {
                detail: {
                    lists: response.lists.all_lists
                }
            });
            window.dispatchEvent(event);

            console.log('user lists: response.user_lists', response.lists.user_lists)
            event = new CustomEvent("user-lists-load", {
                detail: {
                    lists: response.lists.user_lists
                }
            });
            window.dispatchEvent(event);

            console.log('dispatched');
        }).catch(function(jqXHR, textStatus, errorThrown) {
            // Handle error during the request
            let message = jqXHR.responseJSON && jqXHR.responseJSON.detail;
            if (!message) {
                message = errorThrown;
            }
            showError('Error loading lists', message);
        });
    }

    $('#container-main').on('click', '.list-generate-image', function(evt) {
        let $this = $(this);
        let listId = $(this).data('list-id');
        $this.addClass('spinner-border');

        $.ajax({
            type: "POST",
            url: '/lists/image',
            dataType: "json",
            contentType: "application/json; charset=utf-8",
            data: JSON.stringify({
                'list_id': listId
            }),
            success: function(response) {
                getGenerateListImageUpdates(
                    response.task_id,
                    listId
                );
            }
        }).fail(function(jqXHR, textStatus, errorThrown) {
            // Handle error during the request
            showError("List Image Generation Error", errorThrown);
            $this.removeClass('spinner-border');
            showError("List Image Generation Error", errorThrown);
        }).always(function() {
        });
    });

    // Refresh Lists upon page load
    refreshLists();

    // User actions
    $('#add-book-to-list').click(function(evt) {
        evt.stopPropagation();

        $('#add-book-to-list').prop('disabled', true);

        const new_list_title = $('#book-list-new').val();
        const existing_list_id = $('#book-list-existing').val();

        const data = {
            book_id: $('#modal-book-id').data('id')
        }

        if (new_list_title && new_list_title.length) {
            data['new_list_title'] = new_list_title;
        }

        if (existing_list_id) { // 0 is a valid list ID, but this will be a string
            data['existing_list_id'] = existing_list_id;
        }

        $.ajax({
            type: "POST",
            url: '/lists/book',
            dataType: "json",
            contentType: "application/json; charset=utf-8",
            data: JSON.stringify(data),
            success: function() {
                refreshLists();
                $('#modal-book').modal('hide');
            }
        }).fail(function(jqXHR, textStatus, errorThrown) {
            // Handle error during the request
            let message = jqXHR.responseJSON && jqXHR.responseJSON.detail;
            if (!message) {
                message = errorThrown;
            }
            showError('Error', message);
        }).always(function() {
            $('#add-book-to-list').prop('disabled', false);
        });
    });

    $('#form-create-list').submit(function(evt) {
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
            success: function() {
                refreshLists();
                $('#modal-create-list').modal('hide');
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
