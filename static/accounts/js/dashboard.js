document.addEventListener('DOMContentLoaded', function () {
const csrfToken = '{{ csrf_token }}';
const editButton = document.getElementById('editButton');

const email = document.getElementById('email_address');

const phone_number = document.getElementById('phone_number');
const phone_verifybutton = document.getElementById('phone_verify_button');
const phone_container = document.getElementById('phone_container');
const phone_otpInput = document.getElementById('phone_otp_input');
const phone_otpVerifyButton = document.getElementById('phone_otp_verify_button');
const phone_otp_container = document.getElementById('phone_otp_container');
const phone_otp_p = document.getElementById('phone_otp_p')
const phoneotpTimerElement = document.getElementById('phone_otp_timer')
const countryDropdown = document.getElementById('countryDropdown');

const profilePictureInput = document.getElementById('profilePictureInput');
const editProfilePictureButton = document.getElementById('editProfilePictureButton');
const profilePicture = document.querySelector('.profile-picture img')

const first_name = document.getElementById('first_name');
const last_name = document.getElementById('last_name');
const skills = document.getElementById('skills');
const education = document.getElementById('education');
const experience = document.getElementById('experience');

const deleteAccountButton = document.getElementById('deleteAccountButton');
const passwordInputContainer = document.getElementById('passwordInputContainer');
const passwordInput = document.getElementById('passwordInput');
const verifyPasswordButton = document.getElementById('verifyPasswordButton');

const overlay = document.getElementById('overlay');

function showToast(message) {
    var toast = document.getElementById("toastNotification");
    var toastMessage = document.getElementById("toastMessage");
    toastMessage.innerText = message;
    toast.classList.add("show");
    setTimeout(function () {
        toast.classList.remove("show");
    }, 3000);
}


function toggleEditSave() {
    if (editButton.textContent === 'Edit Profile') {
        editButton.textContent = 'Save Profile';

        phone_verifybutton.style.display = 'inline-block';
        countryDropdown.style.display = 'inline-block';
        editProfilePictureButton.style.display = 'inline-block';


        first_name.innerHTML = `<input type="text" value="${first_name.textContent}" name="first_name">`;
        last_name.innerHTML = `<input type="text" value="${last_name.textContent}" name="last_name">`;
        phone_number.innerHTML = `<input type="text" value="${phone_number.textContent}" name="new_phone">`;
        skills.innerHTML = `<input type="text" value="${skills.textContent}" name="skills">`;
        education.innerHTML = `<input type="text" value="${education.textContent}" name="education">`;
        experience.innerHTML = `<input type="text" value="${experience.textContent}" name="experience">`;

    } else {
        editButton.textContent = 'Edit Profile';

        const updatefirst_name = document.querySelector('input[name="first_name"]').value;
        const updatelast_name = document.querySelector('input[name="last_name"]').value;
        const updateSkills = document.querySelector('input[name="skills"]').value;
        const updateEducation = document.querySelector('input[name="education"]').value;
        const updateExperience = document.querySelector('input[name="experience"]').value;

        const selectedFile = profilePictureInput.files[0];

        const formData = new FormData();
        formData.append('first_name', updatefirst_name);
        formData.append('last_name', updatelast_name);
        formData.append('skills', updateSkills);
        formData.append('education', updateEducation);
        formData.append('experience', updateExperience);

        if (selectedFile) {
            formData.append('profile_picture', selectedFile);
        }

        fetch('/user_profile_edit/', {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': csrfToken,
                csrfmiddlewaretoken: '{{ csrf_token }}',
            },
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showToast("Profile Saved Successfully")

                    setTimeout(() => {
                        window.location.href = '/dashboard/'
                    }, 2000);
                } else {
                    showToast("Error Updating Profile")
                }
            });
    }
}

editButton.addEventListener('click', toggleEditSave)


editProfilePictureButton.addEventListener('click', () => {
    profilePictureInput.click();
});

profilePictureInput.addEventListener('change', (event) => {
    const selectedFile = event.target.files[0];
    if (selectedFile) {
        const reader = new FileReader();
        reader.onload = function (e) {
            profilePicture.src = e.target.result;
        };
        reader.readAsDataURL(selectedFile);
    }
});


deleteAccountButton.addEventListener('click', () => {
    deleteAccountButton.style.display = 'none';
    passwordInputContainer.style.display = 'block';
});


verifyPasswordButton.addEventListener('click', function (event) {

    event.preventDefault();

    const pwformData = new FormData(passwordVerificationForm);

    fetch("/verify_password/", {
        method: 'POST',
        body: pwformData,
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showToast(data.message)
                verifyPasswordButton.style.display = 'none';
                passwordInput.style.display = 'none';
                deleteAccountButton.style.display = 'block';
                deleteAccountButton.style.backgroundColor = 'red';
                deleteAccountButton.style.color = 'white';
            } else {
                showToast(data.message)
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
});


deleteAccountButton.addEventListener('click', () => {
    if (deleteAccountButton.style.backgroundColor === 'red') {
        fetch("/delete_account/")
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showToast(data.message)
                    setTimeout(function () {
                        window.location.href = "/register/";
                    }, 3000);
                } else {
                    showToast(data.message)
                }
            })
            .catch(error => {
                console.error('Error:', error);
            });
    }

})

let isResendOTPMode = false;

let phone_otpTimer;
let phone_otpCountdown = 60;

function startPhoneOTPTimer() {
    phone_otpCountdown = 60;
    phone_otpTimer = setInterval(updatePhoneOTPTimer, 1000);
    updatePhoneOTPTimer();
}

function updatePhoneOTPTimer() {
    if (phone_otpCountdown <= 0) {
        clearInterval(phone_otpTimer);
        phone_otpVerifyButton.textContent = 'Resend OTP';
        phoneotpTimerElement.textContent = '';
    } else {
        phone_otpVerifyButton.textContent = 'Verify OTP';
        phoneotpTimerElement.textContent = `(${phone_otpCountdown}s)`;
        phone_otpCountdown--;
    }
}


const countriesData = JSON.parse('{{ countries_data|escapejs|safe }}');
console.log(countriesData)

countriesData.forEach(country => {
    const option = document.createElement('option');
    option.textContent = country.name;
    option.setAttribute('data-dial-code', country.dial_code);
    option.setAttribute('data-region-code', country.code);
    option.value = country.name;
    countryDropdown.appendChild(option);
});

countryDropdown.addEventListener('change', () => {
    const selectedCountry = countryDropdown.value;
});


const userJobContainer = document.getElementById('user-job-slider');
const userBookmarkData = JSON.parse('{{ bookmark_data|escapejs|safe }}')
console.log(userBookmarkData)

userBookmarkData.forEach(job => {
    const userJobWidget = document.createElement('div');
    userJobWidget.classList.add('user-job-widget');
    userJobWidget.setAttribute('data-jobid', job.jobid);
    userJobWidget.innerHTML = `
                <p>${job.date_scraped}</p>
                <p>${job.job_title}</p>
                <p>${job.job_types}</p>
                <p>${job.salary_range}</p>
                <button class="remove-user-bookmark" id="remove-user-bookmark" job_id="${job.jobid}">x</button?
            `;
    userJobContainer.appendChild(userJobWidget);
});

const userBookmarkRemoveButton = document.getElementById('remove-user-bookmark');
userBookmarkRemoveButton.addEventListener('click', () => {
    job_id = userBookmarkRemoveButton.getAttribute('job_id');

    const formData = new FormData();
    formData.append('job_id', job_id)

    fetch('/remove_bookmark/', {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': csrfToken,
        },
    })
        .then(response => response.json())
        .then(data => {
            if (data.Message) {
                showToast(data.Message);
                setTimeout(() => {
                    location.reload();
                }, 2000);
            } else {
                showToast(data.Message);
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
})


function phoneVerifyHandler() {
    const phoneInput = document.querySelector('input[name="new_phone"]');
    const newPhone = phoneInput.value.trim();

    const selectedCountryOption = countryDropdown.options[countryDropdown.selectedIndex];
    const dialCode = selectedCountryOption.getAttribute('data-dial-code');
    const regionCode = selectedCountryOption.getAttribute('data-region-code');

    if (newPhone === '') {
        showToast("Phone Number cannot be empty");
        return;
    }
    if (newPhone === '{{ user.phone_number }}') {
        showToast('Phone Number is same as the current one');
        return;
    }

    const csrfToken = '{{ csrf_token }}';
    const formData = new FormData();
    formData.append('new_phone', newPhone);
    formData.append('dial_code', dialCode);
    formData.append('region_code', regionCode);

    const loadingSpinner = document.getElementById('loading-spinner');
    loadingSpinner.style.display = 'block';
    overlay.style.display = 'none';

    fetch('/verify_phone/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken,
        },
        body: formData,
    })
        .then(response => {
            if (response.ok) {
                return response.json();
            } else {
                return response.json();
            }
        })
        .then(data => {
            loadingSpinner.style.display = 'none';
            overlay.style.display = 'none';

            if (data.success) {
                showToast(data.message);
                phone_otp_container.style.display = 'block';
                phone_otpVerifyButton.style.display = 'inline-block';

                if (!isResendOTPMode) {
                    phone_otpVerifyButton.textContent = 'Verify OTP';
                    phone_otpVerifyButton.addEventListener('click', phoneotpVerifyButtonHandler);
                    startPhoneOTPTimer();
                } else {
                    phone_otpVerifyButton.textContent = 'Resend OTP';
                    phone_otpVerifyButton.addEventListener('click', phoneVerifyHandler);
                    startPhoneOTPTimer();
                }
            } else {
                showToast(data.message);
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });

};

function phoneotpVerifyButtonHandler() {
    if (phone_otpVerifyButton.textContent === 'Resend OTP') {
        isResendOTPMode = true
        phoneVerifyHandler();
        phone_otpInput.value = '';
    } else {
        const otp = phone_otpInput.value.trim();

        if (otp === '') {
            showToast("Please enter the OTP");
            return;
        }
        const csrfToken = '{{ csrf_token }}';

        const formData = new FormData();
        formData.append('otp', otp);

        const newPhone = document.querySelector('input[name="new_phone"]').value.trim()

        fetch('/verify_phone_otp/', {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': csrfToken,
            },
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showToast('Phone Number Updated Successfully');

                    phone_otp_container.style.display = 'none';
                    phone_verifyButton.style.display = 'none';
                    countryDropdown.style.display = 'none';

                    phone_number.textContent = newPhone;
                } else {
                    showToast("Invalid OTP");
                }
            })
            .catch(error => {
                console.error('Error:', error);
            });
    }
}

phone_verifybutton.addEventListener('click', phoneVerifyHandler);
phone_otpVerifyButton.addEventListener('click', phoneotpVerifyButtonHandler);

});
