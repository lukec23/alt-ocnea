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

function updatePost(postId) {
    console.log(postId);
    content = document.getElementById("post" + postId).getElementsByTagName("textarea")[0].value;
    $.ajax({
        'url': '/updatePost',
        'type': 'POST',
        'data': {
            'id': postId,
            'content': content
        },
        'success': function (data) {
            window.location.reload();
        }
    });
}
