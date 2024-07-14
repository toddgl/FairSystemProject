/*  static/js/licence_batch.js */

document.addEventListener('DOMContentLoaded', function () {
    // Update form action in Food Licence Batch Update modal
    var foodlicencebatchModal = document.getElementById('foodlicencebatchModal');
    foodlicencebatchModal.addEventListener('show.bs.modal', function (event) {
        var button = event.relatedTarget; // Button that triggered the modal
        var batchId = button.getAttribute('data-batch-id'); // Extract info from data-* attributes
        var form = foodlicencebatchModal.querySelector('#updateForm');
        form.action = "{% url 'foodlicence:licence-batch-update' '' %}".slice(0, -1) + batchId; // Update form action
    });
    // Update iframe src in Food Licence Batch PDF modal
    var batchpdfModal = document.getElementById('batchpdfModal');
    batchpdfModal.addEventListener('show.bs.modal', function (event) {
        var button = event.relatedTarget; // Button that triggered the modal
        var batchPdfUrl = button.getAttribute('data-batch-pdf'); // Extract info from data-* attributes
        var iframe = document.getElementById('batchPdfIframe');
        iframe.src = batchPdfUrl; // Update iframe src
    });
});
