function logout() {
    $.ajax({
        'url': '/logout',
        'type': 'GET',
        'success': function (data) {
            window.location.reload();
        }
    });
}


function deletePost(postId) {
    $.ajax({
        'url': '/deletePost',
        'type': 'POST',
        'data': {
            'id': postId
        },
        'success': function (data) {
            window.location.reload();
        }
    });
}