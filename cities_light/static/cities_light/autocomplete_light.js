$(document).ready(function() {
    $('.autocomplete_light_widget[data-bootstrap=countrycity]').each(function() {
        var country_wrapper = $(this).prev();
        var city_wrapper = $(this);

        country_wrapper.bind('deckready', function() {
            var city_deck = city_wrapper.yourlabs_deck();

            $(this).yourlabs_deck().valueSelect.bind('change', function() {
                city_deck.input.yourlabs_autocomplete().data['country__pk'] = $(this).val();
            });
        });
    });
});
