$(document).ready(function() {
    $('.autocompleteselectwidget_light[data-bootstrap=countrycity]').each(function() {
        var country_wrapper = $(this).prev();
        var city_wrapper = $(this);

        country_wrapper.bind('yourlabs_deck.ready', function() {
            var city_deck = city_wrapper.yourlabs_deck();

            $(this).yourlabs_deck().options.valueSelect.bind('change', function() {
                city_deck.options.input.yourlabs_autocomplete().options.data['country__pk'] = $(this).val();
            });
        });
    });
});
