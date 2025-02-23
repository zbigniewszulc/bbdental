/*
    Ref https://docs.stripe.com/js
*/

var stripePublicKey = JSON.parse(document.getElementById("id_stripe_public_key").text);
var clientSecret = JSON.parse(document.getElementById("id_client_secret").text);
var stripe = Stripe(stripePublicKey);
var elements = stripe.elements();

var style = {
    base: {
        fontSize: '16px',
        color: '#32325d',
        fontFamily: '"Gantari", sans-serif',
        '::placeholder': {
            color: '#aab7c4'
        }
    },
    invalid: {
        color: '#fa755a',
        iconColor: '#fa755a'
    }
};

var card = elements.create('card', { style: style });
card.mount('#card-element');

// Validation errors handling 
card.addEventListener('change', function(event) {
    var displayError = document.getElementById('card-errors');
    if (event.error) {
        displayError.textContent = event.error.message;
    } else {
        displayError.textContent = '';
    }
});


// Form submission handling
var form = document.getElementById('checkout-form');
form.addEventListener('submit', function(event) {
    event.preventDefault();
    card.update({'disabled': true});
    $('#submit_checkout').attr('disabled', true);
    $('#loading-overlay').removeClass('d-none');
    stripe.confirmCardPayment(clientSecret, {
        payment_method: {
            card: card,
            billing_details: {
                name: $.trim(form.name.value) + " + " + $.trim(form.surname.value),
                email: $.trim(form.email.value),
                phone: $.trim(form.phone_number.value),
                address: {
                    line1: $.trim(form.address_line_1.value),
                    line2: $.trim(form.address_line_2.value),
                    city: $.trim(form.town.value),
                    postal_code: $.trim(form.postcode.value),
                    country: $.trim(form.country.value)
                }
            }
        },
        shipping: {
            name: $.trim(form.name.value) + " + " + $.trim(form.surname.value),
            phone: $.trim(form.phone_number.value),
            address: {
                line1: $.trim(form.address_line_1.value),
                line2: $.trim(form.address_line_2.value),
                city: $.trim(form.town.value),
                postal_code: $.trim(form.postcode.value),
                country: $.trim(form.country.value)
            }
        }
    }).then(function(result) {
        if (result.error) {
            document.getElementById('card-errors').textContent = result.error.message;
            $('#loading-overlay').addClass('d-none');
            card.update({'disabled': false});
            $('#submit_checkout').attr('disabled', false);
        } else {
            if (result.paymentIntent.status === 'succeeded') {
                form.submit();
            }
        }
    });
});
