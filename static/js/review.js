$(function () {
    $('#commentField').on('keyup', function () {
        $('#commentFieldError').hide();
    });

    $('#submitReview').on('click', function () {

        var valid = false;
        var comment = document.getElementById('commentField');
        var rating = document.get
        if ($(comment).val() === undefined || $(comment).val() === null || $(comment).val().length === 0) {
            $('#commentFieldError').show();
        } else {
            valid = true;
        }

        if ($("input[name=rating]").val() === undefined || $("input[name=rating]").val() === null || $("input[name=rating]").val().length === 0) {
            $('#ratingFieldError').show();
        }

        if (valid) {
            $("form:first").submit();
        }
    });
});