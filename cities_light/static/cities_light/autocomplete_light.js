$(document).ready(function() {
    // autocomplete widget javascript initialization for bootstrap=countrycity
    $('.autocomplete_light_widget[data-bootstrap=countrycity]').each(function() {
        var country_wrapper = $(this).prev();
        var city_wrapper = $(this);

        function setup() {
            // get the related country deck
            var country_deck = country_wrapper.yourlabs_deck();
            var country_select = country_deck.valueSelect;

            if (country_deck.payload.bootstrap == 'remote') {
                // instanciate a RemoteChannelDeck deck for this city
                var city_deck = city_wrapper.yourlabs_deck(RemoteChannelDeck);
            } else {
                // instanciate a deck for this city
                var city_deck = city_wrapper.yourlabs_deck();
            }

            // set country_pk in city autocomplete data when a country is selected
            country_select.bind('change', function() {
                city_deck.input.yourlabs_autocomplete().data['country__pk'] = $(this).val();
            });

            // set country_pk in city autocomplete data if a country is initially selected
            if (country_select.val())
                city_deck.input.yourlabs_autocomplete().data['country__pk'] = country_select.val();
        }

        // if the country deck is ready: setup the city deck, else wait for country deck to be ready
        country_wrapper.data('deckready', 0) ? setup() : country_wrapper.bind('deckready', setup);
    });
});
