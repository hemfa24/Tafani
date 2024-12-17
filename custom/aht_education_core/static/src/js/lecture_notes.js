
//    $('[data-toggle="minimize"]').on("click", function() {
//      if ((body.hasClass('sidebar-toggle-display')) || (body.hasClass('sidebar-absolute'))) {
//        body.toggleClass('sidebar-hidden');
//      } else {
//        body.toggleClass('sidebar-icon-only');
//      }
//    });
function download_attachments(ev, attachment_id){
    console.log("lecture_id: ", attachment_id);
    if (attachment_id) {
        var downloadUrl = '/custom/download_attachment/' + attachment_id;
        window.location.href = downloadUrl;
        }
}
$('#courses').on('change', function() {
            var selectedCourseId = $(this).find(':selected').data('id');

             $.ajax({
                type: "GET",
                dataType: 'json',
                url: "/getCourseContent/" + selectedCourseId,
                success: function(data) {
                $('#course-table-body').html('');
                if (data['error'])
                    alert(data['message']);
                else {
                    $.each(data['courses'], function (index, item) {
                        var newRow = $('<tr>');
                        newRow.append('<td>' + item.sno + '</td>');
                        newRow.append('<td>' + item.title + '</td>');
                        newRow.append('<td>' + item.uploaded_by + '</td>');
                        newRow.append('<td>' + item.document_type + '</td>');
                        // Create a "Download" button for each row with data attributes
                        var downloadButton = $('<button type="button" class="mb-2 mr-2 btn btn-primary btnDownload">Download</button>');
                        downloadButton.attr('data-attachment_id', item.attachment_id);
                        downloadButton.attr('onclick', 'download_attachments(this,' + item.attachment_id + ')');
                        newRow.append('<td>').find('td:last').append(downloadButton);
                        $('#course-table-body').append(newRow);
                    });
                }
                },
                error: function(error) {
                    console.error("Error:", error);
                }
            });

        });