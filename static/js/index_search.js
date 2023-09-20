// index_search.js

const searchClient = algoliasearch('SF0IKHXEOM', 'd230e775381cdb00d71055ca68ce0a32');
const index = searchClient.initIndex('test_arXiv');
const searchInput = document.getElementById('search-input');
const searchButton = document.getElementById('search-button');
const resultsList = document.getElementById('results');

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

    // Perform a search
    index.search(query, {
        clickAnalytics: true
    })
        .then(({ hits, queryID: receivedQueryID }) => {
            console.log('Search results:', hits);
            console.log('QueryID:', receivedQueryID);

            // Set the queryID value from the response to the outer queryID variable
            queryID = receivedQueryID;

            displayResults(hits);
        })
        .catch(err => {
            console.error(err);
        });
}

// Function to display results
function displayResults(results) {
    resultsList.innerHTML = '';

    if (results.length === 0) {
        resultsList.innerHTML = '<li>No results found.</li>';
    } else {
        results.forEach(result => {
            const li = document.createElement('li');

            // Create a hyperlink for the result's title
            const link = document.createElement('a');
            link.href = `/detail/${result.objectID}`; // Link to the detail page with the objectID

            // Set the title as the link text
            link.textContent = result.title;

            // Attach a click event handler to the link
            const paperObjectID = result.objectID;
            link.addEventListener('click', () => {

                // Get the position of the clicked item
                const position = results.findIndex(resultItem => resultItem.objectID === result.objectID);

                // Send the "click_paper" event to Algolia Insights
                aa('clickedObjectIDsAfterSearch', {
                    index: 'test_arXiv',
                    eventName: 'click_paper',
                    queryID: queryID,
                    objectIDs: [paperObjectID],
                    positions: [position],
                });
            });

            // Append the hyperlink to the list item
            li.appendChild(link);

            // Append the list item to the results list
            resultsList.appendChild(li);
        });
    }
}
