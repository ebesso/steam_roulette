var stoping = false;
var itemSelected = 0;

jQuery(function ($) {
    var $owl = $('.owl-carousel');
    
    // Initialize Owl
    $('.owl-carousel').owlCarousel({
        center: true,
        loop: true,
        margin: 5,
        nav: false,
        mouseDrag: false,
        touchDrag: false,
        pullDrag: false,
        dots: false,
        responsive: {
            0: {
                items: 3
            },
            600: {
                items: 3
            },
            1000: {
                items: 7
            }
        }
    });

    // Click in button Jump
    $(document).on('data-run-script', function (event, winning_alternative) {
        stoping = false;
        itemSelected = winning_alternative;
        console.log(winning_alternative);

        $owl.trigger('play.owl.autoplay', [75]);
        setTimeout(stopAutoplay, 1000);
    });

    // Event changed Owl
    $owl.on('changed.owl.carousel', function (e) {
        if (stoping) {
            // Examine only if roulette stop
            var index = e.item.index + 2;
            var element = $(e.target).find(".owl-item").eq(index).find('.element-roulette');
            var item = element.data('item');

            if (item == itemSelected) {
                // If element equals to random, stop roulette
                $owl.trigger('stop.owl.autoplay');
                $('#js-btn-jump').html('Rolling');
                $('#js-btn-jump').removeAttr('disabled');

                $('.bet-table td').remove();

                $owl.trigger('next.owl.carousel', [750])
                $owl.trigger('next.owl.carousel', [1500])
            }
        }
    });
});

/**
 * Reduce speed roulette
 * @param {type} $owl
 * @param {type} speed
 * @returns {undefined}
 */
function slowSpeed($owl, speed) {
    $owl.trigger('play.owl.autoplay', [speed]);
}

/**
 * Stop autoplay roulette
 * @returns {undefined}
 */
function stopAutoplay() {
    stoping = true;
}