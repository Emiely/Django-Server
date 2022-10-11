var updateBtns = document.getElementsByClassName('update-cart')

for (let i = 0; i < updateBtns.length; i++)
{
    updateBtns[i].addEventListener('click',
    function()
    {
        var productID = this.dataset.product // this = self in python. Which means, It represents the button that is clicked on.
        var action    = this.dataset.action 
        console.log('productID', productID, 'action', action)
        // Check if the Customer is Logged-in or Not.
        console.log('USER', user)
        if (user == 'AnonymousUser')
        {
            console.log("User is Not authenticated.")
        }
        else
        {
            update_user_order(productID, action)
        }
    }
    )
}

function update_user_order(productId, action)
{
    console.log("User is authenticated, Sending data...")
    // When you want to make the URL is directly after the Domain name as the first in the path;
    // => Just put the pre-slash in that URL, It won't be a complement of a path; It'll be a whole different path.
    var url = '/update_item/'
    // Create and Use `fetch` api. (fetch call) - Send POST data to our the Back-End (to the View-Function)
    fetch (url, {
        method  : 'POST',
        headers : {
            'Content-Type' : 'application/json',
            'X-CSRFToken'  : csrftoken
        },
        body    : JSON.stringify({'productId' : productId, 'action' : action})
    })
    // Once we send the data we need to return a Promise.
    .then((response) => { // Convert the response to json value.
        return response.json()
    })
    // Just console the Returned Data (That are in the View function JsonResponse) For Testing Purposes.
    .then((data) => {
        console.log('Data:', data)
        location.reload()
    })
}