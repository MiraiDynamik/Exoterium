// index_search.js
// used in index.html

const searchClient = algoliasearch('SF0IKHXEOM', 'd230e775381cdb00d71055ca68ce0a32');
const index = searchClient.initIndex('test_arXiv');
const searchInput = document.getElementById('search-input');
const searchButton = document.getElementById('search-button');
const resultsList = document.getElementById('results');
const recommendResults = document.getElementById('recommendResults');

let hashedSub = getSub();
console.log('hashedSub', hashedSub);
if (hashedSub !== '') {
    getRecommendResults()
}

aa('setUserToken', hashedSub);

// Algolia Client: Initialize
aa('init', {
    appId: 'SF0IKHXEOM',
    apiKey: 'd230e775381cdb00d71055ca68ce0a32',
});

// Event listener for the search button
searchButton.addEventListener('click', () => {
    performSearch();
});

// Event listener for Enter key press
searchInput.addEventListener('keydown', event => {
    if (event.key === 'Enter') {
        performSearch();
    }
});

let queryID = null;


// Function to perform the search
function performSearch() {
    const query = searchInput.value;
    if (query) {
        // Perform a search
        index.search(query, {
            clickAnalytics: true
        })
            .then(({hits, query_id: receivedQueryID}) => {
                console.log('Search results:', hits);
                console.log('QueryID:', receivedQueryID);

                // Set the queryID value from the response to the outer queryID variable
                queryID = receivedQueryID;
                console.log(hits)
                displayResults(hits);
            })
            .catch(err => {
                console.error(err);
            });
    }
}


// Function to create a list item with a hyperlink
function createListItem(result, queryID) {
    const li = document.createElement('li');

    // Create a hyperlink for the result's title
    const link = document.createElement('a');

    if (queryID) {
        // Link to the detail page with the objectID and add the queryID as a URL parameter
        link.href = `/detail/${result.objectID}?queryID=${queryID}`;
    } else {
        link.href = `/detail/${result.objectID}`;
    }

    // Set the title as the link text
    link.textContent = result.title;

    // Return the list item with the hyperlink
    return { li, link };
}


// Function to handle the click event and send the event to Algolia Insights
function handleLinkClick(result, queryID, results) {
    return () => {

        // Get the position of the clicked item
        const position = results.findIndex(resultItem => resultItem.objectID === result.objectID) + 1;

        // Send the "click_paper" event to Algolia Insights
        if (queryID) {
            aa('clickedObjectIDsAfterSearch', {
                index: 'test_arXiv',
                eventName: 'click_paper',
                queryID: queryID,
                objectIDs: [result.objectID],
                positions: [position],
            });
        } else {
            aa('clickedObjectIDsAfterSearch', {
                index: 'test_arXiv',
                eventName: 'click_paper',
                objectIDs: [result.objectID],
            });
        }
    };
}


// Function to display results
function displayResults(results) {
    resultsList.innerHTML = '';

    if (results.length === 0) {
        resultsList.innerHTML = '<li>No results found.</li>';
    } else {
        results.forEach(result => {
            const { li, link } = createListItem(result, queryID);

            // Attach a click event handler to the link
            link.addEventListener('click', handleLinkClick(result, queryID, results));

            // Append the hyperlink to the list item
            li.appendChild(link);

            // Append the list item to the results list
            resultsList.appendChild(li);
        });
    }
}


// Function to get hashed userID
function getSub() {
    const url = 'http://localhost:3000/sub'
    let hashSub
    $.ajax({
        url: url,
        async: false,
        success: function (res) {
            hashSub = res
        }
    })
    return hashSub
}


function getRecommendResults() {
    const url = 'http://localhost:3000/recommend?userID=' + hashedSub
    let recommendData
    $.ajax({
        url: url,
        async: false,
        success: function (res) {
            recommendData = res
        }
    })
    displayRecommendResults(recommendData)
}

function displayRecommendResults(results) {
    recommendResults.innerHTML = '';

    if (results.length === 0) {
        recommendResults.innerHTML = '<li>No results found.</li>';
    } else {
        console.log(results)
        results.forEach(result => {
            const { li, link } = createListItem(result, null);

            // Attach a click event handler to the link
            link.addEventListener('click', handleLinkClick(result, null, results));

            // Append the hyperlink to the list item
            li.appendChild(link);

            // Append the list item to the results list
            recommendResults.appendChild(li);
        });
    }
}
