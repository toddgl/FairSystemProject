/*  static/js/clear_iframe.js */

$("#zonePdfModal").on('data-bs-dismiss', function() {
    var iframe = document.getElementByTagName("iframe");
    iframedoc =iframe.contentDocument || iframe.contentWindow.document;
    iframedoc.body.innerHTML = '';
});