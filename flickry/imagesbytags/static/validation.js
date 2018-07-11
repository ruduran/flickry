function validateForm(input, alert_elem) {
    var tag_list = $('#' + input).val();
    if (tag_list === '') {
        $('#' + alert_elem).show();
        $('#' + alert_elem).delay(3000).fadeOut('slow');
        return false;
    } else {
        return true;
    }
}
