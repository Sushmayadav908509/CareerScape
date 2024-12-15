const profileTypeSelect = document.getElementById('id_profile_type');
const companyNameField = document.getElementById('company_name_field');
const companyNameInput = document.getElementsByClassName('company_name');


profileTypeSelect.addEventListener('change', function () {
    if (profileTypeSelect.value === 'recruiter') {
        companyNameField.style.display = 'block';
        for (let input of companyNameInput) {
            input.setAttribute('required', 'required')
        }
    } else {
        companyNameField.style.display = 'none';
        for (let input of companyNameInput) {
            input.removeAttribute('required');
        }
    }
});

if (profileTypeSelect.value === 'recruiter') {
    for (let input of companyNameInput) {
        input.setAttribute('required', 'required');
    }
}