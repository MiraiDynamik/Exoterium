// detail_like.js

const likeButton = document.getElementById('likeButton');

const sub = "{{ session.userinfo.sub }}";
const hashedSub = CryptoJS.MD5(sub).toString();
console.log(hashedSub);

aa('setUserToken', hashedSub);

// Algolia Client: Initialize
aa('init', {
    appId: 'SF0IKHXEOM',
    apiKey: 'd230e775381cdb00d71055ca68ce0a32',
});

    // Add a click event listener to the "like" button
    likeButton.addEventListener('click', function() {


        // Define the object ID of the current paper (replace "# the obj id of current paper" with the actual object ID)
        const paperObjectID = $('p:contains("Arxiv ID:") + p').text();


        console.log(sub);
        console.log(paperObjectID);


        // Send the "like_paper" event to Algolia Insights
        aa('convertedObjectIDs', {
            index: 'test_arXiv',
            eventName: 'like_paper',
            objectIDs: [paperObjectID],
        });
        // Optionally, you can update the button label or style to indicate that the paper is liked.
        likeButton.innerText = 'Liked'; // Update the button label
        likeButton.disabled = true; // Disable the button to prevent multiple clicks
});
