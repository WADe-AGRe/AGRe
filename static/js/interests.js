$(function () {
    var csrftoken = jQuery("[name=csrfmiddlewaretoken]").val();

    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }

    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });

    $('#goToHomePage').on('click', function () {
        window.location = '/';
    });

    $('.list-group.checked-list-box .list-group-item').each(function () {

        var $widget = $(this),
            $checkbox = $('<input type="checkbox" hidden />'),
            color = ($widget.data('color') ? $widget.data('color') : "primary"),
            style = ($widget.data('style') == "button" ? "btn-" : "list-group-item-"),
            settings = {
                on: {
                    icon: 'far fa-check-square'
                },
                off: {
                    icon: 'far fa-square-o'
                }
            };

        $widget.css('cursor', 'pointer')
        $widget.append($checkbox);

        $widget.on('click', function () {
            $checkbox.prop('checked', !$checkbox.is(':checked'));
            $checkbox.triggerHandler('change');
            updateDisplay();
        });
        $checkbox.on('change', function () {
            updateDisplay();
        });

        function updateDisplay() {
            var isChecked = $checkbox.is(':checked');

            $widget.data('state', (isChecked) ? "on" : "off");

            $widget.find('.state-icon')
                .removeClass()
                .addClass('state-icon ' + settings[$widget.data('state')].icon);

            if (isChecked) {
                $widget.addClass(style + color + ' active');
            } else {
                $widget.removeClass(style + color + ' active');
            }
        }

        function init() {
            if ($widget.data('checked') == true || $widget.data('val') === 'True') {
                $checkbox.prop('checked', !$checkbox.is(':checked'));
            }
            updateDisplay();
            if ($widget.find('.state-icon').length == 0) {
                $widget.prepend('<span class="state-icon ' + settings[$widget.data('state')].icon + '"></span>');
            }
        }

        init();
    });

    $('#get-checked-data').on('click', function (event) {
        event.preventDefault();
        var checkedItems = [], counter = 0;
        $("#check-list-box li.active").each(function (idx, li) {
            checkedItems.push($(li).val());
        });

        $.ajax({
            type: "POST",
            traditional: true,
            url: "",
            async: false,
            data: JSON.stringify({'ids': checkedItems}, null, '\t'),
            dataType: "json",
            error: function (data) {
                $('#largeModal').modal('show');
            }
        });

        $('#updateInfo').on('click', function () {
            event.preventDefault();
            var checkedItems = [], counter = 0;
            $("#check-list-box li.active").each(function (idx, li) {
                checkedItems.push($(li).val());
            });

            $.ajax({
                type: "POST",
                traditional: true,
                url: "",
                async: false,
                data: JSON.stringify({'ids': checkedItems}, null, '\t'),
                dataType: "json",
                error: function (data) {
                    $('#largeModal').modal('show');
                }
            });
        });
    });