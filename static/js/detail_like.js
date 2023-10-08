// detail_like.js
// used in detail.html

const likeButton = document.getElementById('fullPassage');

let hashedSub = getSub();
console.log('hashedSub', hashedSub);

aa('setUserToken', hashedSub);

// Algolia Client: Initialize
aa('init', {
    appId: 'SF0IKHXEOM',
    apiKey: 'd230e775381cdb00d71055ca68ce0a32',
});


// Get the queryID from the URL
const queryID = getUrlParameter('queryID');


    // Add a click event listener to the "like" button
likeButton.addEventListener('click', function() {

    // Define the object ID of the current paper (replace "# the obj id of current paper" with the actual object ID)
    const paperObjectID = $('p:contains("Arxiv ID:") + p').text();

    console.log(paperObjectID);

    // Send the "like_paper" event to Algolia Insights
    if (queryID) {
        aa('convertedObjectIDsAfterSearch', {
            index: 'test_arXiv',
            eventName: 'like_paper',
            objectIDs: [paperObjectID],
            queryID: queryID,
        });
    } else {
        aa('convertedObjectIDs', {
            index: 'test_arXiv',
            eventName: 'like_paper',
            objectIDs: [paperObjectID],
        })
    }

    // Send the "like_paper" event to Back
    const url = 'http://localhost:3000/detail/' + paperObjectID + '/like'
    $.get(url, function (res) {
          console.log(res)
    })
});


// Function to extract URL parameters
function getUrlParameter(name) {
    name = name.replace(/[\[]/, '\\[').replace(/[\]]/, '\\]');
    var regex = new RegExp('[\\?&]' + name + '=([^&#]*)');
    var results = regex.exec(location.search);
    return results === null ? '' : decodeURIComponent(results[1].replace(/\+/g, ' '));
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
