/*
    Ref https://docs.stripe.com/js
*/

const stripe_pubblic_key = JSON.parse(document.getElementById("id_stripe_public_key").text);
const client_secret = JSON.parse(document.getElementById("id_client_secret").text);
var stripe = Stripe(stripe_pubblic_key);
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
