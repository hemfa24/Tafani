var upload_submission_id=0;
$('.assignment_btn').click(function()
    {
    var submission_id = $(this).attr('data-id');
    $.ajax({
        url: "/action_redirect_download_assessment/" + submission_id,
        type: 'GET',
        success: function(data) {
            data = JSON.parse(data)
            if (data['error'])
                alert(data['message']);
            else {
                window.open('/action_redirect_download_assessment/' + submission_id + '/1/' + data['name'], '_self', 'noopener');
            }
        },
        error: function (error) {
            alert(error.status +  " , " + error.statusText);
        }
    });

    });
    $('.solution_btn').click(function(){
    var submission_id = $(this).attr('data-id');
    $.ajax({
        url: "/action_redirect_download_solution/" + submission_id,
        type: 'GET',
        success: function(data) {
            data = JSON.parse(data)
            if (data['error'])
                alert(data['message']);
            else {
                window.open('/action_redirect_download_solution/' + submission_id + '/1/' + data['name'], '_self', 'noopener');
            }
        },
        error: function (error) {
            alert(error.status +  " , " + error.statusText);
        }
    });
    });
    $('.download_btn').click(function(){
    var submission_id = $(this).attr('data-id');
    $.ajax({
        url: "/action_redirect_download_uploaded/" + submission_id,
        type: 'GET',
        success: function(data) {
            data = JSON.parse(data)
            if (data['error'])
                alert(data['message']);
            else {
                window.open('/action_redirect_download_uploaded/' + submission_id + '/1/' + data['name'], '_self', 'noopener');
            }
        },
        error: function (error) {
            alert(error.status +  " , " + error.statusText);
        }
    });
    });
    $('#actual-btn').on('change', function () {
    const fileName = $(this).prop('files')[0].name;
    var fileInput = document.getElementById('actual-btn');
    var file = fileInput.files[0];
    var submission_id = upload_submission_id;
    console.log('submission_id', submission_id);

    if (file) {
        if (file.type === 'application/pdf' || file.type === 'application/zip') {
            var formData = new FormData();
            formData.append('file', file);
            formData.append('submission_id', submission_id);

            $.ajax({
                url: '/store_assignment_file',
                type: 'POST',
                data: formData,
                processData: false,
                contentType: false,
                success: function (data) {
                     location.reload();
                },
                error: function (error) {
                    console.log('Error:', error);
                }
            });
        } else {
        Swal.fire({
                icon: 'error',
                title: 'Error',
                text: 'Error: Invalid file type. Allowed types are ZIP and PDF.'
            });
        }
    }
});

$('.upload_btn3').on('click', function() {
            var submission_id = $(this).attr('data-id');
            upload_submission_id = submission_id;
        });


    $('.btn_delete2').click(function(){
    var formData = new FormData();
    var submission_id = $(this).attr('data-id');
    formData.append('submission_id', submission_id);
        $.ajax({
        url: '/delete_assignment_file',
        type: 'POST',
        data: formData,
        processData: false,
        contentType: false,
        success: function (data) {
            location.reload();
        },
        error: function (error) {
            console.log('Error:', error);
        }
    });
    });