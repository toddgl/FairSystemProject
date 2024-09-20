/*  static/js/licence_batch.js */

document.addEventListener('DOMContentLoaded', function () {
    // Update iframe src in Food Licence Batch PDF modal
    var batchpdfModal = document.getElementById('batchpdfModal');
    batchpdfModal.addEventListener('show.bs.modal', function (event) {
        var button = event.relatedTarget; // Button that triggered the modal
        var batchPdfUrl = button.getAttribute('data-batch-pdf'); // Extract info from data-* attributes
        var iframe = document.getElementById('batchPdfIframe');
        iframe.src = batchPdfUrl; // Update iframe src
    });
});
// When the modal is shown, populate the hidden batch_id input
$('#foodlicencebatchModal').on('show.bs.modal', function (event) {
    var button = $(event.relatedTarget);  // Button that triggered the modal
    var batchId = button.data('batch-id');  // Extract batch ID from data-* attributes
    var modal = $(this);
    // Update the modal's hidden input with the batch ID
    modal.find('input[name="batch_id"]').val(batchId);
});
