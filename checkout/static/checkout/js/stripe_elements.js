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
    card.update({'disabled': true})
    $('#submit_checkout').attr('disabled', true)
    stripe.confirmCardPayment(clientSecret, {
        payment_method: {
            card: card,
        }
    }).then(function(result) {
        if (result.error) {
            document.getElementById('card-errors').textContent = result.error.message;
            card.update({'disabled': false})
            $('#submit_checkout').attr('disabled', false)
        } else {
            if (result.paymentIntent.status === 'succeeded') {
                form.submit();
            }
        }
    });
});
