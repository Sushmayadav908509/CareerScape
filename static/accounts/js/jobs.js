document.addEventListener("DOMContentLoaded", function () {
    
    const widgetContainer = document.getElementById("widgetContainer");
    const parentTemplate = widgetContainer.querySelector('.parent');
    const sortDropdown = document.getElementById('sort-by');
    const notification = document.getElementById('notification');
    const notificationMessage = document.getElementById('notificationMessage');
    const searchButton = document.querySelector('.search-button');
    const searchInput = document.getElementById('search');
    const backButton = document.getElementById('backButton');
    const nextButton = document.getElementById('nextButton');
    const jobDescriptionText = document.getElementById('jobDescriptionText');
    const jobDescriptionInfo = document.getElementById('jobDescriptionInfo');

    const overlay = document.getElementById('overlay');

    let pageNumber = 1;
    let offset = 0;


    function showToast(message) {
        var toast = document.getElementById("toastNotification");
        var toastMessage = document.getElementById("toastMessage");
        toastMessage.innerText = message;
        toast.classList.add("show");
        setTimeout(function () {
            toast.classList.remove("show");
        }, 3000);
    }

    function getTodayDate() {
        const today = new Date();
        const year = today.getFullYear();
        const month = String(today.getMonth() + 1).padStart(2, '0');
        const day = String(today.getDate()).padStart(2, '0');
        return `${year}-${month}-${day}`;
    }


    function updatePageNumber(newPageNumber) {
        document.getElementById('page-number').textContent = `${newPageNumber}`;
        pageNumber = newPageNumber;
    }

    function goBack() {
        if (offset > 0) {
            offset -= 12;
            fetchData(sortDropdown.value, offset, searchInput.value.trim());
            scrollToTop();
        }
    }

    function goNext() {
        offset += 12;
        fetchData(sortDropdown.value, offset, searchInput.value.trim());
        scrollToTop();
    }

    function scrollToTop() {
        window.scrollTo(0, 0);
    }

    const jobDescriptionDisplay = document.getElementById('jobDescriptionDisplay');
    function closeJobDescription() {
        jobDescriptionDisplay.style.display = 'none';
        overlay.style.display = 'none';
    }

    overlay.addEventListener('click', () => {
        if (overlay.style.display = 'block') {
            jobDescriptionDisplay.style.display = 'none';
            overlay.style.display = 'none';
        }
    })


    searchButton.addEventListener('click', () => {
        offset = 0;
        sortDropdown.value = 'newest'
        fetchData(sortDropdown.value, offset, searchInput.value.trim());
    });


    function fetchData(sortOption, offset, searchQuery = '') {
        const urlParams = new URLSearchParams(window.location.search);

        // let currentOffset = parseInt(urlParams.get('offset')) || 0;

        if (searchQuery) {
            urlParams.set('search', searchQuery);
        } else {
            urlParams.delete('search');
        }

        if (sortOption && sortOption !== 'Sort-By') {
            urlParams.set('sort', sortOption);
        } else {
            urlParams.delete('sort');
        }

        urlParams.set('offset', offset);

        const url = `${window.location.pathname}?${urlParams.toString()}`;
        console.log('fetching data from url:', url);

        fetch(url, {
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
            .then(response => {
                if (response.ok) {
                    console.log('Response status:', response.status);
                    return response.json();
                } else {
                    throw new Error('API request failed');
                }
            })
            .then(data => {
                console.log('Received data:', data);

                if (data.results.length === 0) {
                    showToast("No Jobs Found");
                } else {
                    const stateObject = { data: data };
                    const title = "Your Page Title";
                    history.pushState(stateObject, title, url);
                    populateData(data);
                }
            })
            .catch(error => {
                console.error('API request failed:', error);
            });
    }

    sortDropdown.addEventListener('change', (event) => {
        const selectedOption = event.target.value;
        if (selectedOption === 'today' || selectedOption === 'newest' || selectedOption === 'oldest') {
            offset = 0;
            fetchData(selectedOption, offset, searchInput.value.trim());
        }
    });


    const jsonData = document.getElementById("data").textContent;
    let data = JSON.parse(jsonData);
    console.log(data);

    const bookmarkedJobsElement = document.getElementById("bookmarked_jobs");
    const bookmarkedJobsData = JSON.parse(bookmarkedJobsElement.textContent);


    function populateData(data) {
        widgetContainer.innerHTML = '';

        data.results.forEach(item => {
            const cardClone = parentTemplate.cloneNode(true);
            cardClone.style.display = 'block';
            cardClone.querySelector('.job-title').textContent = item.job_title;
            cardClone.querySelector('#company_name').textContent = item.company_name;
            cardClone.querySelector('#company_location').textContent = item.company_location;
            cardClone.querySelector('#job_types').textContent = item.job_types;

            const bookmarkButton = cardClone.querySelector('#bookmark-button');
            bookmarkButton.setAttribute('data-job-id', item.jobid);
            const isBookmarked = bookmarkedJobsData.includes(item.jobid);

            if (isBookmarked) {
                bookmarkButton.classList.remove('fa-regular');
                bookmarkButton.classList.add('fa-solid');
            }

            const salaryRange = item.salary_range;
            const salaryUnit = item.salary_unit;

            if (salaryRange !== "None - None") {
                const [minSalary, maxSalary] = salaryRange.split(" - ");
                if (minSalary === "None" && maxSalary === "None") {
                    cardClone.querySelector('#salary').style.display = 'none';
                } else if (minSalary === "None" || minSalary === "-1") {
                    cardClone.querySelector('#salary').textContent = maxSalary;
                } else if (maxSalary === "None" || maxSalary === "-1") {
                    cardClone.querySelector('#salary').textContent = minSalary;
                } else {
                    cardClone.querySelector('#salary').textContent = `${salaryRange} / ${salaryUnit}`;
                }
            } else {
                cardClone.querySelector('#salary').style.display = 'none';
            }

            const dateScraped = new Date(item.date_scraped);
            const month = dateScraped.toLocaleString('default', { month: 'short' });
            const date = dateScraped.getDate();

            cardClone.querySelector('.month').textContent = month;
            cardClone.querySelector('.date').textContent = date;

            const seeMoreButton = cardClone.querySelector('.see-more');
            seeMoreButton.addEventListener('click', () => {
                jobDescriptionInfo.innerHTML = `
                    <p class="desc-date">${item.date_scraped}</p>
                    <p class="desc-job-title">${item.job_title}</p>
                    <p>${item.company_name}</p>
                    <p>${item.company_location}</p>
                    <p>${item.salary_range} / ${item.salary_unit}</p>
                    <p>${item.job_types}</p>
                    <p class="desc-desc-title">Job Description:</p>
                    <p>${item.job_description}</p>
                    <button class="desc-apply" onclick="window.open('${item.url}', '_blank')">Apply Now</button>
                `
                overlay.style.display = 'block';
                jobDescriptionDisplay.style.display = 'block';
            });

            const applyNowButton = cardClone.querySelector('.apply-now');
            applyNowButton.addEventListener('click', () => {
                window.open(item.url, '_blank');
            });

            const newPageNumber = Math.ceil((offset + 1) / 10);
            updatePageNumber(newPageNumber);

            widgetContainer.appendChild(cardClone);

        });
    }
    populateData(data);


    widgetContainer.addEventListener('click', function (event) {
        if (event.target.id === 'bookmark-button') {
            const bookmarkButton = event.target;
            const bookmark_jobid = bookmarkButton.getAttribute('data-job-id');
            console.log(bookmark_jobid);
            document.getElementById('bookmarkJobIdInput').value = bookmark_jobid;

            fetch('/bookmark/', {
                method: 'POST',
                body: new FormData(document.getElementById('bookmarkForm')),
            })
                .then(response => response.json())
                .then(data => {
                    if (data.Message === "Bookmark added successfully") {
                        showToast(data.Message);
                        bookmarkButton.classList.remove('fa-regular');
                        bookmarkButton.classList.add('fa-solid');
                    } else {
                        showToast(data.Message);
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                });
        }
    });

    widgetContainer.addEventListener('click', function (event) {
        if (event.target.id === 'bookmark-button' && event.target.classList.contains('fa-solid')) {
            const bookmarkButton = event.target;
            const bookmark_jobid = bookmarkButton.getAttribute('data-job-id');
            console.log(bookmark_jobid);
            document.getElementById('bookmarkJobIdInput').value = bookmark_jobid;

            fetch('/remove_bookmark/', {
                method: 'POST',
                body: new FormData(document.getElementById('bookmarkForm')),
            })
                .then(response => response.json())
                .then(data => {
                    if (data.Message) {
                        showToast(data.Message);
                        bookmarkButton.classList.remove('fa-solid');
                        bookmarkButton.classList.add('fa-regular');
                    } else {
                        showToast(data.Message);
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                });
        }
    });
    const closeDescriptionButton = document.getElementById('closeDescription');
    closeDescriptionButton.addEventListener('click', closeJobDescription);

    backButton.addEventListener('click', goBack);

    nextButton.addEventListener('click', goNext);

});
