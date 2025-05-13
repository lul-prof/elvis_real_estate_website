document.addEventListener('DOMContentLoaded', function() {
    // Auto-submit form when select fields change
    const autoSubmitFields = document.querySelectorAll('select[name="type"], select[name="bedrooms"], select[name="status"], select[name="sort"]');
    autoSubmitFields.forEach(field => {
        field.addEventListener('change', () => {
            document.getElementById('searchForm').submit();
        });
    });

    // Debounce function for price inputs
    let timeout = null;
    const priceInputs = document.querySelectorAll('input[name="min_price"], input[name="max_price"]');
    priceInputs.forEach(input => {
        input.addEventListener('input', () => {
            clearTimeout(timeout);
            timeout = setTimeout(() => {
                document.getElementById('searchForm').submit();
            }, 1000);
        });
    });

    // Initialize price range slider if using one
    if (typeof noUiSlider !== 'undefined') {
        const priceSlider = document.getElementById('price-range');
        noUiSlider.create(priceSlider, {
            start: [0, 1000000],
            connect: true,
            range: {
                'min': 0,
                'max': 1000000
            },
            format: {
                to: value => Math.round(value),
                from: value => value
            }
        });

        priceSlider.noUiSlider.on('change', values => {
            document.querySelector('input[name="min_price"]').value = values[0];
            document.querySelector('input[name="max_price"]').value = values[1];
            document.getElementById('searchForm').submit();
        });
    }
});