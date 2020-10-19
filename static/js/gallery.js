const doc = document;
doc.addEventListener('DOMContentLoaded', function () {
    const update_button = doc.getElementsByClassName('update-cart')

    for (i = 0; i < update_button.length; i++) {
        update_button[i].addEventListener('click', function () {
            const handicraft_id = this.dataset.handicraft
            const action = this.dataset.action
            console.log('handicraft_id:', handicraft_id, 'action:', action)

            console.log('USER:', user)
            updateUserOrder(handicraft_id, action)
        })
    }

    function updateUserOrder(handicraft_id, action) {
        console.log('added product to list')

        const url = '/add_art/'

        fetch('/add_art/', {
            method: 'POST',
            headers:{
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken,
            },
            body: JSON.stringify({'handicraft_id': handicraft_id, 'action': action})
        }).then((response) => {
            return response.json()
        }).then((data) => {
            location.reload()
        });
    }
});