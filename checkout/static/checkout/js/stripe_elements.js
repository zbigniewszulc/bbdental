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

var card = elements.create('card', {
    style: style,
    hidePostalCode: true // use the postcode from the checkout form
});

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

// Show or hide billing address fields
var sameBillingAddress = document.getElementById('sameBillingAddress');
var billingAddressFields = document.getElementById(
    'billing-address-fields'
);
var requiredBillingFields = billingAddressFields.querySelectorAll(
    '[data-billing-required]'
);

function updateBillingAddressFields() {
    var useDeliveryAddress = sameBillingAddress.checked;

    billingAddressFields.classList.toggle(
        'd-none',
        useDeliveryAddress
    );

    requiredBillingFields.forEach(function(field) {
        field.required = !useDeliveryAddress;
    });
}

sameBillingAddress.addEventListener(
    'change',
    updateBillingAddressFields
);

updateBillingAddressFields();

// a function that handles the form submission
form.addEventListener('submit', function(event) {
    event.preventDefault();
    var billingAddress;

    if (sameBillingAddress.checked) {
        billingAddress = {
            line1: $.trim(form.address_line_1.value),
            line2: $.trim(form.address_line_2.value),
            city: $.trim(form.town.value),
            postal_code: $.trim(form.postcode.value),
            country: $.trim(form.country.value)
        };
    } else {
        billingAddress = {
            line1: $.trim(form.billing_address_line_1.value),
            line2: $.trim(form.billing_address_line_2.value),
            city: $.trim(form.billing_town.value),
            postal_code: $.trim(form.billing_postcode.value),
            country: $.trim(form.billing_country.value)
        };
    }
    card.update({'disabled': true});
    $('#submit_checkout').attr('disabled', true);
    $('#loading-overlay').removeClass('d-none');
    // Save checkout data before confirming the payment
    var postData = {
        csrfmiddlewaretoken: form.querySelector(
            '[name="csrfmiddlewaretoken"]'
        ).value,
        client_secret: clientSecret,
        save_profile: document.getElementById(
            'saveProfile'
        ).checked.toString(),
        name: $.trim(form.name.value),
        surname: $.trim(form.surname.value),
        email: $.trim(form.email.value),
        phone_number: $.trim(form.phone_number.value),
        address_line_1: $.trim(form.address_line_1.value),
        address_line_2: $.trim(form.address_line_2.value),
        town: $.trim(form.town.value),
        postcode: $.trim(form.postcode.value),
        country: $.trim(form.country.value)
    };
    $.post(form.dataset.cacheUrl, postData)
        .done(function() {
            stripe.confirmCardPayment(clientSecret, {
                payment_method: {
                    card: card,
                    billing_details: {
                        name: $.trim(form.name.value) + " " + $.trim(form.surname.value),
                        email: $.trim(form.email.value),
                        phone: $.trim(form.phone_number.value),
                        address: billingAddress
                    }
                },
                shipping: {
                    name: $.trim(form.name.value) + " " + $.trim(form.surname.value),
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
                        document.getElementById('stripe-pid').value =
                            result.paymentIntent.id;
                        form.submit();
                    }
                }
            });
        })
        .fail(function(response) {
            var errorMessage = response.responseText;

            if (!errorMessage) {
                errorMessage =
                    'There was a problem preparing your payment. Please try again.';
            }

            document.getElementById('card-errors').textContent = errorMessage;
            $('#loading-overlay').addClass('d-none');
            card.update({'disabled': false});
            $('#submit_checkout').attr('disabled', false);
        });
});
